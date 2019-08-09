"""Module comprising the abstract RuntimeCluster class with its related `launcher strategy` classes."""
from typing import List, Tuple, Optional, Dict, Union

import atexit

from subprocess import Popen
from lazycluster.runtime_mgmt import RuntimeGroup


class MasterLauncher(object):
    """Abstract class for implementing the strategy for launching the cluster master instance. """

    def __init__(self, runtime_group: RuntimeGroup):
        """Constructor method.

        Args:
            runtime_group (RuntimeGroup): The group where the workers will be started.
        """
        self._group = runtime_group
        self._port = None            # Needs to be set in self.start()
        self._process: Popen = None  # Needs to be set in self.start()

    @property
    def port(self) -> int:
        return self._port

    @property
    def process(self) -> Popen:
        return self._process

    def start(self, ports: Union[List[int], int], timeout: int = 3) -> List[int]:
        """Launch a master instance.

        Args:
            ports (int): Port where the master should be started. If a list is given then the first port that is free in
                         the `RuntimeGroup` will be used. The actual chosen port can requested via the property `port`.
            timeout (int): Timeout (s) after which check will be executed if scheduler is started.

        Returns:
            List[int]: In case a port list was given the updated port list will be returned. Otherwise an empty list.

        Raises:
            PortInUseError: If a single port is given and it is not free in the `RuntimeGroup`.
            NoPortsLeftError: If a port list was given and none of the ports is actually free in the `RuntimeGroup`.
        """

        # The actual values for the following instance attributes need to be set within the concrete implementations:
        # - self._port
        # - self._process

        raise NotImplementedError


class WorkerLauncher(object):
    """Abstract class for implementing the a strategy for
    launching worker instances within a RuntimeGroup. """

    def __init__(self, runtime_group: RuntimeGroup):
        """Constructor method.

        Args:
            runtime_group (RuntimeGroup): The group where the workers will be started.
        """
        self._group = runtime_group
        self._ports_per_host: Dict[str, List[int]] = {}  # Needs to be set in `self.start()`

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    @property
    def ports_per_host(self) -> Dict[str, List[int]]:
        return self._ports_per_host

    def start(self, worker_count: int, master_port: int, ports: List[int]) -> List[int]:
        """Launches the worker instances in the RuntimeGroup.

        Args:
            worker_count (int): The number of worker instances to be started in the group.
            ports (List[int]): The ports to be used for starting the workers. Only ports from the list will be chosen
                               that are actually free.
            master_port (int): The port of the Dask scheduler.
        Returns:
             Tuple[Dict[str, int], List[int]]:
                Dict[str, int]: Hosts as key and the worker ports as values.
                List[int]: The updated port list after starting the workers.
        """

        # The actual values for the following instance attributes need to be set within the concrete implementations:
        # - self._ports_per_host

        raise NotImplementedError

    def setup_worker_ssh_tunnels(self):
        """Sets up ssh tunnel for workers such that all communication is routed over the
        local machine and all entities can talk to each other on localhost.

        Note: This method needs to be called if the communication between the worker instances is necessary,
              e.g. in case of DASK or Apache Flink.
        """
        for host, ports in self.ports_per_host.items():
            for worker_port in ports:
                self._group.expose_port_from_runtime_to_group(host, worker_port)


class RuntimeCluster(object):
    """Abstract cluster class. """

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


