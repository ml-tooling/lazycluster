"""Runtimes module.

This module comprises classes for executing so called `RuntimeTasks` in `Runtimes` by leveraging the power of ssh.
The `RuntimeTask` class is a container for defining a sequence of elegantly task steps. This `RuntimeTask` can then be
executed either standalone of by passing it over to a `Runtime` instance. Passwordless ssh should be configured for all
hosts that should act as a `Runtime` to be able to conveniently manage those entities.

"""
import tempfile
import time

from fabric import Connection
from multiprocessing import Process, Manager
from typing import Optional, List, Dict, Generator, Union
import shutil
import cloudpickle as pickle
import atexit

import lazycluster.settings as settings

from lazycluster import InvalidRuntimeError, NoPortsLeftError, PortInUseError
import lazycluster._utils as _utils

import socket
import warnings

import json
import os
import psutil
import sys
import platform
import subprocess


class RuntimeTask(object):
    """This class provides the functionality for executing a sequence of elementary operations over ssh. The `fabric`
    library is used for handling ssh connections. A `RuntimeTask` can be composed from four different operations which
    we call steps, namely adding a step for running a shell command via `run_command()`, sending a file to a host via
    `send_file()`, retrieving a file from a host via `get_file()` or adding a step for executing a python function on a
    host via `run_function()`. The current restriction for running functions is that these functions need to be
    serializable via cloudpickle. To actually execute a `RuntimeTask`, i.e. the sequence of task steps, either a call
    to `execute()` is necessary or a handover to the `execute_task()` method of the `Runtime` class is necessary.
    Usually, a `RuntimeTask` will be executed in a `Runtime` or in a `RuntimeGroup`. See its documentation for further
    details.

    Examples:
        >>> # 1. Define a function that should be executed remotely via a RuntimeTask
        >>> def print():
        ...     print('Hello World!')

        >>> # 2. Create & compose the RuntimeTask by using the elementary operations
        >>> my_task = RuntimeTask('my-task').run_command('echo Hello World!').run_function(print)

        >>> # 3. Execute the RuntimeTask standalone w/o Runtime by handing over a fabric ssh connection
        >>> from fabric import Connection
        >>> task = my_task.execute(Connection('host'))

        >>> # 4. Check the logs of the RuntimeTask execution
        >>> task.print_log()
        >>> log = task.execution_log
    """

    def __init__(self, name: Optional[str] = None):
        """Initialization method.
        
        Args:
            name (Optional[str]): The name of the task. Defaults to None and consequently a unique identifier is
                                  generated via Python's id() function.
        """
        self._name = name
        if not self._name:
            self._name = str(id(self))
        self._task_steps = []
        self._execution_log = []
        self._function_return_pkl_paths = []  # file paths to files with function's pickled return data
        self._requested_files = []

        self._process = None

        # Will be created if run_function is executed      
        self._temp_dir = None
        # Cleanup will be done atexit since usage of destructor may lead to exceptions
        atexit.register(self.cleanup)

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __str__(self):
        return type(self).__name__ + ': ' + self.name

    def cleanup(self):
        """Remove temporary used resources, like temporary directories if created."""
        if self._temp_dir:
            shutil.rmtree(self._temp_dir)
            print('Temporary directory ' + self._temp_dir + ' of RuntimeTask ' + self.name + ' on localhost removed.')

    @property
    def name(self) -> str:
        """Get the task name.
        
        Returns:
            str: Task name
        """
        return self._name

    @property
    def execution_log(self) -> List[str]:
        """Return the execution log as list. The list is empty as long as a task was not yet executed. Each log entry
        corresponds to a single task step and the log index starts at 0. If th execution of an individual step does not
        produce and outut the list entry will be empty.
        """
        return self._execution_log

    @property
    def function_returns(self) -> Generator[object, None, None]:
        """Get the return data produced by functions which were executed as a consequence of a `task.run_function()`
        call.

       Internally, a function return is saved as a pickled file. This method unpickles each file one after
       another and yields the data. Moreover, the return data will be yielded in the same order as the functions were
       executed.

        Yields:
            Generator[object, None, None]: Generator object yielding the return data of the functions executed during
                                           task execution.
        """
        if self.process:
            self.process.join()

        for return_pkl_path in self._function_return_pkl_paths:

            if not os.path.exists(return_pkl_path):
                warnings.warn('Pickle file ' + return_pkl_path + ' with function return data does not exist. '
                              'Please check the logs.')
                yield None
                continue

            with open(return_pkl_path, 'rb') as file:
                yield pickle.load(file)

    @property
    def process(self) -> Process:
        """Returns the process object in which the task were executed. None, if not yet or synchronously executed. """
        return self._process

    def send_file(self, local_path: str, remote_path: Optional[str] = None):
        """Create a task step for sending either a single file or a folder from localhost to another host.
        
        Args:
            local_path (str): Path to file on local machine.
            remote_path (Optional[str]): Path on the remote host. Defaults to the root directory.
        
        Raises:
            ValueError: If file locally not found.
        """
        if not local_path:
            raise ValueError("Invalid local path")

        if not remote_path:
            remote_path = local_path

        self._task_steps.append(self._TaskStep(self._TaskStep.TYPE_SEND_FILE, local_path=local_path,
                                               remote_path=remote_path))
        return self

    def get_file(self, remote_path: str, local_path: Optional[str] = None):
        """Create a task step for getting either a single file or a folder from another host to localhost.

        Args:
            remote_path (str): Path to file on host.
            local_path (Optional[str]): Path to file on local machine. The remote file is downloaded 
                                        to the current working directory (as seen by os.getcwd) using 
                                        its remote filename if local_path is None. This is the default
                                        behavior of fabric.
        Raises:
            ValueError: If remote path is emtpy.
        """
        if not remote_path:
            raise ValueError("Remote path must not be empty")

        self._task_steps.append(self._TaskStep(self._TaskStep.TYPE_GET_FILE, remote_path=remote_path,
                                               local_path=local_path))
        self._requested_files.append(local_path)
        return self

    def run_command(self, command: str):
        """Create a task step for running a given shell command. 

        Args:
            command (str): Shell command.

        Raises:
            ValueError: If command is emtpy.
        """
        if not command:
            raise ValueError("Command must not be emtpy")
        self._task_steps.append(self._TaskStep(self._TaskStep.TYPE_RUN_COMMAND, command=command))

        return self

    def run_function(self, function: callable, **func_kwargs):
        """Create a task step for executing a given python function on a remote host. The function will be transferred
        to the remote host via ssh and cloudpickle. The return data can be requested via the property `function_returns`

        Note:
            Hence, the function must be serializable via cloudpickle and all dependencies must be available in its
            correct versions on the remote host for now. We are planning to improve the dependency handling.

        Args:
            function (callable): The function to be executed remotely.
            **func_kwargs: kwargs which will be passed to the function.
        
        Raises:
            ValueError: If function is empty.
        """
        if not function:
            raise ValueError("Function is invalid.")

        # Create a temp directory for persisting the serialized function
        if not self._temp_dir:
            self._temp_dir = tempfile.mkdtemp()
            self.run_command('mkdir -p ' + self._temp_dir)
            print('Temporary directory ' + self._temp_dir + ' for task ' + self.name + ' on localhost created.')

        # We distinguish between local -  and remote paths because in case we execute a function in a
        # `Runtime.create_instance('localhost')`, we may overwrite the files.
        input_function_name = function.__name__
        remote_file_name = self._create_file_name(input_function_name)
        local_file_name = 'local_' + remote_file_name
        local_pickle_file_path = os.path.join(self._temp_dir, local_file_name)
        remote_pickle_file_path = os.path.join(self._temp_dir, remote_file_name)

        local_return_file_name = 'return_' + remote_file_name
        remote_return_file_name = 'remote_' + local_return_file_name
        local_return_pickle_file_path = os.path.join(self._temp_dir, local_return_file_name)
        remote_return_pickle_file_path = os.path.join(self._temp_dir, remote_return_file_name)

        # Hereby we can pickle the function incl. kwargs, since we are
        # going to pickle the wrapper and not only the function itself.
        def function_wrapper():

            result = function(**func_kwargs)

            # Make the function return data available
            # => pickle the data and save it as a file on the remote host so that we can get the file back to the
            # local machine. Local machine means NOT the one where `function_wrapper()` is actually executed, but
            # the one where `task.run_function()` is actually executed.
            with open(remote_return_pickle_file_path, 'wb') as fp:
                pickle.dump(result, fp)
                fp.close()

        # Create cloud pickle file of the function_wrapper() and save it locally
        with open(local_pickle_file_path, 'wb') as f:
            pickle.dump(function_wrapper, f)
            f.close()

        # Add `TaskStep` for sending the pickled function_wrapper file to the Runtime
        self.send_file(local_pickle_file_path, remote_pickle_file_path)

        # Ensure installation of cloudpickle 
        self.run_command('pip install -q cloudpickle')

        # Create commands for executing the pickled function file
        run_function_code = 'import cloudpickle as pickle; file=open(\'' + remote_pickle_file_path + '\', \'rb\'); ' \
                            'fn=pickle.load(file); file.close(); fn()'
        run_cmd = 'python -c "' + run_function_code + '"'
        self.run_command(run_cmd)

        # Ensure the cleanup of the created function pickle file on the Runtime
        run_cmd = 'rm ' + remote_pickle_file_path
        self.run_command(run_cmd)

        # Get the return data back as pickled file
        self.get_file(remote_return_pickle_file_path, local_return_pickle_file_path)
        self._function_return_pkl_paths.append(local_return_pickle_file_path)

        # Cleanup the return pickle file on the remote host
        run_cmd = 'rm ' + remote_return_pickle_file_path
        self.run_command(run_cmd)

        return self

    def execute(self, connection: Connection):
        """Execute the task on a remote host using a fabric connection.
        
        Args:
            connection (fabric.Connection): Fabric connection object managing the ssh connection to the remote host.
        Raises:
            ValueError: If cxn is broken and connection can not be established.
        """
        # Fabric will only consider the manually set root directory for connection.run()
        # but not fur connection.put() & connection.get(). Thus, we need to set the path in
        # these cases manually.
        try:
            root_dir = connection.run('pwd').stdout.replace('\n', '').replace('\r', '')
        except socket.gaierror:
            raise ValueError('Connection cannot be established. connection: ' + str(connection))

        for task_step in self._task_steps:

            if task_step.type == self._TaskStep.TYPE_RUN_COMMAND:
                res = connection.run(task_step.command, pty=True)
                stdout = res.stdout.replace('\n', '').replace('\r', '')
                self._execution_log.append(stdout)

            elif task_step.type == self._TaskStep.TYPE_SEND_FILE:
                remote_path = task_step.remote_path
                if not remote_path:
                    # Manually set the root dir since fabric defaults to the os user's home dir
                    local_dir, filename = os.path.split(task_step.local_path)
                    remote_path = os.path.join(root_dir, filename)
                connection.put(task_step.local_path, remote_path)
                self._execution_log.append('Send file ' + task_step.local_path + ' to ' + remote_path + connection.host)

            elif task_step.type == self._TaskStep.TYPE_GET_FILE:
                # Set root dir manually, so that it feels naturally for the user if he just 
                # uses the filename w/o a path
                remote_path = task_step.remote_path
                if not remote_path.startswith('/'):
                    remote_dir, filename = os.path.split(remote_path)
                    remote_path = os.path.join(root_dir, filename)
                connection.get(remote_path, task_step.local_path)
                self._execution_log.append('Get file ' + task_step.local_path + ' to remote.')

    def join(self):
        """Block the execution until the `RuntimeTask` finished its asynchronous execution. """
        if self.process:
            self.process.join()

    def print_log(self):
        """Print the execution log. Each log entry will be printed separately. The log index will be prepended."""
        if not self.execution_log:
            print('The log of task ' + self.name + 'is empty!')
        else:
            print('Log of Task ' + self.name + ':')
        i = 0
        for entry in self.execution_log:
            print(str(i) + ': ' + entry)
            i += 1

    # Private helper methods & attributes
    _function_index = 0
    _FUNCTION_PREFIX = 'func'
    _PICKLE_FILENAME_EXT = 'pkl'

    @classmethod
    def _create_file_name(cls, function_name: Optional[str] = None):
        """Creates a program unique function name. """
        if function_name:
            file_prefix = function_name
        else:
            file_prefix = cls._FUNCTION_PREFIX
        cls._function_index += 1
        return file_prefix + str(cls._function_index) + '.' + cls._PICKLE_FILENAME_EXT

    class _TaskStep:
        """Represents an individual action, i.e. a `_TaskStep` within a `RuntimeTask`. """
        TYPE_RUN_COMMAND = 'command'
        TYPE_SEND_FILE = 'send-file'
        TYPE_GET_FILE = 'get-file'

        def __init__(self, step_type: str, local_path: Optional[str] = None,
                     remote_path: Optional[str] = None, command: Optional[str] = None):
            self.type = step_type
            self.local_path = local_path
            self.remote_path = remote_path
            self.command = command

        def __repr__(self):
            return "%s(%r)" % (self.__class__, self.__dict__)


