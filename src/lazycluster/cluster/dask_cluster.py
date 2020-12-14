"""Module for conveniently managing a [DASK](http://distributed.dask.org) cluster."""

import time
from subprocess import Popen
from typing import List, Optional, Union

from distributed import Client

from lazycluster import Runtime, RuntimeGroup, RuntimeTask, _utils
from lazycluster.cluster import MasterLauncher, MasterWorkerCluster, WorkerLauncher
from lazycluster.cluster.exceptions import MasterStartError
from lazycluster.exceptions import NoPortsLeftError, PortInUseError


class LocalMasterLauncher(MasterLauncher):
    """Concrete implementation of the `MasterLauncher` interface. See its documentation to get a list of the inherited methods and attributes.

    This class implements the logic for starting a the DASK master instance (i.e. scheduler in DASK terms) on localhost.
    """

    def start(
        self, ports: Union[List[int], int], timeout: int = 3, debug: bool = False
    ) -> List[int]:
        """Launch a master instance.

        Note:
            If you create a custom subclass of MasterLauncher which will not start the master instance on localhost
            then you should pass the debug flag on to `execute_task()` of the `RuntimeGroup` or `Runtime` so that you
            can benefit from the debug feature of `RuntimeTask.execute()`.

        Args:
            ports: Port where the master should be started. If a list is given then the first port that is free in the
                   `RuntimeGroup` will be used. The actual chosen port can be requested via the property `port`.
            timeout: Timeout (s) after which an MasterStartError is raised if master instance not started yet.
            debug: If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then
                   the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to
                   `False`.

        Returns:
            List[int]: In case a port list was given the updated port list will be returned. Otherwise an empty list.

        Raises:
            PortInUseError: If a single port is given and it is not free in the `RuntimeGroup`.
            NoPortsLeftError: If a port list was given and none of the ports is actually free in the `RuntimeGroup`.
            MasterStartError: If master was not started after the specified `timeout`.
        """

        _ports: Union[List[int], int] = (
            ports.copy() if isinstance(ports, list) else ports
        )

        if debug:
            self.log.debug("The debug flag has no effect in LocalMasterLauncher.")

        if not isinstance(_ports, list):
            if _utils.localhost_has_free_port(_ports) and self._group.has_free_port(
                _ports, exclude_hosts=Runtime.LOCALHOST
            ):
                master_port = _ports
            else:
                raise PortInUseError(_ports, self._group)

        else:
            master_port = self._group.get_free_port(_ports)  # Raises NoPortsLeftError
            _ports = _utils.get_remaining_ports(_ports, master_port)

        self._process = Popen(["dask-scheduler", "--port", str(master_port)])

        time.sleep(timeout)  # Needed for being able to check the port

        if not _utils.localhost_has_free_port(master_port):
            self._port = master_port
            self.log.info(
                "Dask scheduler started on localhost on port " + str(self._port)
            )
        else:
            self.log.debug(
                "Dask scheduler could NOT be started successfully on port "
                + str(self._port)
            )
            cause = f"The master port {master_port} is still free when checking after the timeout of {timeout} seconds."
            raise MasterStartError("localhost", master_port, cause)

        # Sets up ssh tunnel for scheduler such that all communication is routed over the
        # local machine and all entities can talk to each the scheduler on localhost.
        self.log.debug("Expose the Dask scheduler port in the RuntimeGroup.")
        self._group.expose_port_to_runtimes(self._port)

        # Return an empty list if a single port was provided
        return _ports if isinstance(_ports, list) else []

    def cleanup(self) -> None:
        """Release all resources."""
        self.log.info("Cleanup the LocalMasterLauncher ...")
        super().cleanup()


