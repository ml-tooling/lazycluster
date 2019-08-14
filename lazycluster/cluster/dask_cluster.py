"""Module for conveniently managing a DASK cluster. http://distributed.dask.org """

from distributed import Client
import time
from typing import List, Union, Optional

from subprocess import Popen

from lazycluster import RuntimeTask, Runtime, RuntimeGroup, localhost_has_free_port
from lazycluster.cluster import MasterWorkerCluster, MasterLauncher, WorkerLauncher
from lazycluster import _utils
from lazycluster.cluster.exceptions import MasterStartError
from lazycluster.exceptions import PortInUseError


class LocalMasterLauncher(MasterLauncher):
    """Concrete implementation of the `MasterLauncher` interface.

    This class implements the logic for starting a the DASK master instance (i.e. scheduler in DASK terms) on localhost.
    """

    def start(self, ports: Union[List[int], int], timeout: int = 3) -> List[int]:
        """Launch a master instance.

        Args:
            ports (Union[List[int], int]): Port where the master should be started. If a list is given then the
                                                 first port that is free in the `RuntimeGroup` will be used. The actual
                                                 chosen port can requested via the property `port`.
            timeout (int): Timeout (s) after which an MasterStartError is raised if master instance not started yet.

        Returns:
            List[int]: In case a port list was given the updated port list will be returned. Otherwise an empty list.

        Raises:
            PortInUseError: If a single port is given and it is not free in the `RuntimeGroup`.
            NoPortsLeftError: If a port list was given and none of the ports is actually free in the `RuntimeGroup`.
            MasterStartError: If master was not started after the specified `timeout`.
        """

        if not isinstance(ports, list):
            if localhost_has_free_port(ports) and self._group.has_free_port(ports, exclude_hosts=Runtime.LOCALHOST):
                master_port = ports
            else:
                raise PortInUseError(ports, self._group)

        else:
            master_port = self._group.get_free_port(ports)  # Raises NoPortsLeftError
            ports = _utils.get_remaining_ports(ports, master_port)

        self._process = Popen(['dask-scheduler', '--port', str(master_port)])

        time.sleep(timeout)  # Needed for being able to check the port

        if not localhost_has_free_port(master_port):
            self._port = master_port
            print('Dask scheduler started on localhost on port ' + str(self._port))
        else:
            raise MasterStartError('localhost', self._port)

        # Sets up ssh tunnel for scheduler such that all communication is routed over the
        # local machine and all entities can talk to each the scheduler on localhost.
        self._group.expose_port_to_runtimes(self._port)

        return ports


class RoundRobinLauncher(WorkerLauncher):
    """WorkerLauncher implementation for launching DASK workers in a round robin manner. """

    def __init__(self, runtime_group: RuntimeGroup):
        """Initialization method.

        Args:
            runtime_group (RuntimeGroup): The group where the workers will be started.
        """
        super().__init__(runtime_group)
        self._ports = None

    def start(self, worker_count: int, master_port: int, ports: List[int]) -> List[int]:
        """Launches the worker instances in the `RuntimeGroup`.

        Args:
            worker_count (int): The number of worker instances to be started in the group.
            master_port (int):  The port of the master instance.
            ports (List[int]): The ports to be used for starting the workers. Only ports from the list will be chosen
                               that are actually free.
        Returns:
            List[int]: The updated port list after starting the workers, i.e. the used ones were removed.

        Raises:
            NoPortsLeftError: If there are not enough free ports for starting all workers.
        """
        self._ports = ports
        hosts = self._group.hosts
        runtimes = self._group.runtimes

        # Launch each desired worker one by one
        for worker_index in range(worker_count):

            # Determine the runtime where the next worker will be started in
            runtime_index = (self._group.runtime_count + worker_index) % self._group.runtime_count
            # Get the actual host corresponding to the index
            host = hosts[runtime_index]
            root_dir = runtimes[runtime_index].root_directory
            assert host == runtimes[runtime_index].host

            worker_port = self._launch_single_worker(host, worker_index, master_port, root_dir)  # NoPortsLeftError
            # Remember which worker ports are now used per `Runtime`
            if host in self._ports_per_host:
                self._ports_per_host[host].append(worker_port)
            else:
                self._ports_per_host.update({host: [worker_port]})

        # Needed for worker communication between workers, which is necessary in case of DASK
        self.setup_worker_ssh_tunnels()

        return self._ports

    def _launch_single_worker(self, host: str, worker_index: int, master_port: int, root_directory: str):
        """Launch a single worker instance in a `Runtime` in the `RuntimeGroup`.

        Raises:
            NoPortsLeftError
        """
        # 1. Get a free port based on the port list
        worker_port = self._group.get_free_port(self._ports)  # Raises NoPortsLeftError
        self._ports = _utils.get_remaining_ports(self._ports, worker_port)
        # 2. Start the worker on this port
        task = RuntimeTask('launch-dask-worker-' + str(worker_index))
        task.run_command(DaskCluster.PIP_INSTALL_COMMAND)
        task.run_command(self._get_launch_command(master_port, worker_port, root_directory))
        self._group.execute_task(task, host)
        return worker_port

    @classmethod
    def _get_launch_command(cls, master_port: int, worker_port: int, root_directory: str) -> str:
        """Get the shell command for starting a worker instance.

        Returns:
             str: The launch command.
        """
        return 'dask-worker --worker-port=' + str(worker_port) + ' --local-directory=' + root_directory \
               + ' localhost:' + str(master_port)


