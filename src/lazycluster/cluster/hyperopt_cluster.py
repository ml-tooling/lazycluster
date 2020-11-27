"""Module for conveniently managing a [Hyperopt](https://github.com/hyperopt/hyperopt) cluster."""

import os
import time
from typing import List, Optional, Union

from lazycluster import Runtime, RuntimeGroup, RuntimeTask, _utils
from lazycluster.cluster import MasterLauncher, MasterWorkerCluster, WorkerLauncher
from lazycluster.cluster.exceptions import MasterStartError
from lazycluster.exceptions import PortInUseError
from lazycluster.utils import Environment


class MongoLauncher(MasterLauncher):
    """Abstract implementation of the `MasterLauncher` interface used to implement a concrete launch strategy for mongodb instance used in hyperopt.

    This class implements the logic for starting a MongoDB instance on localhost. Hence, we simply treat the MongoDB
    instance as master node.
    """

    def __init__(self, runtime_group: RuntimeGroup):
        """Initialization method.

        Args:
            runtime_group: The group where the workers will be started.
        """
        super().__init__(runtime_group)
        self.dbpath: Optional[str] = None


class LocalMongoLauncher(MongoLauncher):
    """Concrete implementation of the `MasterLauncher` interface. See its documentation to get a list of the inherited methods and attributes.

    This class implements the logic for starting a MongoDB instance on localhost. Hence, we simply treat the MongoDB
    instance as master node.
    """

    def start(
        self, ports: Union[List[int], int], timeout: int = 0, debug: bool = False
    ) -> List[int]:
        """Launch a master instance.

        Note:
            If you create a custom subclass of MasterLauncher which will not start the master instance on localhost
            then you should pass the debug flag on to `execute_task()` of the `RuntimeGroup` or `Runtime` so that you
            can benefit from the debug feature of `RuntimeTask.execute()`.

        Args:
            ports: Port where the DB should be started. If a list is given then the first port that is free in the
                   `RuntimeGroup` will be used. The actual chosen port can be requested via the property `port`.
            timeout: Timeout (s) after which an MasterStartError is raised if DB instance not started yet. Defaults to
                     3 seconds.
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

        if debug:
            self.log.debug("The debug flag has no effect in LocalMongoLauncher.")

        _ports: Union[List[int], int] = (
            ports.copy() if isinstance(ports, list) else ports
        )

        if not isinstance(_ports, list):
            if _utils.localhost_has_free_port(_ports) and self._group.has_free_port(
                _ports, exclude_hosts=Runtime.LOCALHOST
            ):
                self._port = master_port = _ports
            else:
                raise PortInUseError(_ports, self._group)

        else:
            self._port = master_port = self._group.get_free_port(
                _ports
            )  # Raises NoPortsLeftError
            _ports = _utils.get_remaining_ports(_ports, master_port)

        self.log.debug(
            f"Starting MongoDB on localhost on port {str(master_port)} with dbpath `{self.dbpath}` and "
            f"logfile `{self.dbpath}/{HyperoptCluster.MONGO_LOG_FILENAME}`."
        )

        # Start the mongod deamon process
        return_code = os.system(self.get_mongod_start_cmd())

        if return_code != 0:
            cause = (
                f"Please verify that (1) MongoDB is installed, (2) the dbpath `{self.dbpath}` exists with the "
                f"rights required by mongod and (3) that no other MongoDB instance is using and consequently "
                f"locking the respective files (=> Init HyperoptCluster with another dbpath "
                f"or manually stop the mongod process). See hyperopt docs in README for further details."
            )
            raise MasterStartError("localhost", master_port, cause)

        time.sleep(timeout)  # Needed for being able to check the port

        if not _utils.localhost_has_free_port(master_port):
            self.log.info("MongoDB started on localhost on port " + str(self._port))
        else:
            self.log.debug(
                "MongoDB could NOT be started successfully on port " + str(self._port)
            )
            cause = f"The master port {master_port} is still free when checking after the timeout of {timeout} seconds."
            raise MasterStartError("localhost", master_port, cause)

        # Sets up ssh tunnel for scheduler such that all communication is routed over the
        # local machine and all entities can talk to each the scheduler on localhost.
        self.log.info("Expose the MongoDB port in the RuntimeGroup.")
        self._group.expose_port_to_runtimes(self._port)

        return _ports if isinstance(_ports, list) else []

    def get_mongod_start_cmd(self) -> str:
        """Get the shell command for starting mongod as a deamon process.

        Returns:
            str: The shell command.
        """
        return (
            f"mongod --fork --logpath={self.dbpath}/{HyperoptCluster.MONGO_LOG_FILENAME} --dbpath={self.dbpath} "
            f"--port={self._port}"
        )

    def get_mongod_stop_cmd(self) -> str:
        """Get the shell command for stopping the currently running mongod process.

        Returns:
            str: The shell command.
        """
        return f"mongod --shutdown --dbpath={self.dbpath}"

    def cleanup(self) -> None:
        """Release all resources."""
        self.log.info("Stop the MongoDB ...")
        self.log.debug("Cleaning up the LocalMasterLauncher ...")
        return_code = os.system(self.get_mongod_stop_cmd())
        if return_code == 0:
            self.log.info("MongoDB successfully stopped.")
        else:
            self.log.warning("MongoDB daemon could NOT be stopped.")
        super().cleanup()


class RoundRobinLauncher(WorkerLauncher):
    """Concrete WorkerLauncher implementation for launching hyperopt workers in a round robin manner.

    See the `WorkerLauncher` documentation to get a list of the inherited methods and attributes.
    """

    def __init__(self, runtime_group: RuntimeGroup, dbname: str, poll_interval: float):
        """Initialization method.

        Args:
            runtime_group: The group where the workers will be started.
            dbname: The name of the mongodb instance.
            poll_interval: The poll interval of the hyperopt worker.

        Raises.
            ValueError: In case dbname is empty.
        """
        super().__init__(runtime_group)
        self._ports = None

        if not dbname:
            raise ValueError("dbname must not be empty")
        self._dbname = dbname

        if not poll_interval:
            raise ValueError("poll_interval must not be empty")
        self._poll_interval = poll_interval

        self.log.debug("RoundRobinLauncher initialized.")

    def start(
        self,
        worker_count: int,
        master_port: int,
        ports: List[int] = None,
        debug: bool = True,
    ) -> List[int]:
        """Launches the worker instances in the `RuntimeGroup`.

        Args:
            worker_count: The number of worker instances to be started in the group.
            master_port:  The port of the master instance.
            ports: Without use here. Only here because we need to adhere to the interface defined by the
                   WorkerLauncher class.
            debug: If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then
                   the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to
                   `False`.

        Returns:
            List[int]: The updated port list after starting the workers, i.e. the used ones were removed.
        """
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
            # working_dir = runtimes[runtime_index].working_dir
            assert host == runtimes[runtime_index].host

            self.log.debug(
                f"Launch Hyperopt worker with index {worker_index} on Runtime {host}"
            )

            self._launch_single_worker(host, worker_index, master_port, debug)

        return ports if isinstance(ports, list) else []

    def _launch_single_worker(
        self, host: str, worker_index: int, master_port: int, debug: bool
    ) -> None:
        """Launch a single worker instance in a `Runtime` in the `RuntimeGroup`."""
        # 2. Start the worker on this port
        task = RuntimeTask("launch-hyperopt-worker-" + str(worker_index))
        task.run_command(
            self._get_launch_command(master_port, self._dbname, self._poll_interval)
        )
        self._group.execute_task(task, host, omit_on_join=True, debug=debug)

    @classmethod
    def _get_launch_command(
        cls, master_port: int, dbname: str, poll_interval: float = 0.1
    ) -> str:
        """Get the shell command for starting a worker instance.

        Returns:
             str: The launch command.
        """
        return (
            f"hyperopt-mongo-worker --mongo=localhost:{str(master_port)}/{dbname} "
            f"--poll-interval={str(poll_interval)}"
        )

    def cleanup(self) -> None:
        """Release all resources."""
        self.log.info("Cleanup the RoundRobinLauncher ...")
        super().cleanup()


class HyperoptCluster(MasterWorkerCluster):
    """Convenient class for launching a Hyperopt cluster in a `RuntimeGroup`.

    HyperoptCluster inherits from MasterWorkerCluster. See its documentation to get a list of the inherited methods
    and attributes.

    The number of hyperopt workers defaults to the number of `Runtimes` in the used `RuntimeGroup`. This number can be
    adjusted so that more or less workers than available `Runtimes` can be used. Per default the desired number of
    workers is started in a round robin way as implemented in `RoundRobinLauncher`. Consequently, this leads to an
    equal distribution of hyperopt workers in the `RuntimeGroup`. You can provide a custom implementation inheriting
    from the `WorkerLauncher` class in order to execute a different strategy how workers should be started. The
    master instance (i.e. the mongoDB) will always be started on localhost as implemented in `LocalMasterLauncher`. This
    behavior can also be changed by providing a custom implementation inheriting from the `MasterLauncher`.
    """

    MONGO_LOG_FILENAME = "hyperopt_mongo.log"
    DEFAULT_MASTER_PORT = 27017
    ENV_NAME_MONGO_URL = "MONGO_CONNECTION_URL"

    def __init__(
        self,
        runtime_group: RuntimeGroup,
        mongo_launcher: Optional[MongoLauncher] = None,
        worker_launcher: Optional[WorkerLauncher] = None,
        dbpath: Optional[str] = None,
        dbname: str = "hyperopt",
        worker_poll_intervall: float = 0.1,
    ):
        """Initialization method.

        Args:
            runtime_group: The `RuntimeGroup` contains all `Runtimes` which can be used for starting the entities.
            mongo_launcher: Optionally, an instance implementing the `MasterLauncher` interface can be given, which
                            implements the strategy for launching the master instances in the cluster. If None, then
                            `LocalMasterLauncher` is used.
            worker_launcher: Optionally, an instance implementing the `WorkerLauncher` interface can be given, which
                             implements the strategy for launching the worker instances. If None, then
                             `RoundRobinLauncher` is used.
            dbpath: The directory where the db files will be kept. Defaults to a `mongodb` directory inside the
                    `utils.Environment.main_directory`.
            dbname: The name of the database to be used for experiments. See MongoTrials url scheme in hyperopt
                    documentation for more details. Defaults to ´hyperopt´.
            worker_poll_intervall: The poll interval of the hyperopt worker. Defaults to `0.1`.

        Raises:
            PermissionError: If the `dbpath` does not exsist and could not be created due to lack of permissions.
        """
        super().__init__(runtime_group)

        self._master_launcher = mongo_launcher or LocalMongoLauncher(runtime_group)

        if dbpath:
            self._master_launcher.dbpath = os.path.join(
                Environment.main_directory, "mongodb"
            )
            assert self._master_launcher.dbpath
            try:
                os.makedirs(self._master_launcher.dbpath)  # Raises PermissionError
            except FileExistsError:
                # All good because the dir already exists
                pass
        else:
            self._master_launcher.dbpath = dbpath

        self._dbname = dbname

        self._worker_launcher = (
            worker_launcher
            if worker_launcher
            else RoundRobinLauncher(runtime_group, dbname, worker_poll_intervall)
        )

        self.log.debug("HyperoptCluster initialized.")

    @property
    def mongo_trial_url(self) -> str:
        """The MongoDB url indicating what mongod process and which database to use.

        Note:
            The format is the format required by the hyperopt MongoTrials object.

        Returns:
            str: URL string.
        """
        if not self.master_port:
            self.log.warning(
                "HyperoptCluster.mongo_trial_url was requested although the master_port is not yet set."
            )

        return f"mongo://localhost:{self.master_port}/{self.dbname}/jobs"

    @property
    def mongo_url(self) -> str:
        """The MongoDB url indicating what mongod process and which database to use.

        Note:
            The format is `mongo://host:port/dbname`.

        Returns:
            str: URL string.
        """
        if not self.master_port:
            self.log.warning(
                "HyperoptCluster.mongo_trial_url was requested although the master_port is not yet set."
            )

        return f"mongo://localhost:{self.master_port}/{self.dbname}"

    @property
    def dbname(self) -> str:
        """The name of the MongoDB database to be used for experiments."""
        return self._dbname

    def start_master(
        self, master_port: Optional[int] = None, timeout: int = 3, debug: bool = False
    ) -> None:
        """Start the master instance.

        Note:
            How the master is actually started is determined by the the actual `MasterLauncher` implementation. Another
            implementation adhering to the `MasterLauncher` interface can be provided in the constructor of the cluster
            class.

        Args:
            master_port: Port of the master instance. Defaults to self.DEFAULT_MASTER_PORT, but another one is chosen if
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
        super().start_master(master_port, timeout)
        self._group.add_env_variables({self.ENV_NAME_MONGO_URL: self.mongo_trial_url})

    def cleanup(self) -> None:
        """Release all resources."""
        self.log.info("Shutting down the HyperoptCluster...")
        super().cleanup()
