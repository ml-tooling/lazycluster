"""Runtimes module.

This module comprises classes for executing so called `RuntimeTasks` in `Runtimes` by leveraging the power of ssh.
The `RuntimeTask` class is a container for defining a sequence of elegantly task steps. This `RuntimeTask` can then be
executed either standalone or by passing it over to a `Runtime` instance. Passwordless ssh should be configured for all
hosts that should act as a `Runtime` to be able to conveniently manage those entities.

"""
import atexit
import logging
import os
import shutil
import tempfile
import time
import warnings
from multiprocessing import Manager, Process
from typing import Any, Callable, Dict, Generator, List, Optional, Union

import cloudpickle as pickle
from fabric import Connection

from lazycluster import _utils
from lazycluster.exceptions import (
    InvalidRuntimeError,
    LazyclusterError,
    NoPortsLeftError,
    PathCreationError,
    PortInUseError,
    TaskExecutionError,
)
from lazycluster.utils import ExecutionFileLogUtil


class RuntimeTask(object):
    """This class provides the functionality for executing a sequence of elementary operations over ssh.

    The [fabric](http://docs.fabfile.org/en/2.5/api/connection.html) library is used for handling ssh connections.
    A `RuntimeTask` can be composed from four different operations which we call steps, namely adding a step
    for running a shell command via `run_command()`, sending a file to a host via `send_file()`, retrieving
    a file from a host via `get_file()` or adding a step for executing a python function on a host via
    `run_function()`. The current restriction for running functions is that these functions need to be
    serializable via cloudpickle. To actually execute a `RuntimeTask`, i.e. the sequence of task steps, either a call
    to `execute()` is necessary or a handover to the `execute_task()` method of the `Runtime` class is necessary.
    Usually, a `RuntimeTask` or `RuntimeGroup` will be executed in a `Runtime` or in a `RuntimeGroup`.
    See its documentation for further details.

    Examples:
    ```python
    # 1. Define a function that should be executed remotely via a RuntimeTask
    def print():
        print('Hello World!')

    # 2. Create & compose the RuntimeTask by using the elementary operations
    my_task = RuntimeTask('my-task').run_command('echo Hello World!').run_function(print)

    # 3. Execute the RuntimeTask standalone w/o Runtime by handing over a fabric ssh connection
    from fabric import Connection
    task = my_task.execute(Connection('host'))

    # 4. Check the logs of the RuntimeTask execution
    task.print_log()
    log = task.execution_log
    ```
    """

    def __init__(self, name: Optional[str] = None):
        """Initialization method.

        Args:
            name: The name of the task. Defaults to None and consequently a unique identifier is generated via Python's
                  id() function.
        """

        # Create the Logger
        self.log = logging.getLogger(__name__)
        self._execution_log_file_path: Optional[str] = None

        self.name = name or ""
        if not self.name:
            self.name = str(id(self))

        # todo Check if typing is a problem
        self._task_steps: List["RuntimeTask._TaskStep"] = []
        self._execution_log: List[str] = []
        # File paths to files with function's pickled return data:
        self._function_return_pkl_paths: List[str] = []
        self._process: Optional[Process] = None

        self.omit_on_join: bool = False
        # Will be passed on to the fabric connection:
        self._env_variables: Dict[str, str] = {}

        # Will be created if run_function is executed
        self._temp_dir: Optional[str] = None

        # This indicates how many deep copies were created based on this task.
        # E.g. if this task was deep copied tiwce, then the index would be 2.
        self._copy_index: int = 0

        # Cleanup will be done atexit since usage of destructor may lead to exceptions
        atexit.register(self.cleanup)

        self.log.debug(f"RuntimeTask {self.name} initialized.")

    def __repr__(self) -> str:
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __str__(self) -> str:
        return type(self).__name__ + ": " + str(self.name)

    def __deepcopy__(self, memo: Optional[dict] = None) -> "RuntimeTask":
        """This functions implements the deep copy logic so that all relevant data is copied or recreated with similar values.

        Note:
            A custom implementation is necessary here since especially in run_function we automatically generate  pickle
            file paths. When broadcasting a task we need to copy the task since it holds state such as logs and paths.
            In order to circumvent the overwriting of such files, we need to ensure that new paths must be created.

        Returns:
            RuntimeTask: Deepcopy of the `RuntimeTask` itself.
        """
        # Increment the task index and append the index to the end of the task name
        # -> simplifies debugging
        self._copy_index += 1
        new_name = f"{self.name}-{self._copy_index}"

        copied_task = RuntimeTask(new_name)

        # Copy the task steps and re-execute run_function on the copied task,
        # since there will be individual file paths created among others.
        for step in self._task_steps:
            if step.type != self._TaskStep.TYPE_RUN_FUNCTION:
                copied_task._task_steps.append(step)
            elif step.function:
                copied_task.run_function(step.function, **step.func_kwargs)

        copied_task._env_variables = self._env_variables
        copied_task.omit_on_join = self.omit_on_join

        self.log.debug(
            f"Deep copy [{self._copy_index}] of RuntimeTask {self.name} created by using its custom "
            f"__deepcopy__ implementation."
        )

        return copied_task

    def cleanup(self) -> None:
        """Remove temporary used resources, like temporary directories if created."""
        self.log.debug(f"Start cleanup of task {self.name}.")
        if self._temp_dir:
            shutil.rmtree(self._temp_dir)
            self.log.debug(
                f"Temporary directory {self._temp_dir} of RuntimeTask {self.name} on localhost removed."
            )
            self._temp_dir = None

    @property
    def execution_log(self) -> List[str]:
        """The execution log as list.

        The list is empty as long as a task was not yet executed. Each log entry
        corresponds to a single task step and the log index starts at `0`. If th execution of an individual step does not
        produce and outut the list entry will be empty.

        Returns:
            List[str]: List with logs of the `RuntimeTask` execution.
        """
        return self._execution_log

    @property
    def execution_log_file_path(self) -> Optional[str]:
        """The execution log file path. This property is read-only and will be updated each time the `RuntimeTask` gets executed.

        Returns:
            Optional[str]: The path of the execution log.
        """
        return self._execution_log_file_path

    @property
    def function_returns(self) -> Generator[object, None, None]:
        """The return data produced by functions which were executed as a consequence of a `task.run_function()` call.

        Internally, a function return is saved as a pickled file. This method unpickles each file one after
        another and yields the data. Moreover, the return data will be yielded in the same order as the functions were
        executed.

        Yields:
            Generator[object, None, None]: Generator object yielding the return data of the functions executed during task execution.
        """
        self.log.debug(
            f"Start generating function returns for RuntimeTask {self.name}."
        )

        # Ensure that the task finished its execution already
        self.join()

        for return_pkl_path in self._function_return_pkl_paths:

            if not os.path.exists(return_pkl_path):
                warnings.warn(
                    "Pickle file "
                    + return_pkl_path
                    + " with function return data does not exist. "
                    "Please check the logs."
                )
                yield None
                continue

            with open(return_pkl_path, "rb") as file:
                yield pickle.load(file)

    @property
    def process(self) -> Optional[Process]:
        """The process object in which the task were executed. None, if not yet or synchronously executed."""
        return self._process

    @property
    def env_variables(self) -> Dict:
        """Environment parameters used when executing a task."""
        return self._env_variables

    @env_variables.setter
    def env_variables(self, env_variables: Dict) -> None:
        """Set environment parameters used when executing a RuntimeTask.

        Args:
            env_variables: The env variables as dictionary.
        """
        self._env_variables = env_variables

    def send_file(
        self, local_path: str, remote_path: Optional[str] = None
    ) -> "RuntimeTask":
        """Create a task step for sending either a single file or a folder from localhost to another host.

        Args:
            local_path: Path to file on local machine.
            remote_path: Path on the remote host. Defaults to the connection working directory. See
                         `RuntimeTask.execute()` docs for further details.

        Returns:
            RuntimeTask: self.

        Raises:
            ValueError: If local_path is emtpy.
        """
        if not local_path:
            raise ValueError("Local path must not be empty")

        self._task_steps.append(
            self._TaskStep.create_send_file_instance(local_path, remote_path)
        )

        self.log.debug(
            f"Step for sending the file {local_path} to {remote_path} was added to RuntimeTask {self.name}."
        )
        return self

    def get_file(
        self, remote_path: str, local_path: Optional[str] = None
    ) -> "RuntimeTask":
        """Create a task step for getting either a single file or a folder from another host to localhost.

        Args:
            remote_path: Path to file on host.
            local_path: Path to file on local machine. The remote file is downloaded  to the current working directory
                        (as seen by os.getcwd) using its remote filename if local_path is None. This is the default
                        behavior of fabric.

        Returns:
            RuntimeTask: self.

        Raises:
            ValueError: If remote path is emtpy.
            OSError: In case of non existent paths.
        """
        if not remote_path:
            raise ValueError("Remote path must not be empty")

        self._task_steps.append(
            self._TaskStep.create_get_file_instance(remote_path, local_path)
        )

        self.log.debug(
            f"Step for getting the file {remote_path} to {local_path} was added to RuntimeTask {self.name}."
        )
        return self

    def run_command(self, command: str) -> "RuntimeTask":
        """Create a task step for running a given shell command.

        Args:
            command: Shell command.

        Returns:
            RuntimeTask: self.

        Raises:
            ValueError: If command is emtpy.
        """
        if not command:
            raise ValueError("Command must not be emtpy")
        self._task_steps.append(self._TaskStep.create_run_command_instance(command))

        self.log.debug(
            f"Step for running the command `{command}` was added to RuntimeTask {self.name}."
        )
        return self

    def run_function(
        self, function: Callable[..., Any], **func_kwargs: Any
    ) -> "RuntimeTask":
        """Create a task step for executing a given python function on a remote host.

        The function will be transferred to the remote host via ssh and cloudpickle.
        The return data can be requested via the property `function_returns`.

        Note:
            Hence, the function must be serializable via cloudpickle and all dependencies must be available in its
            correct versions on the remote host for now. We are planning to improve the dependency handling.

        Args:
            function: The function to be executed remotely.
            **func_kwargs: kwargs which will be passed to the function.

        Returns:
            RuntimeTask: self.

        Raises:
            ValueError: If function is empty.
        """

        # Attention:
        #   Please do not change the current task step composition, i.e. the order of the task steps where the current
        #   TaskStep is composed of. The reason is the order of the task log, which will break. At least, the indices
        #   in Runtime._read_info() needs to be adapted. Of course, this change might affect existing users!!!

        if not function:
            raise ValueError("Function is invalid.")

        self.log.debug(
            f"Start generating steps to RuntimeTask {self.name} for executing function {function.__name__}"
        )

        steps = []

        # Create a temp directory for persisting the serialized function
        if not self._temp_dir:
            self._temp_dir = tempfile.mkdtemp()
            self.log.debug(
                f"Temporary directory {self._temp_dir} for RuntimeTask {self.name} on localhost created."
            )

        # We distinguish between local -  and remote filename because in case we execute a function in a
        # `Runtime('localhost')`, we may overwrite the files.
        input_function_name = function.__name__
        remote_file_name = self._create_file_name(input_function_name)
        local_file_name = "local_" + remote_file_name
        local_pickle_file_path = os.path.join(self._temp_dir, local_file_name)
        remote_pickle_file_path = os.path.join(".", remote_file_name)

        local_return_file_name = "return_" + remote_file_name
        remote_return_file_name = "remote_" + local_return_file_name
        local_return_pickle_file_path = os.path.join(
            self._temp_dir, local_return_file_name
        )
        remote_return_pickle_file_path = os.path.join(".", remote_return_file_name)

        # Hereby we can pickle the function incl. kwargs, since we are
        # going to pickle the wrapper and not only the function itself.
        def function_wrapper() -> Callable[..., Any]:
            # Make the function return data available
            return function(**func_kwargs)

        # Create cloud pickle file of the function_wrapper() and save it locally
        with open(local_pickle_file_path, "wb") as f:
            pickle.dump(function_wrapper, f)
            f.close()

        self.log.debug(
            f"Function {function.__name__} locally saved as pickle file under `{local_pickle_file_path}`."
        )

        # Add `TaskStep` for sending the pickled function_wrapper file to the Runtime
        steps.append(
            self._TaskStep.create_send_file_instance(
                local_pickle_file_path, remote_pickle_file_path
            )
        )
        self.log.debug(
            f"Step for sending the file {local_pickle_file_path} to {remote_pickle_file_path} was added to "
            f"RuntimeTask {self.name}."
        )

        # Ensure installation of cloudpickle
        run_cmd = "pip install -q cloudpickle"
        steps.append(self._TaskStep.create_run_command_instance(run_cmd))
        self.log.debug(
            f"Step for running the command `{run_cmd}` was added to RuntimeTask {self.name}."
        )

        # Create commands for executing the pickled function file
        # => pickle the return data and save it as a file on the remote host so that we can get the file back to the
        # local machine. Local machine means NOT the one where `function_wrapper()` is actually executed, but
        # the one where `task.run_function()` is actually executed.
        run_function_code = (
            "import cloudpickle as pickle; "
            "file=open('" + remote_pickle_file_path + "', 'rb'); "
            "fn=pickle.load(file); file.close(); result = fn(); "
            "file=open('" + remote_return_pickle_file_path + "', 'wb'); "
            "pickle.dump(result, file); file.close();"
        )

        run_cmd = 'python3 -c "' + run_function_code + '"'
        steps.append(self._TaskStep.create_run_command_instance(run_cmd))
        self.log.debug(
            f"Step for running the command `{run_cmd}` was added to RuntimeTask {self.name}."
        )

        # Ensure the cleanup of the created function pickle file on the Runtime
        run_cmd = "rm " + remote_pickle_file_path
        steps.append(self._TaskStep.create_run_command_instance(run_cmd))
        self.log.debug(
            f"Step for running the command `{run_cmd}` was added to RuntimeTask {self.name}."
        )

        # Get the return data back as pickled file
        steps.append(
            self._TaskStep.create_get_file_instance(
                remote_return_pickle_file_path, local_return_pickle_file_path
            )
        )
        self.log.debug(
            f"Step for getting the file {remote_return_pickle_file_path} to {local_return_pickle_file_path} "
            f"was added to RuntimeTask {self.name}."
        )

        self._function_return_pkl_paths.append(local_return_pickle_file_path)

        # Cleanup the return pickle file on the remote host
        run_cmd = "rm " + remote_return_pickle_file_path
        steps.append(self._TaskStep.create_run_command_instance(run_cmd))
        self.log.debug(
            f"Step for running the command `{run_cmd}` was added to RuntimeTask {self.name}."
        )

        self._task_steps.append(
            self._TaskStep.create_run_function_instance(steps, function, func_kwargs)
        )
        self.log.debug(
            f"Successfully added the final step for running the function {function.__name__} to the "
            f"RuntimeTask {self.name}."
        )

        self.log.debug(
            f"Finished generating steps for RuntimeTask {self.name} for executing "
            f"function {function.__name__}."
        )
        return self

    def execute(self, connection: Connection, debug: bool = False) -> None:
        """Execute the task on a remote host using a fabric connection.

        Note:
            Each individual task step will be executed relatively to the current directory of the fabric connection.
            Although, the current directory might have changed in the previous task step. Each directory change is
            temporary limited to a single task step.
            If the task gets executed via a `Runtime`, then the current directory will be the Runtimes working
            directory. See the `Runtime` docs for further details.
            Moreover, beside the regular Python log or the `debug` option you can access the execution logs via
            task.`execution.log`. The log gets updated after each task step.

        Args:
            connection: Fabric connection object managing the ssh connection to the remote host.
            debug : If `True`, stdout/stderr from the remote host will be printed to stdout. If, `False`
                    then the stdout/stderr will be written to an execution log file. Defaults to `False`.

        Raises:
            ValueError: If cxn is broken and connection can not be established.
            TaskExecutionError: If an executed task step can't be executed successfully.
            OSError: In case of file transfer and non existent paths.
        """
        exec_file_log_util = ExecutionFileLogUtil(connection.original_host, self.name)
        self._execution_log_file_path = exec_file_log_util.file_path

        # The Fabric connection will only consider the manually set working directory for connection.run()
        # but not fur connection.put() & connection.get(). Thus, we need to set the path in
        # these cases manually.
        from socket import gaierror

        try:
            working_dir = (
                connection.run("pwd", hide=True, warn=True)
                .stdout.replace("\n", "")
                .replace("\r", "")
            )
            self.log.debug(
                f"Current directory of connection to host {connection.original_host} is `{working_dir}`."
            )
        except gaierror:
            raise ValueError(
                "Connection cannot be established. connection: " + str(connection)
            )

        self.log.info(
            f"Start executing RuntimeTask {self.name} on host {connection.original_host}"
        )

        task_step_index = 0

        for task_step in self._task_steps:

            if task_step.type == self._TaskStep.TYPE_RUN_COMMAND:
                self._execute_run_command_step(
                    task_step, task_step_index, connection, debug, exec_file_log_util
                )

            elif task_step.type == self._TaskStep.TYPE_SEND_FILE:
                self._execute_send_file(
                    task_step, task_step_index, working_dir, connection
                )

            elif task_step.type == self._TaskStep.TYPE_GET_FILE:
                self._execute_get_file(
                    task_step, task_step_index, working_dir, connection
                )

            if task_step.type != self._TaskStep.TYPE_RUN_FUNCTION:
                task_step_index = task_step_index + 1
                continue

            # The remote python function execution is not an elementary TaskStep (as opposed to run_command,
            # send_file, get_file) but is composed of these. Hence, we will execute the necessary steps here in order to
            # execute the desired function remotely. Those steps where generated during the RuntimeTask.run_function()
            # execution and not directly created by the user.
            if task_step.type == self._TaskStep.TYPE_RUN_FUNCTION:
                if not task_step.function:
                    continue
                self.log.debug(
                    f"Start executing the generated steps that are necessary to execute the python function `{task_step.function.__name__}` remotely"
                )
                for function_step in task_step.function_steps:

                    if function_step.type == self._TaskStep.TYPE_RUN_COMMAND:
                        self._execute_run_command_step(
                            function_step,
                            task_step_index,
                            connection,
                            debug,
                            exec_file_log_util,
                        )

                    elif function_step.type == self._TaskStep.TYPE_SEND_FILE:
                        self._execute_send_file(
                            function_step, task_step_index, working_dir, connection
                        )

                    elif function_step.type == self._TaskStep.TYPE_GET_FILE:
                        self._execute_get_file(
                            function_step, task_step_index, working_dir, connection
                        )

                self.log.debug(
                    f"Finished executing the generated steps that are necessary to execute the python "
                    f"function `{task_step.function.__name__}` remotely."
                )

        self.log.info(
            f"Finished executing RuntimeTask {self.name} on host {connection.original_host}"
        )

    def join(self) -> None:
        """Block the execution until the `RuntimeTask` finished its asynchronous execution.

        Note:
            If self.omit_on_join is set, then the execution is omitted in order to prevent a deadlock.

        """
        if self.omit_on_join and self.process:
            self.log.debug(
                f"The execution of join() of RuntimeTask {self.name} is omitted, since this task is marked "
                f"as needs explicit termination."
            )
            return

        if not self.process:
            return

        self.log.info(
            f"Start joining the process that is executing RuntimeTask {self.name}."
        )
        self.process.join()
        self.log.info(
            f"Finished joining the process that is executing RuntimeTask {self.name}."
        )

    def print_log(self) -> None:
        """Print the execution log. Each log entry will be printed separately. The log index will be prepended."""
        if not self.execution_log:
            print("The log of task " + self.name + " is empty!")
        else:
            print("Log of Task " + self.name + ":")
        i = 0
        for entry in self.execution_log:
            print(str(i) + ": " + entry)
            i += 1

    # Private helper methods & attributes
    _function_index = 0
    _FUNCTION_PREFIX = "func"
    _PICKLE_FILENAME_EXT = "pkl"

    @classmethod
    def _create_file_name(cls, function_name: Optional[str] = None) -> str:
        """Creates a program unique function name."""
        if function_name:
            file_prefix = function_name
        else:
            file_prefix = cls._FUNCTION_PREFIX
        cls._function_index += 1
        return file_prefix + str(cls._function_index) + "." + cls._PICKLE_FILENAME_EXT

    def _execute_run_command_step(
        self,
        task_step: "_TaskStep",
        task_step_index: int,
        connection: Connection,
        debug: bool,
        exec_file_log_util: ExecutionFileLogUtil,
    ) -> None:
        self.log.debug(
            f"Start executing step {task_step_index} (`run_command`) from RuntimeTask {self.name} on host "
            f"{connection.original_host}. Command: `{task_step.command}`"
        )

        self.log.debug(
            f"Used environment vars on host {connection.original_host}: {self._env_variables}"
        )

        # The output will be sent to stdout in case of debug
        # Otherwise it gets written to an execution log file
        if debug:
            result = connection.run(
                task_step.command, warn=True, pty=True, env=self._env_variables
            )
        elif exec_file_log_util.file_path:
            with open(
                exec_file_log_util.file_path, exec_file_log_util.get_write_mode()
            ) as log_file:
                result = connection.run(
                    task_step.command,
                    warn=True,
                    pty=True,
                    out_stream=log_file,
                    env=self._env_variables,
                )
        else:
            raise LazyclusterError("ExecutionFileLogUtil.file_path is not defined")

        if not debug:
            self.log.debug(
                f"The stdout of step {task_step_index} (`run_command`) from RuntimeTask {self.name} on host "
                f"{connection.original_host} is `{result.stdout}`."
            )

        self._execution_log.append(result.stdout)

        if result.exited != 0:
            raise TaskExecutionError(
                task_step_index,
                self,
                connection.original_host,
                str(exec_file_log_util.file_path),
                result.stdout,
            )

    def _execute_send_file(
        self,
        task_step: "_TaskStep",
        task_step_index: int,
        working_dir: str,
        connection: Connection,
    ) -> None:
        # Ensure that we have a valid remote path
        remote_path = task_step.remote_path

        if not remote_path:
            # Manually set the working directory since fabric defaults to the os
            # user's home directory in case of file transfer
            local_dir, filename = os.path.split(task_step.local_path)
            remote_path = os.path.join(working_dir, filename)
            self.log.debug(
                f"Remote path was not given and manually set to the working directory {remote_path}."
            )

        elif remote_path.startswith("."):
            # Relative path -> in this case it will be interpreted relative to the working directory
            remote_path = os.path.join(working_dir, remote_path[2:])
            self.log.debug(
                "Remote path was relative path and changed to full path to the working directory."
            )

        # Update the path in the `_TaskStep` so that the actual used path is correctly stored
        task_step.remote_path = remote_path

        self.log.debug(
            f"Start executing TaskStep {task_step_index} (`send_file`) from RuntimeTask {self.name} "
            f"on host {connection.original_host}. File: `local: {task_step.local_path}`, "
            f"`remote: {task_step.remote_path}`."
        )

        connection.put(task_step.local_path, task_step.remote_path)

        self.log.info(
            f"Finished sending the file {task_step.local_path} to {task_step.remote_path} "
            f"on host {connection.original_host}"
        )

    def _execute_get_file(
        self,
        task_step: "_TaskStep",
        task_step_index: int,
        working_dir: str,
        connection: Connection,
    ) -> None:
        # Set working directory manually, so that it feels naturally for the user if he just
        # uses the filename without a path
        remote_path = task_step.remote_path
        if not remote_path.startswith("/"):
            remote_dir, filename = os.path.split(remote_path)
            remote_path = os.path.join(working_dir, filename)

        # or a relative path (-> will be interpreted relatively to the working directory)
        elif remote_path.startswith("."):
            remote_path = os.path.join(working_dir, remote_path[2:])

        # Update the path in the `_TaskStep` so that the actual used path is correctly stored
        task_step.remote_path = remote_path

        self.log.debug(
            f"Start executing step {task_step_index} (`get_file`) from RuntimeTask {self.name} on "
            f"host {connection.original_host}. File: `local: {task_step.local_path}`, "
            f"`remote: {task_step.remote_path}`."
        )

        connection.get(task_step.remote_path, task_step.local_path)

        self.log.info(
            f"Finished transferring remote file {task_step.remote_path} from host {connection.original_host} "
            f"to local file {task_step.local_path}."
        )

    class _TaskStep:
        """Represents an individual action, i.e. a `_TaskStep` within a `RuntimeTask`."""

        TYPE_RUN_COMMAND = "command"
        TYPE_SEND_FILE = "send-file"
        TYPE_GET_FILE = "get-file"
        TYPE_RUN_FUNCTION = "function"

        def __init__(
            self,
            step_type: str,
            local_path: Optional[str] = None,
            remote_path: Optional[str] = None,
            command: Optional[str] = None,
            # TODO: Refactor so that we get rid of the typing issue
            function_steps: List["RuntimeTask._TaskStep"] = [],
            function: Optional[Callable[..., Any]] = None,
            func_kwargs: Dict[str, Any] = {},
        ):
            self.type = step_type
            # Related to send_ / get_file
            self.local_path = local_path if local_path else ""
            self.remote_path = remote_path if remote_path else ""
            # Related to run_command
            self.command = command
            # Related to run_function
            self.function = function
            self.func_kwargs = func_kwargs
            self.function_steps = function_steps

        @classmethod
        def create_get_file_instance(
            cls, remote_path: str, local_path: Optional[str]
        ) -> "RuntimeTask._TaskStep":
            return cls(cls.TYPE_GET_FILE, local_path, remote_path)

        @classmethod
        def create_send_file_instance(
            cls, local_path: str, remote_path: Optional[str] = None
        ) -> "RuntimeTask._TaskStep":
            return cls(cls.TYPE_SEND_FILE, local_path, remote_path)

        @classmethod
        def create_run_command_instance(cls, command: str) -> "RuntimeTask._TaskStep":
            return cls(cls.TYPE_RUN_COMMAND, command=command)

        @classmethod
        def create_run_function_instance(
            cls,
            steps: list,
            function: Callable[..., Any],
            func_kwargs: Optional[dict] = None,
        ) -> "RuntimeTask._TaskStep":
            kwargs = func_kwargs or {}
            return cls(
                cls.TYPE_RUN_FUNCTION,
                function_steps=steps,
                function=function,
                func_kwargs=kwargs,
            )

        def __repr__(self) -> str:
            return "%s(%r)" % (self.__class__, self.__dict__)