class DaskCluster(MasterWorkerCluster):
    """Convenient class for launching a Dask cluster in a `RuntimeGroup`. 

    Examples:
        Create a DASK cluster with all `Runtimes` detected by the `RuntimeManager`. Each `Runtime` will host one DASK
        worker and the DASK master (i.e. scheduler) will be started on localhost as implemented in
        `LocalMasterLauncher`.
        >>> from lazycluster import RuntimeManager
        >>> cluster = DaskCluster(RuntimeManager().create_group())
        >>> cluster.start()

        Use different strategies for launching the master and the worker instance by providing custom implementation of
        `MasterLauncher` and `WorkerLauncher`.
        >>> cluster = DaskCluster(RuntimeManager().create_group(),
        ...                       MyMasterLauncherImpl(),
        ...                       MyWorkerLauncherImpl)
        >>> cluster.start()
    """

    DEFAULT_MASTER_PORT = 8786
    PIP_INSTALL_COMMAND = 'pip install -q "dask[complete]"'

    def __init__(self, runtime_group: RuntimeGroup, ports: Optional[List[int]] = None,
                 master_launcher: Optional[MasterLauncher] = None,
                 worker_launcher: Optional[WorkerLauncher] = None):
        """Initialization method.

        Args:
            runtime_group (RuntimeGroup): The `RuntimeGroup` contains all `Runtimes` which can be used for starting the
                                          DASK entities.
            ports (Optional[List[int]]: The list of ports which will be used to instantiate a cluster. Defaults to
                                        list(range(self.DEFAULT_PORT_RANGE_START,
                                                   self.DEFAULT_PORT_RANGE_END)).
            master_launcher (Optional[MasterLauncher]): Optionally, an instance implementing the `MasterLauncher`
                                                        interface can be given, which implements the strategy for
                                                        launching the master instances in the cluster. If None, then
                                                        `LocalMasterLauncher` is used.
            worker_launcher (Optional[WorkerLauncher]): Optionally, an instance implementing the `WorkerLauncher`
                                                        interface can be given, which implements the strategy for
                                                        launching the worker instances. If None, then
                                                        `RoundRobinLauncher` is used.
        """
        super().__init__(runtime_group, ports)

        self._master_launcher = master_launcher if master_launcher else LocalMasterLauncher(runtime_group)
        self._worker_launcher = worker_launcher if worker_launcher else RoundRobinLauncher(runtime_group)

    def get_client(self, timeout: int = 2) -> Client:
        """Get a connected Dask client. 
        
        Args:
            timeout (int): The timeout (s) value passed on to the Dask `Client` constructor. Defaults to 2.

        Raises:
            TimeoutError: If client connection `timeout` expires.
        """
        return Client('localhost:' + str(self.master_port), timeout=timeout)  # Raises TimeoutError