class Runtime(object):
    """Runtime for executing `RuntimeTasks` in it or exposing ports from / to localhost.
    
    Note: Passwordless ssh access should be be setup in advance. Otherwise the connection kwargs of fabric must be used
          for setting up the ssh connection.

    Examples:
        Execute a RuntimeTask synchronously
        >>> Runtime('host-1').execute_task(my_task, execute_async=False)

        Expose a port from localhost to the remote host so that a service running on localhost
        is accessible from the remote host as well.
        >>> Runtime('host-1').expose_port_to_runtime(8786)

        Expose a port from a remote `Runtime` to to localhost so that a service running on the `Runtime`
        is accessible from localhost as well.
        >>> Runtime('host-1').expose_port_from_runtime(8787)
    """

    LOCALHOST = 'localhost'

    # Constants used for generating process keys
    _PORT_TO_RUNTIME = '-R'
    _PORT_FROM_RUNTIME = '-L'
    _PROCESS_KEY_DELIMITER = '::'
    _TASK_PROCESS_KEY_PREFIX = 'task'

    def __init__(self, host: str, root_dir: Optional[str] = None, **connection_kwargs):
        """Initialization method.

        Args:
            host (str): The host of the `Runtime`.
            root_dir (Optional[str]): The directory which shall act as root one. Defaults to None.
                                      Consequently, a temporary directory will be created and used as root directory. If
                                      the root directory is a temporary one it will be cleaned up either `atexit` or
                                      when calling `cleanup()` manually.

            **connection_kwargs: kwargs that will be passed on to the fabric connection. Please check the fabric docs
                                 for further details.

        Raises:
            InvalidRuntimeError: If `Runtime` could not be instantiated successfully.
        """

        self._host = host
        self._connection_kwargs = connection_kwargs
        self._root_dir = root_dir
        self._root_dir_is_temp = False  # Indicates that a temp directory acts as root, which will be removed at the end
        self._processes = {}  # The dict key is a generated process identifier and the value contains the process
        self._info = {}
        self._process_manager = Manager()
        self._tasks = []

        # Cleanup will be done atexit since usage of destructor may lead to exceptions
        atexit.register(self.cleanup)

        # The check shall be executed at the end of the method, since it relies on some attributes like _root_dir etc.
        if not self.is_valid_runtime():
            raise InvalidRuntimeError(host)

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __str__(self):
        return self.class_name + ': ' + self.host

    @property
    def root_directory(self):
        """The path of the root directory that was set during object initialization. """
        self._create_root_dir_if_not_exists()
        return self._root_dir

    @property
    def task_processes(self) -> List[Process]:
        """Get all processes that were started to execute a `RuntimeTask` asynchronously.

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
        """Get the return data produced by Python functions which were executed as a consequence of
           `task.run_function()`. The call will be passed on to the `function_returns` property of the `RuntimeTask`.
           The order is determined by the order in which the `RuntimeTasks` were executed in the `Runtime`.

        Yields:
            Generator[object, None, None]: Generator object yielding the return data of the functions executed during
                                           task execution.
        """
        for task in self._tasks:
            for function_return in task.function_returns:
                yield function_return

    @classmethod
    def is_runtime_task_process(cls, process_key: str) -> bool:
        """Checks if the process which belongs to a given `process_key` was started to exectue a `RuntimeTask` based on
        an internal naming scheme of the process keys.

        Args:
            process_key (str): The generated process identifier.
        Returns:
            bool: True, if process was started to execute a `RuntimeTask`
        """
        key_splits = process_key.split(cls._PROCESS_KEY_DELIMITER)
        return True if key_splits[0] == cls._TASK_PROCESS_KEY_PREFIX else False

    @classmethod
    def is_port_exposure_process(cls, process_key: str) -> bool:
        """Check if the process which belongs to the given `process_key` is used for exposing a port, i.e. keeping
        an ssh tunnel alive.

        Args:
            process_key (str): The generated process identifier.
        Returns:
            bool: True, if process is used for port exposure.
        """
        key_splits = process_key.split(cls._PROCESS_KEY_DELIMITER)
        return True if key_splits[0] == cls._PORT_FROM_RUNTIME or key_splits[0] == cls._PORT_TO_RUNTIME else False

    @property
    def host(self) -> str:
        """Get the host of the runtime.

        Returns:
            str:  The host of the runtime.
        """
        return self._host

    @property
    def info(self) -> dict:
        """Get information about the runtime.

        Returns:
            dict: Runtime information.
        """
        if not self._info:
            self._info = self._read_info()
        return self._info

    @property
    def os(self) -> str:
        """Get operating system information.

        Returns:
            str: OS.  
        """
        if not self._info:
            self._info = self._read_info()
        return self._info['os']

    @property
    def cpu_cores(self) -> int:
        """Get information about the available CPUs. If you are in a container 
        the CPU quota will be given if set. Otherwise, the number of physical CPUs
        on the host machine is given.

        Returns:
            str: CPU quota.  
        """
        if not self._info:
            self._info = self._read_info()
        return int(self._info['cpu_cores'])

    @property
    def memory(self) -> int:
        """Get information about the total memory in bytes.

        Returns:
            str: Total memory in bytes.  
        """
        if not self._info:
            self._info = self._read_info()
        return int(self._info['memory'])

    @property
    def memory_in_mb(self):
        """Get the memory information in mb. """
        return self.memory / 1024 / 1024

    @property
    def python_version(self) -> str:
        """Get the python version.

        Returns:
            str: Python version.  
        """
        if not self._info:
            self._info = self._read_info()
        return self._info['python_version']

    @property
    def gpus(self) -> list:
        """GPU information as list. Each list entry contains information for one GPU.

        Returns:
            list: List with GPU information.
        """
        if not self._info:
            self._info = self._read_info()
        return self._info['gpus']

    @property
    def gpu_count(self) -> int:
        """The count of GPUs."""
        return len(self.gpus)

    @property
    def class_name(self) -> str:
        """Get the class name  as string. """
        return self.__class__.__name__

    @property
    def alive_process_count(self):
        """Get the number of alive processes. """
        return len(self.get_processes(only_alive=True))

    @property
    def alive_task_process_count(self):
        """Get the number of alive processes which were started to execute a `RuntimeTask`. """
        return len(self.task_processes)

    def is_valid_runtime(self) -> bool:
        """Checks if a given host is a valid `Runtime`.

        Returns:
            bool: True, if it is a valid remote runtime.
        """

        task = RuntimeTask('check-python-version')
        task.run_command('python --version')

        try:
            self.execute_task(task, execute_async=False)
        except Exception:
            return False

        if not task.execution_log[0]:
            return False

        # Example: `Python 3.6.8 :: Anaconda, Inc.`
        python_version = task.execution_log[0].split()[1].split('.')

        if not python_version:
            return False
        elif int(python_version[0]) > 3:  # Stay future-proof
            warnings.warn('The lib was originally created for Python 3.6 and is not yet fully tested for '
                          'Python >= Python 4')
            return True
        elif int(python_version[0]) == 3 and int(python_version[1]) >= 6:
            return True
        else:
            return False

    def get_free_port(self, ports: List[int]) -> int:
        """Returns the first port from the list which is currently not in use in the `Runtime`.

        Args:
             ports List[int]: The list of ports that will be used to check if the port is currently in use.

        Returns:
            int: The first port from the list which is not yet used within the whole group.

        Raises:
            NoPortsLeftError: If the port list is empty and no free port was found yet.
        """
        for port in ports:
            if self.has_free_port(port):
                return port

        raise NoPortsLeftError()

    def execute_task(self, task: RuntimeTask, execute_async: Optional[bool] = True):
        """Execute a given `RuntimeTask` in the `Runtime`.

        Args:
            task (RuntimeTask): The task to be executed.
            execute_async (bool, Optional): The execution will be done in a separate thread if True. Defaults to True.
        """
        self._create_root_dir_if_not_exists()
        async_str = ' asynchronously ' if execute_async else ' synchronously '
        print('Executing task ' + task.name + async_str + ' on ' + self._host)

        # Wrapper needed to ensure execution from root directory
        def execute_remote_wrapper():
            cxn = self._fabric_connection
            with cxn.cd(self._root_dir):
                task.execute(cxn)

        if execute_async:
            # Initialize logs with managed list (multiprocessing)
            # => We can access the logs although it is executed in another process
            task._execution_log = self._process_manager.list()
            process = Process(target=execute_remote_wrapper)
            process.start()
            self._processes.update({self._create_process_key_for_task_execution(task): process})
            task._process = process
        else:
            execute_remote_wrapper()

        self._tasks.append(task)

    def _create_root_dir_if_not_exists(self):
        if not self._root_dir:
            self._root_dir = self.create_tempdir()
            self._root_dir_is_temp = True
            print('Temporary directory ' + self._root_dir + ' created on ' + self._host)

    def print_log(self):
        """Print the execution logs of each `RuntimeTask` that was executed in the `Runtime`. """
        for task in self._tasks:
            task.print_log()

    def clear_tasks(self):
        """Clears all internal state related to `RuntimeTasks`. """
        self._tasks = []
        self._processes = {key: value for key, value in self._processes.items()
                           if not Runtime.is_runtime_task_process(key)}

    def expose_port_to_runtime(self, local_port: int, runtime_port: Optional[int] = None) -> str:
        """Expose a port from localhost to the `Runtime` so that all traffic on the `runtime_port` is forwarded to the
        `local_port` on localhost.
        
        Args:
            local_port (int): The port on the local machine.
            runtime_port (Optional[int]): The port on the runtime. Defaults to `local_port`.

        Returns:
            str: Process key, which can be used for manually stopping the process running the port exposure for example.
        
        Examples:
            A DB is running on localhost on port `local_port` and the DB is only accessible from localhost.
            But you also want to access the service on the remote `Runtime` on port `runtime_port`. Then you can use
            this method to expose the service which is running on localhost to the remote host.
        """
        if not runtime_port:
            runtime_port = local_port
        if local_port == runtime_port and self._host == self.LOCALHOST:
            # We can not forward a port to itself!
            print('Port exposure skipped. Can\'t expose a port to myself.')
            return ''
        elif not self.has_free_port(runtime_port):
            raise PortInUseError(runtime_port, runtime=self)

        proc = Process(target=self._forward_runtime_port_to_local,
                       kwargs={'local_port': local_port, 'runtime_port': runtime_port})
        proc.start()
        key = self._create_process_key_for_port_exposure(self._PORT_TO_RUNTIME, local_port, runtime_port)
        self._processes.update({key: proc})
        time.sleep(0.1)  # Necessary to prevent collisions with MaxStartup restrictions
        print('Local port ' + str(local_port) + ' exposed to runtime ' + self._host + ' on port ' +
              str(runtime_port))
        return key

    def expose_port_from_runtime(self, runtime_port: int, local_port: Optional[int] = None) -> str:
        """Expose a port from a `Runtime` to localhost so that all traffic to the `local_port` is forwarded to the
        `runtime_port` of the `Runtime`. This corresponds to local port forwarding in ssh tunneling terms.
        
        Args:            
            runtime_port (int): The port on the runtime.
            local_port (Optional[int]): The port on the local machine. Defaults to `runtime_port`.

        Returns:
            str: Process key, which can be used for manually stopping the process running the port exposure.
        
        Examples:
            A DB is running on a remote host on port `runtime_port` and the DB is only accessible from the remote host.
            But you also want to access the service from the local machine on port `local_port`. Then you can use this
            method to expose the service which is running on the remote host to localhost.

        """
        if not local_port:
            local_port = runtime_port
        if local_port == runtime_port and self._host == self.LOCALHOST:
            # We can not forward a port to itself!
            print('Port exposure skipped. Can\'t expose a port to myself.')
            return ''
        elif not localhost_has_free_port(local_port):
            raise PortInUseError(runtime_port, runtime=self)

        proc = Process(target=self._forward_local_port_to_runtime,
                       kwargs={'local_port': local_port, 'runtime_port': runtime_port})
        proc.start()
        key = self._create_process_key_for_port_exposure(self._PORT_FROM_RUNTIME, local_port, runtime_port)
        self._processes.update({key: proc})
        time.sleep(0.1)  # Necessary to prevent collisions with MaxStartup restrictions
        print('Port ' + str(runtime_port) + ' from runtime ' + self._host + ' exposed to local port ' +
              str(local_port))
        return key

    def get_process(self, key: str) -> Process:
        """Get an individual process by process key.
        
        Args:
            key (str): The key identifying the process.
            
        Returns:
            Process: The desired process.

        Raises:
            ValueError: Unknown process key.
        """
        if key not in self._processes:
            raise ValueError('Unknown process key.')
        return self._processes[key]

    def get_processes(self, only_alive: bool = False) -> Dict[str, Process]:
        """Get all managed processes or only the alive ones as dictionary with the process key as dict key. An
        individual process can be retrieved by key via `get_process()`.
        
        Args:
            only_alive (bool): True, if only alive processes shall be returned instead of all. Defaults to False.
            
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

    def stop_process(self, key: str):
        """Stop a process by its key. 

        Args: 
            key (str): The key identifying the process.
        
        Raises:
            ValueError: Unknown process key.
        """
        if key not in self._processes:
            raise ValueError('Unknown process key.')
        self._processes[key].terminate()

    def has_free_port(self, port: int) -> bool:
        """Checks if the port is available on the runtime. 
        
        Args:
            port (int): The port which will be checked.

        Returns:
            bool: True if port is free, else False.
        """
        with self._fabric_connection as cxn:
            cmd_str = 'python -c "import socket;print(\'free\') ' \
                      'if socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex((\'localhost\', ' + str(port) + \
                      ')) else None"'
            res = cxn.run(cmd_str)
            return True if res.stdout else False

    def print_info(self):
        """Print the Runtime info formatted as table."""
        info = self.info
        print('\n')
        print('Information of `' + self.class_name + '` ' + self.host + ':')
        for key, value in info.items():
            display_value = value if not key == 'memory' else str(self.memory_in_mb) + ' mb'
            print('{:<8} {:<8}'.format(key, display_value))

    def check_filter(self,
                     gpu_required: bool = False,
                     min_memory: Optional[int] = None,
                     min_cpu_cores: Optional[int] = None,
                     installed_executables: Union[str, List[str], None] = None,
                     filter_commands: Union[str, List[str], None] = None) -> bool:
        """Checks the `Runtime` object for certain filter criteria.

        Args:
            gpu_required (bool): True, if gpu availability is required. Defaults to False.
            min_memory (Optional[int]): The minimal amount of memory in MB. Defaults to None, i.e. not restricted.
            min_cpu_cores (Optional[int]): The minimum number of cpu cores required. Defaults to None, i.e. not
                                           restricted.
            installed_executables (Union[str, List[str], None]): Possibility to check if an executable is
                                                                installed. E.g. if the executable `ping` is installed.
            filter_commands (Union[str, List[str], None]): Shell commands that can be used for generic filtering.
                                                           See examples. A filter command must echo true to be evaluated
                                                           to True, everything else will be interpreted as False.
                                                           Defaults to None.

        Returns:
            bool: True, if all filters were successfully checked otherwise False.

        Examples:
            >>> runtime = Runtime('host-1')
            Check if the `Runtime` has a specific executable installed
            such as `ping` the network administration software utility.
            >>> check_passed = runtime.check_filter(installed_executables='ping')

            Check if a variable `WORKSPACE_VERSION` is set on the `Runtime`
            >>> filter_str = '[ ! -z "$WORKSPACE_VERSION" ] && echo "true" || echo "false"'
            >>> check_passed = runtime.check_filter(filer_commands=filter_str)
        """

        all_filters_checked = True

        if gpu_required and not self.gpus:
            print(self.class_name + ' ' + self.host + 'does not have GPUs.')
            all_filters_checked = False

        if min_memory and self.memory < min_memory:
            print(self.class_name + ' ' + self.host + 'has only ' + str(self.memory) + ' instead of ' + str(min_memory) +
                  ' as required')
            all_filters_checked = False

        if min_cpu_cores and self.cpu_cores < min_cpu_cores:
            print(self.class_name + ' ' + self.host + 'has only ' + str(self.cpu_cores) + ' instead of ' + str(min_cpu_cores) +
                  ' as required.')
            all_filters_checked = False

        if installed_executables:
            for executable_name in _utils.create_list_from_parameter_value(installed_executables):
                if not self._has_executable_installed(str(executable_name)):
                    print(self.class_name + ' ' + self.host + 'does not have executable ' + str(executable_name) +
                          'installed.')
                    all_filters_checked = False

        if filter_commands:
            for filter_command in _utils.create_list_from_parameter_value(filter_commands):
                if not self._filter_command_checked(str(filter_command)):
                    print('Filter ' + filter_commands + ' could not be checked successfully on ' + self.class_name + ' ' +
                          self.host + ' .')
                    all_filters_checked = False

        return all_filters_checked

    def create_tempdir(self) -> str:
        """Create a temporary directory and return its name/path.

        Returns:
            str: The name/path of the directory.
        """
        with self._fabric_connection as cxn:
            cmd_str = 'python -c "import tempfile; print(tempfile.mkdtemp())"'
            res = cxn.run(cmd_str)
            path = res.stdout.split("\n")[0]
            if not path:
                path = res.stdout
            return path

    def create_dir(self, path):
        """Create a directory. All folders in the path will be created if not existing.

        Args:
            path (str): The full path of the directory to be created.
        """
        with self._fabric_connection as cxn:
            cmd_str = 'mkdir -p ' + path
            res = cxn.run(cmd_str)

    def delete_dir(self, path: str) -> bool:
        """Delete a directory recursively. If at least one contained file could not be removed then False is returned.

        Args:
            path (str): The full path of the directory to be deleted.

        Returns:
            bool: True if the directory could be deleted successfully.
        """
        with self._fabric_connection as cxn:
            cmd_str = 'rm -r ' + path
            try:
                cxn.run(cmd_str)
                return True
            except:
                return False

    def cleanup(self):
        """Release all acquired resources and terminate all processes. """
        for key, process in self._processes.items():
            process.terminate()
            process.join()
            if process.is_alive():
                print('Process with key ' + key + ' could not be terminated')
            else:
                print('Process with key ' + key + ' terminated')
        if self._root_dir_is_temp and self._root_dir:
            success = self.delete_dir(self._root_dir)
            if success:
                print('Temporary directory ' + self.root_directory + ' of Runtime ' + self.host + ' removed.')
                self._root_dir = None
                self._root_dir_is_temp = False
            else:
                print('Temporary directory ' + self.root_directory + ' of Runtime ' + self.host +
                      ' could not be removed.')

    # - Private methods -#

    @classmethod
    def _create_process_key_for_port_exposure(cls, direction: str, local_port: int, runtime_port: int) -> str:
        """Create a process key for processes exposing ports, i.e. keeping ssh tunnels open.
        This key will act as an identifier for internally generated processes.
        
        Raises:
            ValueError: If direction has an invalid value.
        """
        if not local_port:
            local_port = runtime_port
        if not runtime_port:
            runtime_port = local_port

        delimiter = cls._PROCESS_KEY_DELIMITER

        if direction == cls._PORT_FROM_RUNTIME:
            return cls._PORT_FROM_RUNTIME + delimiter + str(local_port) + delimiter + str(runtime_port)
        elif direction == cls._PORT_TO_RUNTIME:
            return cls._PORT_TO_RUNTIME + delimiter + str(runtime_port) + delimiter + str(local_port)
        else:
            raise ValueError(direction + ' is not a supported runtime process prefix type')

    @classmethod
    def _create_process_key_for_task_execution(cls, task: RuntimeTask) -> str:
        """Create a process key for processes started to execute a `RuntimeTasks` asynchronously
        This key will act as an identifier for internally generated processes.
        """
        return cls._TASK_PROCESS_KEY_PREFIX + cls._PROCESS_KEY_DELIMITER + task.name

    @classmethod
    def _create_executable_installed_shell_cmd(cls, executable: str) -> str:
        return 'hash ' + executable + ' 2>/dev/null && echo "true" || echo ""'

    def _has_executable_installed(self, executable_name: str) -> bool:
        """Checks if an executable is installed on the runtime."""
        shell_cmd = self._create_executable_installed_shell_cmd(executable_name)
        return self._filter_command_checked(shell_cmd)

    def _filter_command_checked(self, shell_cmd: str) -> bool:
        task = RuntimeTask('_filter_command_checked')
        task.run_command(shell_cmd)
        self.execute_task(task, execute_async=False)

        # Check the last log entry for the string true
        result = str(task.execution_log[len(task.execution_log) - 1])
        return True if result.lower() == 'true' else False

    @property
    def _fabric_connection(self) -> Connection:
        """Get a new fabric connection to the runtime.

        Raises:
            ValueError: If user or port values are given via both host shorthand
                        and their own arguments.
        """
        try:
            return Connection(host=self.host, connect_kwargs=self._connection_kwargs)
        except socket.gaierror:
            raise ValueError('Cannot establish SSH connection to host ' + self.host)

    def _forward_local_port_to_runtime(self, local_port: int, runtime_port: Optional[int] = None):
        """Creates ssh connection to the runtime and creates then a ssh tunnel
        from `localhost`:`local_port to `runtime`:`runtime_port`. """
        if not runtime_port:
            runtime_port = local_port

        with self._fabric_connection.forward_local(local_port, runtime_port):
            while True:
                time.sleep(1000)

    def _forward_runtime_port_to_local(self, runtime_port: int, local_port: Optional[int] = None):
        """Creates ssh connection to the runtime and then creates a ssh tunnel
        from `runtime`:`runtime_port` to `localhost`:`local_port`. """
        if not local_port:
            local_port = runtime_port

        with self._fabric_connection.forward_remote(runtime_port, local_port):
            while True:
                time.sleep(1000)

    def _read_info(self) -> dict:
        """Read the host machine information.  """
        task = RuntimeTask('get-host-info')
        task.run_command('pip install -q --upgrade ' + settings.PIP_PROJECT_NAME)
        task.run_function(print_localhost_info)
        self.execute_task(task, execute_async=False)
        return json.loads(task.execution_log[4])