class Runtime(object):
    """A `Runtime` is the logical representation of a remote host.

    Typically, the host is another server or a virtual
    machine / container on another server. This python class provides several methods for utilizing remote resources
    such as the port exposure from / to a `Runtime` as well as the execution of `RuntimeTasks`. A `Runtime` has a
    working directory. Usually, the execution of a `RuntimeTask` is conducted relatively to this directory if no other
    path is explicitly given. The working directory can be manually set during the initialization. Otherwise, a
    temporary directory gets created that might eventually be removed.

    A Runtime has a working directory (property: `working_dir`) which is a temporary directory per default and gets
    deleted `atexit` in this case. If you set this directory manually, either via `__init__()` or via the property
    `working_dir` then it won't be removed. Moreover, the working directory will also be set as environment variable on
    the Runtime. It is accessible via the env variable name stated in the constant `Runtime.WORKING_DIR_ENV_VAR_NAME`.
    This might be especially of interest when executing python functions remotely.

    Note:
        [Passwordless SSH access](https://linuxize.com/post/how-to-setup-passwordless-ssh-login/) should be be setup in
        advance. Otherwise the connection kwargs of fabric must be used for setting up the ssh connection.

    Examples:
        ```python
        # Execute a RuntimeTask synchronously
        Runtime('host-1').execute_task(my_task, execute_async=False)
        # Expose a port from localhost to the remote host so that a service running on localhost
        # is accessible from the remote host as well.
        Runtime('host-1').expose_port_to_runtime(8786)
        # Expose a port from a remote `Runtime` to localhost so that a service running on the `Runtime`
        # is accessible from localhost as well.
        Runtime('host-1').expose_port_from_runtime(8787)
        ```
    """

    # The working directory will be set as environment variable with this env variable name
    WORKING_DIR_ENV_VAR_NAME = "WORKING_DIR"
    LOCALHOST = "localhost"

    # Constants used for generating process keys
    _PORT_TO_RUNTIME = "-R"
    _PORT_FROM_RUNTIME = "-L"
    _PROCESS_KEY_DELIMITER = "::"
    _TASK_PROCESS_KEY_PREFIX = "task"

    def __init__(
        self,
        host: str,
        working_dir: Optional[str] = None,
        connection_kwargs: Optional[Dict] = None,
    ):
        """Initialization method.

        Note:
            The working directory will also be set as environment variable (see `Runtime.env_variables`) on the Runtime.
            It is accessible via the env variable name stated in the constant `Runtime.WORKING_DIR_ENV_VAR_NAME`. This
            might be especially of interest when executing functions remotely.

        Args:
            host: The host of the `Runtime`.
            working_dir: The directory which shall act as working directory. If set, then the full path will be created
                         on the remote host in case it does not exist. All individual Steps of a `RuntimeTask` will be
                         executed relatively to this directory. Defaults to None. Consequently, a temporary directory
                         will be created and used as working dir. If the working directory is a temporary one it will be
                         cleaned up either `atexit` or when calling `cleanup()` manually.

            connection_kwargs: kwargs that will be passed on to the fabric connection. Please check the fabric docs
                                 for further details.

        Raises:
            InvalidRuntimeError: If `is_valid_runtime()` check fails.
            PathCreationError: If the `working_dir` path could not be created successfully.
        """

        # Create the Logger
        self.log = logging.getLogger(__name__)

        # All attributes that need to be present before executing the valid Runtime check must be put here !!!!!
        self._host = host
        self._connection_kwargs = connection_kwargs
        self._env_variables: Dict[
            str, str
        ] = (
            {}
        )  # Will be passed on to fabric connect, so that they are available on the remote host

        # This check relies on some attributes, which must be declared above
        if not self.is_valid_runtime():
            raise InvalidRuntimeError(host)

        self._working_dir_is_temp = (
            False  # Indicates that a temp directory acts as working directory
        )
        self._working_dir: Optional[str] = None
        if working_dir:
            self.working_dir = working_dir  # raises PathCreationError

        self._processes: Dict[
            str, Process
        ] = (
            {}
        )  # The dict key is a generated process identifier and the value contains the process
        self._info: Dict[str, Union[str, List[str]]] = {}
        self._process_manager = Manager()
        self._tasks: List[RuntimeTask] = []

        # Cleanup will be done atexit since usage of destructor may lead to exceptions
        atexit.register(self.cleanup)

        self.log.debug(f"Runtime {self.host} initialized.")

    def __repr__(self) -> str:
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __str__(self) -> str:
        return self.class_name + ": " + self.host

    @property
    def working_dir(self) -> str:
        """The path of the working directory that was set during object initialization.

        Note:
            The working directory will also be set as environment variable on the Runtime. It is accessible via the
            env variable name stated in the constant `Runtime.WORKING_DIR_ENV_VAR_NAME`. This might be especially of
            interest when executing python functions remotely.
            Moreover, The full path will be created on the remote host in case it does not exist.

        Returns:
            str: The path of the working directory.
        """
        self._create_working_dir_if_not_exists()
        return self._working_dir  # type: ignore

    @working_dir.setter
    def working_dir(self, working_dir: str) -> None:
        """Setter of the working directory. This will also update the related env variable.

        Note:
            The full path will be created on the remote host in case it does not exist.

        Args:
            working_dir: The full path to the working directory.

        Raises:
            PathCreationError: If the working_dir path could not be created successfully.
        """
        self.create_dir(working_dir)  # raises PathCreationError
        self._working_dir = working_dir
        self._working_dir_is_temp = False
        self._env_variables.update({self.WORKING_DIR_ENV_VAR_NAME: self._working_dir})
        self.log.debug(
            f"The working directory  `{self._working_dir}` of Runtime {self.host} was set as environment "
            f"variable with the name {self.WORKING_DIR_ENV_VAR_NAME}."
        )

    @property
    def task_processes(self) -> List[Process]:
        """All processes that were started to execute a `RuntimeTask` asynchronously.

        Returns:
            List[Process]: RuntimeTask processes.
        """
        processes = []
        for process_key, process in self._processes.items():
            if self.is_runtime_task_process(process_key):
                processes.append(process)
        return processes

    @property
    def function_returns(self) -> Generator[object, None, None]:
        """Return data of remote executed functions.

        The return data produced by Python functions which were executed as a consequence
        of `task.run_function()`. The call will be passed on to the `function_returns`
        property of the `RuntimeTask`. The order is determined by the order in which the
        `RuntimeTasks` were executed in the `Runtime`.

        Yields:
            Generator[object, None, None]: Generator object yielding the return data of the functions executed during
                                           task execution.
        """
        self.log.debug(f"Start generating function returns for Runtime {self.host}.")
        for task in self._tasks:
            for function_return in task.function_returns:
                yield function_return

    @property
    def host(self) -> str:
        """The host of the runtime.

        Returns:
            str:  The host of the runtime.
        """
        return self._host

    @property
    def info(self) -> dict:
        """Information about the runtime.

        Returns:
            dict: Runtime information.
        """
        if not self._info:
            self._info = self._read_info()
        return self._info

    @property
    def os(self) -> str:
        """Operating system information.

        Returns:
            str: OS.
        """
        if not self._info:
            self._info = self._read_info()
        if not isinstance(self._info["os"], str):
            raise LazyclusterError("Runtime._info['os'] must be of type str")
        return self._info["os"]

    @property
    def cpu_cores(self) -> int:
        """Information about the available CPUs.

        If you are in a container the CPU quota will be given if set. Otherwise, the number of physical CPUs
        on the host machine is given.

        Raises:
            LazyclusterError: Data could not be read succesfully.

        Returns:
            int: Number of CPU cores
        """
        if not self._info:
            self._info = self._read_info()
        if not isinstance(self._info["cpu_cores"], str):
            raise LazyclusterError("Runtime._info['cpu_cores'] must be of type str")
        return int(self._info["cpu_cores"])

    @property
    def memory(self) -> int:
        """Information about the total memory in bytes.

        Returns:
            str: Total memory in bytes.
        """
        if not self._info:
            self._info = self._read_info()
        if not isinstance(self._info["memory"], str):
            raise LazyclusterError("Runtime._info['memory'] must be of type str")
        return int(self._info["memory"])

    @property
    def memory_in_mb(self) -> int:
        """Memory information in mb.

        Returns:
            int: Total memory in mega bytes.
        """
        return int(self.memory / 1024 / 1024)

    @property
    def python_version(self) -> str:
        """The installed python version.

        Returns:
            str: Python version.
        """
        if not self._info:
            self._info = self._read_info()
        if not isinstance(self._info["python_version"], str):
            raise LazyclusterError(
                "Runtime._info['python_version'] must be of type str"
            )
        return self._info["python_version"]

    @property
    def gpus(self) -> List[str]:
        """GPU information as list. Each list entry contains information for one GPU.

        Returns:
            list: List with GPU information.
        """
        if not self._info:
            self._info = self._read_info()
        if not isinstance(self._info["gpus"], list):
            raise LazyclusterError("Runtime._info['gpus'] must be of type List")
        return self._info["gpus"]

    @property
    def gpu_count(self) -> int:
        """The count of GPUs.

        Returns:
            int: The number of GPUs
        """
        return len(self.gpus)

    @property
    def class_name(self) -> str:
        """Getter for the class name as string.

        Returns:
            str: Class name.
        """
        return self.__class__.__name__

    @property
    def alive_process_count(self) -> int:
        """The number of alive processes.

        Returns:
            int: The count.
        """
        return len(self.get_processes(only_alive=True))

    @property
    def alive_task_process_count(self) -> int:
        """The number of alive processes which were started to execute a `RuntimeTask`.

        Returns:
            int: The count.
        """
        return len(self.task_processes)

    @property
    def env_variables(self) -> Dict[str, str]:
        """The environment variables for the Runtime.

        These variables are accessible on the Runtime and can be used
        when executing Python functions or shell commands.

        Note:
            The working directory is always accessible as environment variable on the Runtime. The respective variable
            name is given by the value of the constant `self.WORKING_DIR_ENV_VAR_NAME`.
        """
        return self._env_variables

    @env_variables.setter
    def env_variables(self, env_variables: Dict[str, str]) -> None:
        """Setter for the environment variables.

        Args:
            env_variables: The new env var dictionary.
        """
        self._env_variables = env_variables
        if self.WORKING_DIR_ENV_VAR_NAME not in self._env_variables:

            assert self._working_dir, "Workind directory must not be empty here"

            self._env_variables.update(
                {self.WORKING_DIR_ENV_VAR_NAME: self._working_dir}
            )

    def add_env_variables(self, env_variables: Dict) -> None:
        """Update the environment variables. If a variable already exists it gets updated and if not it will be added.

        Args:
            env_variables: The env variables used for the update.
        """
        self._env_variables.update(env_variables)

    @classmethod
    def is_runtime_task_process(cls, process_key: str) -> bool:
        """Check if the process manages the `RuntimeTask` execution.

        Checks if the process which belongs to a given `process_key` was started to execute a `RuntimeTask` based on
        an internal naming scheme of the process keys.

        Args:
            process_key: The generated process identifier.

        Returns:
            bool: True, if process was started to execute a `RuntimeTask`
        """
        key_splits = process_key.split(cls._PROCESS_KEY_DELIMITER)
        return key_splits[1] == cls._TASK_PROCESS_KEY_PREFIX

    @classmethod
    def is_port_exposure_process(cls, process_key: str) -> bool:
        """Check if the process manages a port exposure.

        Check if the process which belongs to the given `process_key` is used for exposing a port, i.e. keeping
        an ssh tunnel alive.

        Args:
            process_key (str): The generated process identifier.

        Returns:
            bool: True, if process is used for port exposure.
        """
        key_splits = process_key.split(cls._PROCESS_KEY_DELIMITER)
        return (
            True
            if key_splits[1] == cls._PORT_FROM_RUNTIME
            or key_splits[1] == cls._PORT_TO_RUNTIME
            else False
        )

    def is_valid_runtime(self) -> bool:
        """Checks if a given host is a valid `Runtime`.

        Returns:
            bool: True, if it is a valid remote runtime.
        """
        self.log.debug(f"Start executing `is_valid_runtime()` on Runtime {self.host}")

        # Paramiko is only used by fabric and thus not needed in our project requirements
        from paramiko.ssh_exception import NoValidConnectionsError, SSHException

        try:
            # use a relatively high timeout to prevent errors when sshing with slow network connections
            cxn = Connection(
                host=self.host,
                connect_kwargs=self._connection_kwargs,
                inline_ssh_env=True,
                connect_timeout=2,
            )
            stdout = cxn.run(
                "python3 --version",
                env=self._env_variables,
                warn=False,
                hide=True,
                pty=True,
                timeout=10,
            ).stdout
        except NoValidConnectionsError:
            self.log.debug(f"No valid ssh connection to host {self.host}.")
            return False
        except SSHException:
            self.log.debug(
                f"connection.run() threw a SSHException during is_valid_runtime of host {self.host}."
            )
            return False
        except ValueError:
            self.log.debug(
                f"connection.run() threw a ValueError during is_valid_runtime of host {self.host}."
            )
            return False

        stdout = stdout.replace("\n", "").replace("\r", "")
        self.log.debug(
            f"stdout of python version check on host {self.host} is `{stdout}`."
        )

        if not stdout:
            return False

        # Example: `Python 3.6.8 :: Anaconda, Inc.`
        python_version = stdout.split()[1].split(".")

        if not python_version:
            return False
        elif int(python_version[0]) > 3:  # Stay future-proof?
            self.log.warning(
                "The lib was originally created for Python 3.6 and is not yet tested for "
                "Python >= Python 4"
            )
            return True
        elif int(python_version[0]) == 3 and int(python_version[1]) >= 6:
            return True
        else:
            return False

    def get_free_port(self, ports: List[int]) -> int:
        """Returns the first port from the list which is currently not in use in the `Runtime`.

        Args:
             ports: The list of ports that will be used to check if the port is currently in use.

        Returns:
            int: The first port from the list which is not yet used within the whole group.

        Raises:
            NoPortsLeftError: If the port list is empty and no free port was found yet.
        """
        for port in ports:
            if self.has_free_port(port):
                return port

        raise NoPortsLeftError()

    def execute_task(
        self,
        task: RuntimeTask,
        execute_async: Optional[bool] = True,
        omit_on_join: bool = False,
        debug: bool = False,
    ) -> None:
        """Execute a given `RuntimeTask` in the `Runtime`.

        Note:
            Each execution will initialize the execution log of the `RuntimeTask`.

        Args:
            task: The RuntimeTask to be executed.
            execute_async: The execution will be done in a separate process if True. Defaults to True.
            omit_on_join: If True, then a call to join() won't wait for the termination of the corresponding process.
                          Defaults to False. This parameter has no effect in case of synchronous execution.
            debug : If `True`, stdout/stderr from the remote host will be printed to stdout. If, `False`
                    then the stdout/stderr will be written to execution log files. Defaults to `False`.

        Raises:
            TaskExecutionError: If an executed task step can't be executed successfully.
        """
        self._create_working_dir_if_not_exists()
        async_str = " asynchronously " if execute_async else " synchronously "
        self.log.info(f"Start executing task {task.name} {async_str} on {self.host}")

        # Pass env parameters on to the RuntimeTask
        task.env_variables = self._env_variables

        # Wrapper needed to ensure execution from the Runtime's working directory
        def execute_remote_wrapper() -> None:
            cxn = self._fabric_connection
            with cxn.cd(self._working_dir):
                task.execute(cxn, debug=debug)

        if execute_async:
            # Initialize logs with managed list (multiprocessing)
            # => We can access the logs although it is executed in another process
            task._execution_log = self._process_manager.list()
            task.omit_on_join = omit_on_join
            process = Process(target=execute_remote_wrapper)
            process.start()
            self._processes.update(
                {self._create_process_key_for_task_execution(task): process}
            )
            task._process = process
        else:
            task._execution_log = []
            execute_remote_wrapper()

        self._tasks.append(task)

    def send_file(
        self,
        local_path: str,
        remote_path: Optional[str] = None,
        execute_async: Optional[bool] = False,
    ) -> "RuntimeTask":
        """Send either a single file or a folder from the manager to the Runtime.

        Note:
            This method is a convenient wrapper around the RuntimeTask's send file functionality. But it directly
            executes the file transfer in contrast to the send_file() method of the RuntimeTask.

        Args:
            local_path: Path to file on local machine.
            remote_path: Path on the Runtime. Defaults to the self.working_dir. See
                         `RuntimeTask.execute()` docs for further details.
            execute_async: The execution will be done in a separate process if True. Defaults to False.

        Returns:
            RuntimeTask: The task that were internally created for the file transfer.

        Raises:
            ValueError: If local_path is emtpy.
            TaskExecutionError: If an executed task step can't be executed successfully.
            OSError: In case of non existent paths.e
        """
        async_str = " asynchronously " if execute_async else " synchronously "
        self.log.debug(
            f"Start sending local file `{local_path}` to Runtime {self.host} {async_str}. Given remote path:"
            f" {remote_path}`."
        )
        task = RuntimeTask(f"send-file-{local_path}-to-{self.host}")
        task.send_file(local_path, remote_path)
        self.execute_task(task, execute_async)
        return task

    def get_file(
        self,
        remote_path: str,
        local_path: Optional[str] = None,
        execute_async: Optional[bool] = False,
    ) -> "RuntimeTask":
        """Get either a single file or a folder from the Runtime to the manager.

        Note:
            This method is a convenient wrapper around the RuntimeTask's get file functionality. But it directly
            executes the file transfer in contrast to the get_file() method of the RuntimeTask.

        Args:
            remote_path: Path to file on host.
            local_path: Path to file on local machine (i.e. manager). The remote file is downloaded  to the current
                        working directory (as seen by os.getcwd) using its remote filename if local_path is None.
                        This is the default behavior of fabric.Connection.get().
            execute_async: The execution will be done in a separate process if True. Defaults to False.

        Returns:
            RuntimeTask: self.

        Raises:
            ValueError: If remote path is emtpy.
        """
        async_str = " asynchronously " if execute_async else " synchronously "
        self.log.debug(
            f"Start transferring the file `{remote_path}` of Runtime {self.host} {async_str} to local path:"
            f" {local_path}`."
        )
        task = RuntimeTask(f"get-file-{remote_path}-from-{self.host}")
        task.get_file(remote_path, local_path)
        self.execute_task(task, execute_async)
        return task

    def execute_function(
        self,
        function: Callable[..., Any],
        execute_async: bool = False,
        debug: bool = False,
        **func_kwargs: Any,
    ) -> "RuntimeTask":
        """Execute a Python function on the Runtime.

        Note:
            Internally, creates a RuntimeTask for executing the given python function on a remote host. The function
            will be transferred to the remote host via ssh and cloudpickle. The return data can be requested via the
            property `function_returns` of the Runtime or of the returned RuntimeTask. Hence, the function must be
            serializable via cloudpickle and all dependencies must be available in its correct versions on the Runtime.

        Args:
            function: The function to be executed remotely.
            execute_async: The execution will be done in a separate process if True. Defaults to False.
            debug : If `True`, stdout/stderr from the remote host will be printed to stdout. If, `False`
                    then the stdout/stderr will be written to execution log files. Defaults to `False`.
            **func_kwargs: kwargs which will be passed to the function.

        Returns:
            RuntimeTask: self.

        Raises:
            ValueError: If function is empty.
            TaskExecutionError: If there was an error during the execution.
        """
        task = RuntimeTask(f"execute-function-{function.__name__}").run_function(
            function, **func_kwargs
        )
        self.execute_task(task, execute_async, debug)
        return task

    def _create_working_dir_if_not_exists(self) -> None:
        if not self._working_dir:
            working_dir = self.create_tempdir()
            self._working_dir_is_temp = True
            self.log.debug(
                f"Temporary directory {working_dir} created as working directory on Runtime "
                f"{self._host}"
            )
            self.working_dir = (
                working_dir  # This will call the setter of self._working_dir
            )
        if not self._working_dir:
            raise LazyclusterError("Working Directory could not be created")

    def print_log(self) -> None:
        """Print the execution logs of each `RuntimeTask` that was executed in the `Runtime`."""
        for task in self._tasks:
            task.print_log()

    def execution_log(self, task_name: str) -> List[str]:
        """Get the execution log of a `RuntimeTask` which was executed in the Runtime.

        Args:
            task_name (str): The name of the `RuntimeTask`

        Raises:
            ValueError: The RuntimeTask `task_name` was not executed on the Runtime

        Returns:
            List[str]: Execution log
        """
        for task in self._tasks:
            if task.name == task_name:
                return task.execution_log
        raise ValueError(
            f"The RuntimeTask {task_name} was not executed on Runtime {self.host}"
        )

    def clear_tasks(self) -> None:
        """Clears all internal state related to `RuntimeTasks`."""
        self.log.info(
            f"Clear all RuntimeTasks and kill related processes on Runtime {self.host}"
        )
        self._tasks = []
        self._processes = {
            key: value
            for key, value in self._processes.items()
            if not Runtime.is_runtime_task_process(key)
        }

    def expose_port_to_runtime(
        self, local_port: int, runtime_port: Optional[int] = None
    ) -> str:
        """Espose a port to a `Runtime`.

        Expose a port from localhost to the `Runtime` so that all traffic on the `runtime_port` is forwarded to the
        `local_port` on localhost.

        Args:
            local_port: The port on the local machine.
            runtime_port: The port on the runtime. Defaults to `local_port`.

        Returns:
            str: Process key, which can be used for manually stopping the process running the port exposure for example.
        """
        if not runtime_port:
            runtime_port = local_port
        if local_port == runtime_port and self._host == self.LOCALHOST:
            # We can not forward a port to itself!
            self.log.debug(
                f"Port ({str(local_port)}) exposure skipped on Runtime {self.host}. Can't expose a port to "
                f"myself."
            )
            return ""
        elif not self.has_free_port(runtime_port):
            raise PortInUseError(runtime_port, runtime=self)

        proc = Process(
            target=self._forward_runtime_port_to_local,
            kwargs={"local_port": local_port, "runtime_port": runtime_port},
        )
        proc.start()
        key = self._create_process_key_for_port_exposure(
            self._PORT_TO_RUNTIME, local_port, runtime_port
        )
        self._processes.update({key: proc})
        time.sleep(0.1)  # Necessary to prevent collisions with MaxStartup restrictions
        self.log.info(
            f"Local port {str(local_port)} exposed to Runtime {self._host} on port {str(runtime_port)}"
        )
        return key

    def expose_port_from_runtime(
        self, runtime_port: int, local_port: Optional[int] = None
    ) -> str:
        """Expose a port from a `Runtime`.

        Expose a port from a `Runtime` to localhost so that all traffic to the `local_port` is forwarded to the
        `runtime_port` of the `Runtime`. This corresponds to local port forwarding in ssh tunneling terms.

        Args:
            runtime_port: The port on the runtime.
            local_port: The port on the local machine. Defaults to `runtime_port`.

        Returns:
            str: Process key, which can be used for manually stopping the process running the port exposure.
        """
        if not local_port:
            local_port = runtime_port
        if local_port == runtime_port and self._host == self.LOCALHOST:
            # We can not forward a port to itself!
            self.log.debug(
                f"Port ({str(local_port)}) exposure skipped on Runtime {self.host}. Can't expose a port to "
                f"myself."
            )
            return ""
        elif not _utils.localhost_has_free_port(local_port):
            raise PortInUseError(runtime_port, runtime=self)

        proc = Process(
            target=self._forward_local_port_to_runtime,
            kwargs={"local_port": local_port, "runtime_port": runtime_port},
        )
        proc.start()
        key = self._create_process_key_for_port_exposure(
            self._PORT_FROM_RUNTIME, local_port, runtime_port
        )
        self._processes.update({key: proc})
        time.sleep(0.1)  # Necessary to prevent collisions with MaxStartup restrictions
        self.log.info(
            f"Port {str(runtime_port)} from runtime {self._host} exposed to local port {str(local_port)}"
        )
        return key

    def get_process(self, key: str) -> Process:
        """Get an individual process by process key.

        Args:
            key: The key identifying the process.

        Returns:
            Process: The desired process.

        Raises:
            ValueError: Unknown process key.
        """
        if key not in self._processes:
            raise ValueError("Unknown process key.")
        return self._processes[key]

    def get_processes(self, only_alive: bool = False) -> Dict[str, Process]:
        """Get all managed processes or only the alive ones as dictionary with the process key as dict key.

        An individual process can be retrieved by key via `get_process()`.

        Args:
            only_alive: True, if only alive processes shall be returned instead of all. Defaults to False.

        Returns:
            Dict[str, Process]: Dictionary with process keys as dict keys and the respective processes as dict values.

        """
        if only_alive:

            ret_processes = {}

            for key, process in self._processes.items():
                if process.is_alive():
                    ret_processes.update({key: process})
            return ret_processes

        else:
            return self._processes

    def stop_process(self, key: str) -> None:
        """Stop a process by its key.

        Args:
            key: The key identifying the process.

        Raises:
            ValueError: Unknown process key.
        """
        if key not in self._processes:
            raise ValueError("Unknown process key.")
        self._processes[key].terminate()
        self.log.debug(f"Process with key {key} stopped in Runtime {self.host}")

    def has_free_port(self, port: int) -> bool:
        """Checks if the port is available on the runtime.

        Args:
            port: The port which will be checked.

        Returns:
            bool: True if port is free, else False.
        """
        self.log.debug(f"Checking if port {str(port)} is free on Runtime {self.host}")

        with self._fabric_connection as cxn:
            cmd_str = (
                "python -c \"import socket;print('free') "
                "if socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(('localhost', "
                + str(port)
                + ')) else None"'
            )
            res = cxn.run(cmd_str, hide=True)
            return True if res.stdout else False

    def print_info(self) -> None:
        """Print the Runtime info formatted as table."""
        info = self.info
        print(
            "\u001b[1mInformation of `"
            + self.class_name
            + "` "
            + self.host
            + ":\u001b[0m"
        )
        for key, value in info.items():

            if key == "memory":
                display_value = str(self.memory_in_mb) + " mb"
            elif isinstance(value, list):
                display_value = ""
                for gpu in value:
                    display_value = "{}".format(gpu)
            else:
                display_value = value

            print("{:<8} {:<8}".format(key, display_value))

    def check_filter(
        self,
        gpu_required: bool = False,
        min_memory: Optional[int] = None,
        min_cpu_cores: Optional[int] = None,
        installed_executables: Union[str, List[str], None] = None,
        filter_commands: Union[str, List[str], None] = None,
    ) -> bool:
        """Checks the `Runtime` object for certain filter criteria.

        Args:
            gpu_required: True, if gpu availability is required. Defaults to False.
            min_memory: The minimal amount of memory in MB. Defaults to None, i.e. not restricted.
            min_cpu_cores: The minimum number of cpu cores required. Defaults to None, i.e. not restricted.
            installed_executables: Possibility to check if an executable is installed. E.g. if the executable `ping` is
                                   installed.
            filter_commands: Shell commands that can be used for generic filtering. See examples. A filter command must
                             echo true to be evaluated to True, everything else will be interpreted as False. Defaults
                             to None.

        Returns:
            bool: True, if all filters were successfully checked otherwise False.

        Examples:
            ```python
            # Check if the `Runtime` has a specific executable installed
            # such as `ping` the network administration software utility.
            check_passed = runtime.check_filter(installed_executables='ping')
            # Check if a variable `WORKSPACE_VERSION` is set on the `Runtime`
            filter_str = '[ ! -z "$WORKSPACE_VERSION" ] && echo "true" || echo "false"'
            check_passed = runtime.check_filter(filer_commands=filter_str)
            ```
        """
        self.log.debug(f"Start executing check_filter() for Runtime {self.host}")

        all_filters_checked = True

        if gpu_required and not self.gpus:
            self.log.debug(f"Runtime  {self.host} does not have GPUs.")
            all_filters_checked = False

        if min_memory and self.memory_in_mb < min_memory:
            self.log.debug(
                f"Runtime {self.host} has only {str(self.memory_in_mb)} mb instead of {str(min_memory)} as required."
            )
            all_filters_checked = False

        if min_cpu_cores and self.cpu_cores < min_cpu_cores:
            self.log.debug(
                f"Runtime {self.host} has only {str(self.cpu_cores)} instead of {str(min_cpu_cores)} as required."
            )
            all_filters_checked = False

        if installed_executables:
            for executable_name in _utils.create_list_from_parameter_value(
                installed_executables
            ):
                if not self._has_executable_installed(str(executable_name)):
                    self.log.debug(
                        f"Runtime {self.host} does not have executable {str(executable_name)} installed."
                    )
                    all_filters_checked = False

        if filter_commands:
            for filter_command in _utils.create_list_from_parameter_value(
                filter_commands
            ):
                if not self._filter_command_checked(str(filter_command)):
                    self.log.debug(
                        f"Filter filter_commands could not be checked successfully on Runtime"
                        f" {self.host}."
                    )
                    all_filters_checked = False

        return all_filters_checked

    def create_tempdir(self) -> str:
        """Create a temporary directory and return its name/path.

        Returns:
            str: The name/path of the directory.
        """
        with self._fabric_connection as cxn:
            cmd_str = 'python -c "import tempfile; print(tempfile.mkdtemp())"'
            res = cxn.run(cmd_str, hide=True)
            path = res.stdout.split("\n")[0]
            if not path:
                path = res.stdout
            self.log.debug(f"Temporary directory {path} created on Runtime {self.host}")
            return path

    def create_dir(self, path: str) -> None:
        """Create a directory. All folders in the path will be created if not existing.

        Args:
            path: The full path of the directory to be created.

        Raises:
            PathCreationError: If the path could not be created successfully.
        """
        try:
            with self._fabric_connection as cxn:
                cmd_str = "mkdir -p " + path
                res = cxn.run(cmd_str, hide=True)
                if res.stderr:
                    raise PathCreationError(path, self.host)
                else:
                    self.log.debug(f"Directory {path} created on Runtime {self.host}")
        except Exception:
            raise PathCreationError(path, self.host)

    def delete_dir(self, path: str) -> bool:
        """Delete a directory recursively. If at least one contained file could not be removed then False is returned.

        Args:
            path: The full path of the directory to be deleted.

        Returns:
            bool: True if the directory could be deleted successfully.
        """
        from invoke.exceptions import ThreadException

        with self._fabric_connection as cxn:
            cmd_str = f"rm -r {path} 2> /dev/null"

            try:
                res = cxn.run(cmd_str, warn=True)
            except ThreadException:
                self.log.warning(
                    f"ThreadException occured when deleting the directory {path}"
                )
                return True

            if res.ok:
                self.log.debug(f"Directory {path} deleted from Runtime {self.host}")
                return True
            else:
                self.log.debug(
                    f"Directory {path} may not be deleted on Runtime {self.host}"
                )
                return False

    def join(self) -> None:
        """Blocks until `RuntimeTasks` which were started via the `runtime.execute_task()` method terminated."""
        self.log.info(
            f"Joining all processes executing a RuntimeTask that were started via the Runtime {self.host}"
        )
        for task in self._tasks:
            task.join()

    def cleanup(self) -> None:
        """Release all acquired resources and terminate all processes."""
        self.log.info(f"Start cleanup of Runtime {self.host}.")
        for key, process in self._processes.items():
            process.terminate()
            process.join()
            if process.is_alive():
                self.log.warning(f"Process with key {key} could not be terminated")
            else:
                self.log.debug(f"Process with key {key} terminated")
        if self._working_dir_is_temp and self._working_dir:
            success = self.delete_dir(self._working_dir)
            if success:
                self.log.debug(
                    f"Temporary directory {self.working_dir} of Runtime {self.host} removed."
                )
                self._working_dir = None
                self._working_dir_is_temp = False
            else:
                self.log.warning(
                    f"Temporary directory {self.working_dir} of Runtime {self.host} could not be"
                    f" removed."
                )

        for task in self._tasks:
            task.cleanup()

    def echo(self, msg: str) -> str:
        """Convenient method for echoing a string on the `Runtime` and returning the result."""
        cxn = self._fabric_connection
        with cxn.cd(self.working_dir):
            return cxn.run(f"echo {msg}", env=self._env_variables, hide=True).stdout

    # - Private methods -#

    def _create_process_key_for_port_exposure(
        self, direction: str, local_port: int, runtime_port: int
    ) -> str:
        """Create a process key for processes exposing ports, i.e. keeping ssh tunnels open.

        This key will act as an identifier for internally generated processes.

        Args:
            direction (str): [description]
            local_port (int): [description]
            runtime_port (int): [description]

        Raises:
            ValueError: If direction has an invalid value.

        Returns:
            str: Generated key.
        """
        if not local_port:
            local_port = runtime_port
        if not runtime_port:
            runtime_port = local_port

        delimiter = self._PROCESS_KEY_DELIMITER

        if direction == self._PORT_FROM_RUNTIME:
            return (
                self.host
                + delimiter
                + self._PORT_FROM_RUNTIME
                + delimiter
                + str(local_port)
                + delimiter
                + str(runtime_port)
            )
        elif direction == self._PORT_TO_RUNTIME:
            return (
                self.host
                + delimiter
                + self._PORT_TO_RUNTIME
                + delimiter
                + str(runtime_port)
                + delimiter
                + str(local_port)
            )
        else:
            raise ValueError(
                direction + " is not a supported runtime process prefix type"
            )

    def _create_process_key_for_task_execution(self, task: RuntimeTask) -> str:
        """Generate keys used to identify subprocesses.

        Create a process key for processes started to execute a `RuntimeTasks` asynchronously
        This key will act as an identifier for internally generated processes.

        Args:
            task (RuntimeTask): The task that will be scanned for processes.

        Returns:
            str: Generated key.
        """
        return (
            self.host
            + self._PROCESS_KEY_DELIMITER
            + self._TASK_PROCESS_KEY_PREFIX
            + self._PROCESS_KEY_DELIMITER
            + str(task.name)
        )

    @classmethod
    def _create_executable_installed_shell_cmd(cls, executable: str) -> str:
        return "hash " + executable + ' 2>/dev/null && echo "true" || echo ""'

    def _has_executable_installed(self, executable_name: str) -> bool:
        """Checks if an executable is installed on the runtime."""
        shell_cmd = self._create_executable_installed_shell_cmd(executable_name)
        return self._filter_command_checked(shell_cmd)

    def _filter_command_checked(self, shell_cmd: str) -> bool:
        task = RuntimeTask("_filter_command_checked")
        task.run_command(shell_cmd)
        self.execute_task(task, execute_async=False)

        # Check the last log entry for the string true
        result = str(task.execution_log[len(task.execution_log) - 1])
        return True if result.lower() == "true" else False

    @property
    def _fabric_connection(self) -> Connection:
        """Get a new fabric connection to the runtime.

        Note: We set the `fabric.Connection` parameter `inline_ssh_env=True`.

        Raises:
            ValueError: If user or port values are given via both host shorthand
                        and their own arguments.
        """
        from socket import gaierror

        try:
            self.log.debug(
                f"Create new fabric connection to host {self.host} via _fabric_connection."
            )
            return Connection(
                host=self.host,
                connect_kwargs=self._connection_kwargs,
                inline_ssh_env=True,
            )
        except gaierror:
            raise ValueError("Cannot establish SSH connection to host " + self.host)

    def _forward_local_port_to_runtime(
        self, local_port: int, runtime_port: Optional[int] = None
    ) -> None:
        """Setup port forwarding.

        Creates ssh connection to the runtime and creates then a ssh tunnel
        from `localhost`:`local_port to `runtime`:`runtime_port`.

        Args:
            local_port (int): The local port to be forwarded.
            runtime_port (Optional[int], optional): The target port on the `Runimte`. Defaults to None.
        """
        if not runtime_port:
            runtime_port = local_port

        with self._fabric_connection.forward_local(local_port, runtime_port):
            while True:
                time.sleep(1000)

    def _forward_runtime_port_to_local(
        self, runtime_port: int, local_port: Optional[int] = None
    ) -> None:
        """Setup port forwarding.

        Creates ssh connection to the runtime and then creates a ssh tunnel
        from `runtime`:`runtime_port` to `localhost`:`local_port`.

        Args:
            runtime_port (int): The port on the `runtime`.
            local_port (Optional[int], optional): The target port on localhost. Defaults to None.
        """
        if not local_port:
            local_port = runtime_port

        with self._fabric_connection.forward_remote(runtime_port, local_port):
            while True:
                time.sleep(1000)

    def _read_info(self) -> Dict[str, Union[str, List[str]]]:
        """Read the host machine information."""
        self.log.debug(f"Read Runtime information of Runtime {self.host}")
        return _utils.read_host_info(self.host)