class RoundRobinLauncher(WorkerLauncher):
    """WorkerLauncher implementation for launching DASK workers in a round robin manner. See its documentation to get a list of the inherited methods and attributes."""

    def __init__(self, runtime_group: RuntimeGroup):
        """Initialization method.

        Args:
            runtime_group: The group where the workers will be started.
        """
        super().__init__(runtime_group)
        self._ports: Optional[List[int]] = None

        self.log.debug("RoundRobinLauncher initialized.")

    def start(
        self, worker_count: int, master_port: int, ports: List[int], debug: bool = False
    ) -> List[int]:
        """Launches the worker instances in the `RuntimeGroup`.

        Args:
            worker_count: The number of worker instances to be started in the group.
            master_port:  The port of the master instance.
            ports: The ports to be used for starting the workers. Only ports from the list will be chosen
                               that are actually free.
            debug: If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then
                   the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to
                   `False`.

        Returns:
            List[int]: The updated port list after starting the workers, i.e. the used ones were removed.

        Raises:
            NoPortsLeftError: If there are not enough free ports for starting all workers.
        """
        self._ports = ports.copy()
        hosts = self._group.hosts
        runtimes = self._group.runtimes

        # Launch each desired worker one by one
        for worker_index in range(worker_count):
            # Determine the runtime where the next worker will be started in
            runtime_index = (
                self._group.runtime_count + worker_index
            ) % self._group.runtime_count
            # Get the actual host corresponding to the index
            host = hosts[runtime_index]
            working_dir = runtimes[runtime_index].working_dir
            assert host == runtimes[runtime_index].host

            self.log.debug(
                f"Launch Dask worker with index {worker_index} on Runtime {host}"
            )

            worker_port = self._launch_single_worker(
                host, worker_index, master_port, working_dir, debug
            )  # NoPortsLeftError
            # Remember which worker ports are now used per `Runtime`
            if host in self._ports_per_host:
                self._ports_per_host[host].append(worker_port)
            else:
                self._ports_per_host.update({host: [worker_port]})

        # Needed for worker communication between workers, which is necessary in case of DASK
        self.setup_worker_ssh_tunnels()

        return self._ports

    def _launch_single_worker(
        self,
        host: str,
        worker_index: int,
        master_port: int,
        working_dir: str,
        debug: bool,
    ) -> int:
        """Launch a single worker instance in a `Runtime` in the `RuntimeGroup`.

        Raises:
            NoPortsLeftError
        """
        if not self._ports:
            raise NoPortsLeftError()
        # 1. Get a free port based on the port list
        worker_port = self._group.get_free_port(self._ports)  # Raises NoPortsLeftError
        if self._ports:
            self._ports = _utils.get_remaining_ports(self._ports, worker_port)
        # 2. Start the worker on this port
        task = RuntimeTask("launch-dask-worker-" + str(worker_index))
        task.run_command(DaskCluster.PIP_INSTALL_COMMAND)
        task.run_command(
            self._get_launch_command(master_port, worker_port, working_dir)
        )
        self._group.execute_task(task, host, omit_on_join=True, debug=debug)
        return worker_port

    @classmethod
    def _get_launch_command(
        cls, master_port: int, worker_port: int, working_directory: str
    ) -> str:
        """Get the shell command for starting a worker instance.

        Returns:
             str: The launch command.
        """
        return (
            "dask-worker --worker-port="
            + str(worker_port)
            + " --local-directory="
            + working_directory
            + " localhost:"
            + str(master_port)
        )

    def cleanup(self) -> None:
        """Release all resources."""
        self.log.info("Cleanup the RoundRobinLauncher ...")
        super().cleanup()


class DaskCluster(MasterWorkerCluster):
    """Convenient class for launching a Dask cluster in a `RuntimeGroup`.

    DaskCluster inherits from MasterWorkerCluster. See its documentation to get a list of the inherited methods
    and attributes.

    The number of DASK workers defaults to the number of `Runtimes` in the used `RuntimeGroup`. This number can be
    adjusted so that more or less workers than available `Runtimes` can be used. Per default the desired number of
    workers is started in a round robin way as implemented in `RoundRobinLauncher`. Consequently, this leads to an
    equal distribution of DASK workers in the `RuntimeGroup`. You can provide a custom implementation inheriting from
    the `WorkerLauncher` class in order to execute a different strategy how workers should be started. The
    DASK master (i.e. scheduler) will always be started on localhost as implemented in `LocalMasterLauncher`. This
    behavior can also be changed by providing a custom implementation inheriting from the `MasterLauncher`.
    """

    DEFAULT_MASTER_PORT = 8786
    PIP_INSTALL_COMMAND = 'pip install -q "dask[complete]"'

    def __init__(
        self,
        runtime_group: RuntimeGroup,
        ports: Optional[List[int]] = None,
        master_launcher: Optional[MasterLauncher] = None,
        worker_launcher: Optional[WorkerLauncher] = None,
    ):
        """Initialization method.

        Args:
            runtime_group: The `RuntimeGroup` contains all `Runtimes` which can be used for starting the DASK entities.
            ports: The list of ports which will be used to instantiate a cluster. Defaults to
                                        `list(range(self.DEFAULT_PORT_RANGE_START, self.DEFAULT_PORT_RANGE_END))`.
            master_launcher: Optionally, an instance implementing the `MasterLauncher` interface can be given, which
                             implements the strategy for launching the master instances in the cluster. If None, then
                             `LocalMasterLauncher` is used.
            worker_launcher: Optionally, an instance implementing the `WorkerLauncher` interface can be given, which
                             implements the strategy for launching the worker instances. If None, then
                             `RoundRobinLauncher` is used.
        """
        super().__init__(runtime_group, ports)

        self._master_launcher = (
            master_launcher if master_launcher else LocalMasterLauncher(runtime_group)
        )
        self._worker_launcher = (
            worker_launcher if worker_launcher else RoundRobinLauncher(runtime_group)
        )

        self.log.debug("DaskCluster initialized.")

    def get_client(self, timeout: int = 2) -> Client:
        """Get a connected Dask client.

        Args:
            timeout: The timeout (s) value passed on to the Dask `Client` constructor. Defaults to 2.

        Raises:
            TimeoutError: If client connection `timeout` expires.
        """
        return Client(
            "localhost:" + str(self.master_port), timeout=timeout
        )  # Raises TimeoutError

    def cleanup(self) -> None:
        """Release all resources."""
        self.log.info("Cleanup the RoundRobinLauncher ...")
        super().cleanup()