""" Module level utils """


def get_localhost_info() -> dict:
    """Get information about the specifications of localhost.

    Returns:
        dict: Current dict keys: 'os', 'cpu_cores', 'memory', 'python_version', 'workspace_version', 'gpus'.
    """
    info = {
        'os': _get_os_on_localhost(),
        'cpu_cores': _get_cpu_count_on_localhost(),
        'memory': _get_memory_on_localhost(),
        'python_version': _get_python_version_on_localhost(),
        'workspace_version': _get_workspace_version_on_localhost(),
        'gpus': _get_gpu_count_from_localhost()
    }
    return info


def print_localhost_info():
    """Prints the dictionary retrieved by `get_localhost_info()`."""
    json_str = json.dumps(get_localhost_info())
    print(json_str)


def command_exists_on_localhost(command: str) -> bool:
    """Check if a command exists on localhost"""
    cmd_ext = 'hash ' + command + ' 2>/dev/null && echo "True" || echo ""'
    return True if os.popen(cmd_ext).read() else False


def localhost_has_free_port(port: int) -> bool:
    """Checks if the port is free on localhost.

    Args:
        port (int): The port which will be checked.
    Returns:
        bool: True if port is free, else False.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    is_success = sock.connect_ex(('localhost', port))
    return True if is_success else False


""" Private module level utils """


def _get_os_on_localhost() -> str:
    return platform.platform()


def _get_cpu_count_on_localhost() -> str:
    # Read the cpu quota
    cpu_quota = os.popen('cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us').read()
    # Remove newlines
    cpu_quota = cpu_quota.replace('\n', '')
    if not cpu_quota.isnumeric():
        return str(os.cpu_count())
    else:
        return str(float(cpu_quota) / 100000)


def _get_memory_on_localhost() -> str:
    mem_limit = None
    if os.path.isfile("/sys/fs/cgroup/memory/memory.limit_in_bytes"):
        with open('/sys/fs/cgroup/memory/memory.limit_in_bytes', 'r') as file:
            mem_limit = file.read().replace('\n', '').strip()

    total_memory = psutil.virtual_memory().total

    if not mem_limit:
        mem_limit = total_memory
    elif int(mem_limit) > int(total_memory):
        # if mem limit from cgroup bigger than total memory -> use total memory
        mem_limit = total_memory

    return str(mem_limit)


def _get_python_version_on_localhost() -> str:
    return str(sys.version_info.major) + '.' + str(sys.version_info.minor) + '.' + str(sys.version_info.micro)


def _get_workspace_version_on_localhost() -> str:
    return os.environ['WORKSPACE_VERSION']


def _get_gpu_count_from_localhost() -> int:
    NVIDIA_CMD = 'nvidia-smi'

    if not command_exists_on_localhost(NVIDIA_CMD):
        return 0

    try:
        sp = subprocess.Popen([NVIDIA_CMD, '-q'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out_str = sp.communicate()
        out_list = out_str[0].decode("utf-8").split('\n')

        count_gpu = 0
        for item in out_list:
            try:
                key, val = item.split(':')
                key, val = key.strip(), val.strip()
                if key == 'Product Name':
                    count_gpu += 1
            except:
                pass
    except:
        count_gpu = 0
    return count_gpu
