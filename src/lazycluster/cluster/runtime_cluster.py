"""Module comprising the abstract RuntimeCluster class with its related `launcher strategy` classes.

Note: The design of the launcher classes follows the strategy pattern.
"""
import atexit
import logging
from subprocess import Popen
from typing import Dict, List, Optional, Union

from lazycluster.exceptions import LazyclusterError
from lazycluster.runtime_mgmt import RuntimeGroup


class MasterLauncher(object):
    """Abstract class for implementing the strategy for launching the master instance of the cluster."""

    def __init__(self, runtime_group: RuntimeGroup):
        """Initialization method.

        Args:
            runtime_group: The group where the workers will be started.
        """
        # Create the Logger
        self.log = logging.getLogger(__name__)

        self._group = runtime_group
        self._port: Union[int, None] = None  # Needs to be set in self.start()
        self._process: Optional[Popen] = None  # Needs to be set in self.start()

        self.log.debug("MasterLauncher initialized.")

    @property
    def port(self) -> Optional[int]:
        """The port where the master instance is started on. Will be None if not yet started.

        Returns:
            Optional[int]: The master port.
        """
        return self._port

    @property
    def process(self) -> Optional[Popen]:
        """The process object where the master instance was started in.

        Returns:
             Optional[Popen]: The process object or None if not yet started.
        """
        return self._process

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
                  `RuntimeGroup` will be used. The actual chosen port can requested via the property `port`.
            timeout: Timeout (s) after which an MasterStartError is raised if master instance not started yet.
            debug: If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then
                   the stdout/stderr will be added to python logger with level debug after each task step. Defaults to
                   `False`.

        Returns:
            List[int]: In case a port list was given the updated port list will be returned. Otherwise an empty list.

        Raises:
            PortInUseError: If a single port is given and it is not free in the `RuntimeGroup`.
            NoPortsLeftError: If a port list was given and none of the ports is actually free in the `RuntimeGroup`.
            MasterStartError: If master was not started after the specified `timeout`.
        """

        # The actual values for the following instance attributes need to be set within the concrete implementations:
        # - self._port
        # - self._process (In case the master is started in a process managed by the MasterLauncher instance )

        raise NotImplementedError

    def cleanup(self) -> None:
        """Release all resources."""
        self.log.debug("Cleaning up MasterLauncher ...")
        if self._process:
            self._process.terminate()


class WorkerLauncher(object):
    """Abstract class for implementing the strategy for launching worker instances within a RuntimeGroup.

    In order to implement a new concrete `WorkerLauncher` subclass you need to implement the start method. Please
    consider the comments of the start method because some internal variables need to be set in the concrete
    implementation.

    Moreover, the `setup_worker_ssh_tunnels()` method can be used to setup ssh tunnels so that all entities can talk to
    each other.
    """

    def __init__(self, runtime_group: RuntimeGroup):
        """Initialization method.

        Args:
            runtime_group: The group where the workers will be started in.
        """
        # Create the Logger
        self.log = logging.getLogger(__name__)

        self._group = runtime_group
        self._ports_per_host: Dict[
            str, List[int]
        ] = {}  # Needs to be set in `self.start()`

        self.log.debug("Worker launcher initialized")

    def __repr__(self) -> str:
        return "%s(%r)" % (self.__class__, self.__dict__)

    @property
    def ports_per_host(self) -> Dict[str, List[int]]:
        """Dictionary with the host as key and a port list as value. The list contains all ports where a worker instance is reachable on the respective host.

        Returns:
            Dict[str, List[int]]: The ports per host as a dictionary.
        """
        return self._ports_per_host

    def start(
        self, worker_count: int, master_port: int, ports: List[int], debug: bool = False
    ) -> List[int]:
        """Launches the worker instances in the `RuntimeGroup`.

        Args:
            worker_count: The number of worker instances to be started in the group.
            master_port:  The port of the master instance.
            ports: The ports to be used for starting the workers. Only ports from the list will be chosen that are
                   actually free.
            debug: If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then
                   the stdout/stderr will be added to python logger with level debug after each task step. Defaults to
                   `False`.

        Returns:
            List[int]: The updated port list after starting the workers, i.e. the used ones were removed.

        Raises:
            NoPortsLeftError: If there are not enough free ports for starting all workers.
        """

        # 1. The actual values for the following instance attributes need to be set within the concrete implementations:
        # - self._ports_per_host

        # 2. Raise `NoPortsLeftError` if there were not sufficient free ports in the list

        raise NotImplementedError

    def setup_worker_ssh_tunnels(self) -> None:
        """Set up ssh tunnel for workers such that all communication is routed over the local machine and all entities can talk to each other on localhost.

        Note:
            This method needs to be called if the communication between the worker instances is necessary, e.g. in case
            of DASK or Apache Flink, where data needs to be shuffled between the different entities.

        Raises:
            ValueError: If host is not contained.
            PortInUseError: If `group_port` is occupied on the local machine.
            NoPortsLeftError: If `group_ports` was given and none of the ports was free.
        """
        self.log.info("Setting up ssh tunnel for inter worker communication.")
        for host, ports in self.ports_per_host.items():
            for worker_port in ports:
                self._group.expose_port_from_runtime_to_group(
                    host, worker_port
                )  # Raises all errors

    def cleanup(self) -> None:
        """Release all resources."""
        self.log.debug("Cleaning up WorkerLauncher ...")
        self.log.debug("No WorkerLauncher resources to be released")


class RuntimeCluster(object):
    """Abstract cluster class.

    All further cluster implementations should inherit from this class either directly (e.g. the abstract class
    `MasterWorkerCluster`) or indirectly (e.g. the DaskCluster which is an concrete implementation of the
    `MasterWorkerCluster`).
    """

    def __repr__(self) -> str:
        return "%s(%r)" % (self.__class__, self.__dict__)


class MasterWorkerCluster(RuntimeCluster):
    """Class for clusters following a master-worker architecture.

    Usually you want to inherit from this class and do not want to use it directly. It is recommended to treat this
    class as an abstract class or an interface.

    Examples:
        Create a cluster with all `Runtimes` detected by the `RuntimeManager`.

        ```python
        from lazycluster import RuntimeManager
        cluster = MyMasterWorkerClusterImpl(RuntimeManager().create_group())
        cluster.start()
        ```

        Use different strategies for launching the master and the worker instance as the default ones by providing
        custom implementation of `MasterLauncher` and `WorkerLauncher`.

        ```python
        cluster = MyMasterWorkerClusterImpl(RuntimeManager().create_group(),
                                            MyMasterLauncherImpl(),
                                            MyWorkerLauncherImpl()
        cluster.start()
        ```
    """

    DEFAULT_MASTER_PORT = 60000
    DEFAULT_PORT_RANGE_START = 60001  # Can be overwritten in subclasses
    DEFAULT_PORT_RANGE_END = 60200  # Can be overwritten in subclasses

    def __init__(
        self,
        runtime_group: RuntimeGroup,
        ports: Optional[List[int]] = None,
        master_launcher: Optional[MasterLauncher] = None,
        worker_launcher: Optional[WorkerLauncher] = None,
    ):
        """Initialization method.

        Args:
            runtime_group: The `RuntimeGroup` contains all `Runtimes` which can be used for starting the cluster
                           entities.
            ports: The list of ports which will be used to instantiate a cluster. Defaults to
                   `list(range(self.DEFAULT_PORT_RANGE_START, self.DEFAULT_PORT_RANGE_END)`.
            master_launcher: Optionally, an instance implementing the `MasterLauncher` interface can be given, which
                             implements the strategy for launching the master instances in the cluster. If None, then
                             the default of the concrete cluster implementation will be chosen.
            worker_launcher: Optionally, an instance implementing the `WorkerLauncher` interface can be given, which
                             implements the strategy for launching the worker instances. If None, then the default of
                             the concrete cluster implementation will be chosen.
        """
        # Create the Logger
        self.log = logging.getLogger(__name__)

        self._group = runtime_group
        self._ports = (
            ports
            if ports
            else list(range(self.DEFAULT_PORT_RANGE_START, self.DEFAULT_PORT_RANGE_END))
        )
        self._master_launcher = master_launcher
        self._worker_launcher = worker_launcher

        # Cleanup will be done atexit since usage of destructor may lead to exceptions
        atexit.register(self.cleanup)

        self.log.debug("MasterWorkerCluster initialized.")

    def __str__(self) -> str:
        return type(self).__name__ + " with " + str(self._group)

    @property
    def master_port(self) -> Optional[int]:
        """The port where the master instance was started. None, if not yet started.

        Returns:
            Optional[int]: The master port.
        """
        return self._master_launcher.port if self._master_launcher else None

    @property
    def runtime_group(self) -> RuntimeGroup:
        """The RuntimeGroup.

        Returns:
            RuntimeGroup: The used group.
        """
        return self._group

    def start(
        self,
        worker_count: Optional[int] = None,
        master_port: Optional[int] = None,
        debug: bool = False,
    ) -> None:
        """Convenient method for launching the cluster.

        Internally, `self.start_master()` and `self.start_workers()` will be called.

        Args:
            master_port: Port of the cluster master. Will be passed on to `self.start()`, hence see respective method
                         for further details.
            worker_count: The number of worker instances to be started in the cluster. Will be passed on to
                          `self.start()`, hence see respective method for further details.
            debug: If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then
                   the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to
                   `False`.

        """
        self.log.info("Starting the cluster ...")
        self.start_master(master_port, debug=debug)
        self.start_workers(worker_count, debug=debug)

    def start_master(
        self, master_port: Optional[int] = None, timeout: int = 3, debug: bool = False
    ) -> None:
        """Start the master instance.

        Note:
            How the master is actually started is determined by the the actual `MasterLauncher` implementation. Another
            implementation adhering to the `MasterLauncher` interface can be provided in the constructor of the cluster
            class.

        Args:
            master_port: Port of the master instance. Defaults to `self.DEFAULT_MASTER_PORT`, but another one is chosen if
                         the port is not free within the group. The actual chosen port can be requested via
                         self.master_port.
            timeout: Timeout (s) after which an MasterStartError is raised if master instance not started yet.
            debug: If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. Has no effect for
                   if the master instance is started locally, what default MasterLauncher implementations usually do.

        Raises:
            PortInUseError: If a single port is given and it is not free in the `RuntimeGroup`.
            NoPortsLeftError: If there are no free ports left in the port list for instantiating the master.
            MasterStartError: If master was not started after the specified `timeout`.
        """
        if not self._master_launcher:
            raise LazyclusterError("Master Launcher does not exist.")

        # 1. Determine a port or port list
        overwrite_port_list = False
        if master_port:
            ports: Union[int, List[int]] = master_port
        elif self._group.has_free_port(self.DEFAULT_MASTER_PORT):
            ports = self.DEFAULT_MASTER_PORT
        else:
            ports = self._ports
            overwrite_port_list = True

        # 2. Trigger the actual logic for starting the master instance
        ports = self._master_launcher.start(
            ports, timeout, debug
        )  # Raises the possible exceptions

        if overwrite_port_list:
            self._ports = ports

        # Some attributes must be set in the given MasterLauncher implementation after
        # starting the master to ensure correct behavior of MasterWorkerCluster
        # => indicates a wrong implementation of the given launcher class
        assert self._master_launcher.port
        if not self._master_launcher.process:
            self.log.debug(
                "No self._master_launcher.process is set after starting the cluster master. If the master"
                "instance was not started as a deamon, then this could indicate buggy implementation. The"
                "variable should be set to be able to eventually shutdown the cluster."
            )

        self.log.info(f"Master instance started on port {str(self.master_port)}.")

    def start_workers(self, count: Optional[int] = None, debug: bool = False) -> None:
        """Start the worker instances.

        Note:
            How workers are actually started is determined by the the actual `WorkerLauncher` implementation. Another
            implementation adhering to the `WorkerLauncher` interface can be provided in the constructor of the cluster
            class.

        Args:
            count: The number of worker instances to be started in the cluster. Defaults to the number of runtimes in
                   the cluster.
            debug: If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then
                   the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to
                   `False`.

        Raises:
            NoPortsLeftError: If there are no free ports left in the port list for instantiating new worker entities.
        """

        if not self._worker_launcher:
            raise LazyclusterError("Worker launcher does not exist")

        if not count:
            count = self._group.runtime_count

        assert self.master_port

        self._ports = self._worker_launcher.start(
            count, self.master_port, self._ports, debug
        )

        # Some attributes must be set in the given MasterLauncher implementation after
        # starting the master to ensure correct behavior of MasterWorkerCluster
        # => indicates a wrong implementation of the given launcher class
        # e.g. for DASK -> assert self._worker_launcher.ports_per_host

        self.log.info("Worker instances started.")

    def print_log(self) -> None:
        """Print the execution log.

        Note:
            This method is a convenient wrapper for the equivalent method of the contained `RuntimeGroup`.

        """
        self.runtime_group.print_log()

    def cleanup(self) -> None:
        """Release all resources."""
        self.log.info("Shutting down the MasterWorkerCluster ...")
        if self._worker_launcher:
            self._worker_launcher.cleanup()
        if self._master_launcher:
            self._master_launcher.cleanup()
        self._group.cleanup()