class MasterWorkerCluster(RuntimeCluster):
    """Abstract class for clusters following a master-worker architecture. """

    DEFAULT_MASTER_PORT = 60000
    DEFAULT_PORT_RANGE_START = 60001  # Can be overwritten in subclasses
    DEFAULT_PORT_RANGE_END = 60200    # Can be overwritten in subclasses

    def __init__(self, runtime_group: RuntimeGroup, ports: Optional[List[int]] = None,
                 master_launcher: Optional[MasterLauncher] = None,
                 worker_launcher: Optional[WorkerLauncher] = None):
        """Initialize MasterWorkerCluster instance.

        Args:
            runtime_group (RuntimeGroup): RuntimeGroup contains all Runtimes which can be used for starting the Dask
                                          entities.
            ports (List[int]): The list of ports which will be used in the cluster. Defaults to range(60000, 61000).
            worker_launcher (Optional[WorkerLauncher]): Optionally, an instance implementing the `WorkerLauncher` interface can
                                                 be given, which implements the strategy for launching DASK worker
                                                 instances in the cluster. If None, the worker will be launched via a
                                                 RoundRobin strategy as implemented in `RoundRobinLauncher`.
        """
        self._group = runtime_group
        self._ports = ports if ports else list(range(self.DEFAULT_PORT_RANGE_START, self.DEFAULT_PORT_RANGE_END))
        self._master_launcher = master_launcher
        self._worker_launcher = worker_launcher

        # Cleanup will be done atexit since usage of destructor may lead to exceptions
        atexit.register(self.cleanup)

    def __str__(self):
        return type(self).__name__ + ' with ' + str(self._group)

    @property
    def master_port(self) -> int:
        """Get the scheduler port.

        Returns:
            int: The scheduler port. None if not yet started.
        """
        return self._master_launcher.port

    def start(self, worker_count: Optional[int] = None, master_port: Optional[int] = None):
        """Start the scheduler and the workers.

        Args:
            master_port (int): Port of the cluster master. Will be passed on to `self.start()`, hence see
                               respective method for further details.
            worker_count (int, Optional): The number of worker instances to be started in the cluster. Will be passed on
                                          to `self.start()`, hence see respective method for further details.

        """
        self.start_master(master_port)
        self.start_workers(worker_count)
        print('RuntimeCluster started ...')

    def start_master(self, master_port: Optional[int] = None, timeout: int = 3):
        """Launch a master instance.

        Args:
            master_port (int): Port of the cluster master. Defaults to self.DEFAULT_MASTER_PORT, but another one is
                               chosen if the port is not free within the group. The actual chosen port can be requested
                               via self.master_port.
            timeout (int): Timeout (s) after which check will be executed if scheduler is started.

        Raises:
            NoPortsLeftError: If there are no free ports left in the port list for instantiating new Dask entities.
        """
        # 1. Determine a port or port list
        overwrite_port_list = False
        if master_port:
            ports = master_port
        elif self._group.has_free_port(self.DEFAULT_MASTER_PORT):
            ports = self.DEFAULT_MASTER_PORT
        else:
            ports = self._ports
            overwrite_port_list = True

        # 2. Trigger the actual logic for starting the master instance
        ports = self._master_launcher.start(ports, timeout)

        if overwrite_port_list:
            self._ports = ports

        # Some attributes must be set in the given MasterLauncher implementation after
        # starting the master to ensure correct behavior of MasterWorkerCluster
        # => indicates a wrong implementation of the given launcher class
        assert self._master_launcher.port
        assert self._master_launcher.process

        print('Master instance started ...')

    def start_workers(self, count: Optional[int] = None):
        """Launch worker instances according to the `WorkerLauncher` strategy.

        An implementation of the `WorkerLauncher` interface can be provided in the constructor of the `RuntimeCluster` class.

        Args:
            count (int): The number of worker instances to be started in the cluster. Defaults to the number of runtimes
                         in the cluster.
         Raises:
            NoPortsLeftError: If there are no free ports left in the port list for instantiating new Dask entities.
        """
        if not count:
            count = self._group.runtime_count

        self._ports = self._worker_launcher.start(count, self.master_port, self._ports)

        # Some attributes must be set in the given MasterLauncher implementation after
        # starting the master to ensure correct behavior of MasterWorkerCluster
        # => indicates a wrong implementation of the given launcher class
        assert self._worker_launcher.ports_per_host

        print('Worker instances started ...')

    def cleanup(self):
        """Release all resources. """
        print('Shutting down DaskRuntimeCluster...')
        self._group.cleanup()
        self._master_launcher.process.terminate()