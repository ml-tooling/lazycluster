
**Source:** [/lazycluster/runtimes.py](/lazycluster/runtimes.py#L0)

-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L35)</span>

## RuntimeTask class

This class provides the functionality for executing a sequence of elementary operations over ssh. The `fabric`
library is used for handling ssh connections. A `RuntimeTask` can be composed from four different operations which
we call steps, namely adding a step for running a shell command via `run_command()`, sending a file to a host via
`send_file()`, retrieving a file from a host via `get_file()` or adding a step for executing a python function on a
host via `run_function()`. The current restriction for running functions is that these functions need to be
serializable via cloudpickle. To actually execute a `RuntimeTask`, i.e. the sequence of task steps, either a call
to `execute()` is necessary or a handover to the `execute_task()` method of the `Runtime` class is necessary.
Usually, a `RuntimeTask` will be executed in a `Runtime` or in a `RuntimeGroup`. See its documentation for further
details.

**Examples:**
  ```python 
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
  ```
#### RuntimeTask.execution_log
 
Return the execution log as list. The list is empty as long as a task was not yet executed. Each log entry
corresponds to a single task step and the log index starts at `0`. If th execution of an individual step does not
produce and outut the list entry will be empty.

#### RuntimeTask.function_returns
 
Get the return data produced by functions which were executed as a consequence of a `task.run_function()`
call.

Internally, a function return is saved as a pickled file. This method unpickles each file one after
another and yields the data. Moreover, the return data will be yielded in the same order as the functions were
executed.

**Yields:**

   Generator[object, None, None]: Generator object yielding the return data of the functions executed during
   task execution.


#### RuntimeTask.name
 
Get the task name.

**Returns:**

 - `str`:  Task name

#### RuntimeTask.process
 
Returns the process object in which the task were executed. None, if not yet or synchronously executed. 

-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L63)</span>

### RuntimeTask.`__init__`

```python
__init__(self, name:  Union[str, NoneType]  =  None)
```

Initialization method.

**Args:**

 - `name` (Optional[str]):  The name of the task. Defaults to None and consequently a unique identifier is
  generated via Python's id() function.


-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L91)</span>

### RuntimeTask.cleanup

```python
cleanup(self)
```

Remove temporary used resources, like temporary directories if created.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L283)</span>

### RuntimeTask.execute

```python
execute(self, connection:  fabric.connection.Connection)
```

Execute the task on a remote host using a fabric connection.

**Args:**

 - `connection` (fabric.Connection):  Fabric connection object managing the ssh connection to the remote host.
**Raises:**

 - `ValueError`:  If cxn is broken and connection can not be established.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L166)</span>

### RuntimeTask.get_file

```python
get_file(
    self,
    remote_path:  str,
    local_path:  Union[str,
    NoneType]  =  None
)
```

Create a task step for getting either a single file or a folder from another host to localhost.

**Args:**

 - `remote_path` (str):  Path to file on host.
 - `local_path` (Optional[str]):  Path to file on local machine. The remote file is downloaded 
  to the current working directory (as seen by os.getcwd) using 
  its remote filename if local_path is None. This is the default
  behavior of fabric.
**Raises:**

 - `ValueError`:  If remote path is emtpy.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L325)</span>

### RuntimeTask.join

```python
join(self)
```

Block the execution until the `RuntimeTask` finished its asynchronous execution. 
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L330)</span>

### RuntimeTask.print_log

```python
print_log(self)
```

Print the execution log. Each log entry will be printed separately. The log index will be prepended.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L186)</span>

### RuntimeTask.run_command

```python
run_command(self, command:  str)
```

Create a task step for running a given shell command. 

**Args:**

 - `command` (str):  Shell command.

**Raises:**

 - `ValueError`:  If command is emtpy.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L201)</span>

### RuntimeTask.run_function

```python
run_function(
    self,
    function:  <built-in function callable>,
    **func_kwargs
)
```

Create a task step for executing a given python function on a remote host. The function will be transferred
to the remote host via ssh and cloudpickle. The return data can be requested via the property `function_returns`

**Note:**

  Hence, the function must be serializable via cloudpickle and all dependencies must be available in its
  correct versions on the remote host for now. We are planning to improve the dependency handling.

**Args:**

 - `function` (callable):  The function to be executed remotely.
**func_kwargs: kwargs which will be passed to the function.

**Raises:**

 - `ValueError`:  If function is empty.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L146)</span>

### RuntimeTask.send_file

```python
send_file(
    self,
    local_path:  str,
    remote_path:  Union[str,
    NoneType]  =  None
)
```

Create a task step for sending either a single file or a folder from localhost to another host.

**Args:**

 - `local_path` (str):  Path to file on local machine.
 - `remote_path` (Optional[str]):  Path on the remote host. Defaults to the root directory.

**Raises:**

 - `ValueError`:  If file locally not found.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L373)</span>

## Runtime class

Runtime for executing `RuntimeTasks` in it or exposing ports from / to localhost.

**Note: Passwordless ssh access should be be setup in advance. Otherwise the connection kwargs of fabric must be used**

  for setting up the ssh connection.

**Examples:**
  ```python
  Execute a RuntimeTask synchronously
  >>> Runtime('host-1').execute_task(my_task, execute_async=False)

  Expose a port from localhost to the remote host so that a service running on localhost
  is accessible from the remote host as well.
  >>> Runtime('host-1').expose_port_to_runtime(8786)

  Expose a port from a remote `Runtime` to to localhost so that a service running on the `Runtime`
  is accessible from localhost as well.
  >>> Runtime('host-1').expose_port_from_runtime(8787)
  ```
#### Runtime.alive_process_count
 
Get the number of alive processes. 

#### Runtime.alive_task_process_count
 
Get the number of alive processes which were started to execute a `RuntimeTask`. 

#### Runtime.class_name
 
Get the class name  as string. 

#### Runtime.cpu_cores
 
Get information about the available CPUs. If you are in a container 
the CPU quota will be given if set. Otherwise, the number of physical CPUs
on the host machine is given.

**Returns:**

 - `str`:  CPU quota.  

#### Runtime.function_returns
 
Get the return data produced by Python functions which were executed as a consequence of
  `task.run_function()`. The call will be passed on to the `function_returns` property of the `RuntimeTask`.
  The order is determined by the order in which the `RuntimeTasks` were executed in the `Runtime`.

**Yields:**

  Generator[object, None, None]: Generator object yielding the return data of the functions executed during
  task execution.

#### Runtime.gpu_count
 
The count of GPUs.

#### Runtime.gpus
 
GPU information as list. Each list entry contains information for one GPU.

**Returns:**

 - `list`:  List with GPU information.

#### Runtime.host
 
Get the host of the runtime.

**Returns:**

 - `str`:   The host of the runtime.

#### Runtime.info
 
Get information about the runtime.

**Returns:**

 - `dict`:  Runtime information.

#### Runtime.memory
 
Get information about the total memory in bytes.

**Returns:**

 - `str`:  Total memory in bytes.  

#### Runtime.memory_in_mb
 
Get the memory information in mb. 

#### Runtime.os
 
Get operating system information.

**Returns:**

 - `str`:  OS.  

#### Runtime.python_version
 
Get the python version.

**Returns:**

 - `str`:  Python version.  

#### Runtime.root_directory
 
The path of the root directory that was set during object initialization. 

#### Runtime.task_processes
 
Get all processes that were started to execute a `RuntimeTask` asynchronously.

**Returns:**

  List[Process]: RuntimeTask processes.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L400)</span>

### Runtime.`__init__`

```python
__init__(
    self,
    host:  str,
    root_dir:  Union[str,
    NoneType]  =  None,
    **connection_kwargs
)
```

Initialization method.

**Args:**

 - `host` (str):  The host of the `Runtime`.
 - `root_dir` (Optional[str]):  The directory which shall act as root one. Defaults to None.
  Consequently, a temporary directory will be created and used as root directory. If
  the root directory is a temporary one it will be cleaned up either `atexit` or
  when calling `cleanup()` manually.

**connection_kwargs: kwargs that will be passed on to the fabric connection. Please check the fabric docs
  for further details.

**Raises:**

 - `InvalidRuntimeError`:  If `Runtime` could not be instantiated successfully.


-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L844)</span>

### Runtime.check_filter

```python
check_filter(
    self,
    gpu_required:  bool  =  False,
    min_memory:  Union[int,
    NoneType]  =  None,
    min_cpu_cores:  Union[int,
    NoneType]  =  None,
    installed_executables:  Union[str,
    List[str],
    NoneType]  =  None,
    filter_commands:  Union[str,
    List[str],
    NoneType]  =  None
) -> bool
```

Checks the `Runtime` object for certain filter criteria.

**Args:**

 - `gpu_required` (bool):  True, if gpu availability is required. Defaults to False.
 - `min_memory` (Optional[int]):  The minimal amount of memory in MB. Defaults to None, i.e. not restricted.
 - `min_cpu_cores` (Optional[int]):  The minimum number of cpu cores required. Defaults to None, i.e. not
  restricted.
 - `installed_executables` (Union[str, List[str], None]):  Possibility to check if an executable is
  installed. E.g. if the executable `ping` is installed.
 - `filter_commands` (Union[str, List[str], None]):  Shell commands that can be used for generic filtering.
  See examples. A filter command must echo true to be evaluated
  to True, everything else will be interpreted as False.
  Defaults to None.

**Returns:**

 - `bool`:  True, if all filters were successfully checked otherwise False.

**Examples:**

Check if the `Runtime` has a specific executable installed
such as `ping` the network administration software utility.
```python
>>> check_passed = runtime.check_filter(installed_executables='ping')
```
Check if a variable `WORKSPACE_VERSION` is set on the `Runtime`
```python
>>> filter_str = '[ ! -z "$WORKSPACE_VERSION" ] && echo "true" || echo "false"'
>>> check_passed = runtime.check_filter(filer_commands=filter_str)
```
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L951)</span>

### Runtime.cleanup

```python
cleanup(self)
```

Release all acquired resources and terminate all processes. 
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L691)</span>

### Runtime.clear_tasks

```python
clear_tasks(self)
```

Clears all internal state related to `RuntimeTasks`. 
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L924)</span>

### Runtime.create_dir

```python
create_dir(self, path)
```

Create a directory. All folders in the path will be created if not existing.

**Args:**

 - `path` (str):  The full path of the directory to be created.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L910)</span>

### Runtime.create_tempdir

```python
create_tempdir(self) -> str
```

Create a temporary directory and return its name/path.

**Returns:**

 - `str`:  The name/path of the directory.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L934)</span>

### Runtime.delete_dir

```python
delete_dir(self, path:  str) -> bool
```

Delete a directory recursively. If at least one contained file could not be removed then False is returned.

**Args:**

 - `path` (str):  The full path of the directory to be deleted.

**Returns:**

 - `bool`:  True if the directory could be deleted successfully.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L650)</span>

### Runtime.execute_task

```python
execute_task(
    self,
    task:  lazycluster.runtimes.RuntimeTask,
    execute_async:  Union[bool,
    NoneType]  =  True
)
```

Execute a given `RuntimeTask` in the `Runtime`.

**Args:**

 - `task` (RuntimeTask):  The task to be executed.
 - `execute_async` (bool, Optional):  The execution will be done in a separate thread if True. Defaults to True.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L732)</span>

### Runtime.expose_port_from_runtime

```python
expose_port_from_runtime(
    self,
    runtime_port:  int,
    local_port:  Union[int,
    NoneType]  =  None
) -> str
```

Expose a port from a `Runtime` to localhost so that all traffic to the `local_port` is forwarded to the
`runtime_port` of the `Runtime`. This corresponds to local port forwarding in ssh tunneling terms.

**Args:**

 - `runtime_port` (int):  The port on the runtime.
 - `local_port` (Optional[int]):  The port on the local machine. Defaults to `runtime_port`.

**Returns:**

 - `str`:  Process key, which can be used for manually stopping the process running the port exposure.

**Examples:**

A DB is running on a remote host on port `runtime_port` and the DB is only accessible from the remote host.
But you also want to access the service from the local machine on port `local_port`. Then you can use this
method to expose the service which is running on the remote host to localhost.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L697)</span>

### Runtime.expose_port_to_runtime

```python
expose_port_to_runtime(
    self,
    local_port:  int,
    runtime_port:  Union[int,
    NoneType]  =  None
) -> str
```

Expose a port from localhost to the `Runtime` so that all traffic on the `runtime_port` is forwarded to the
`local_port` on localhost.

**Args:**

 - `local_port` (int):  The port on the local machine.
 - `runtime_port` (Optional[int]):  The port on the runtime. Defaults to `local_port`.

**Returns:**

 - `str`:  Process key, which can be used for manually stopping the process running the port exposure for example.

**Examples:**

A DB is running on localhost on port `local_port` and the DB is only accessible from localhost.
But you also want to access the service on the remote `Runtime` on port `runtime_port`. Then you can use
this method to expose the service which is running on localhost to the remote host.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L632)</span>

### Runtime.get_free_port

```python
get_free_port(self, ports:  List[int]) -> int
```

Returns the first port from the list which is currently not in use in the `Runtime`.

**Args:**

  ports List[int]: The list of ports that will be used to check if the port is currently in use.

**Returns:**

 - `int`:  The first port from the list which is not yet used within the whole group.

**Raises:**

 - `NoPortsLeftError`:  If the port list is empty and no free port was found yet.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L768)</span>

### Runtime.get_process

```python
get_process(self, key:  str) -> multiprocessing.context.Process
```

Get an individual process by process key.

**Args:**

 - `key` (str):  The key identifying the process.

**Returns:**

 - `Process`:  The desired process.

**Raises:**

 - `ValueError`:  Unknown process key.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L784)</span>

### Runtime.get_processes

```python
get_processes(
    self,
    only_alive:  bool  =  False
) -> Dict[str, multiprocessing.context.Process]
```

Get all managed processes or only the alive ones as dictionary with the process key as dict key. An
individual process can be retrieved by key via `get_process()`.

**Args:**

 - `only_alive` (bool):  True, if only alive processes shall be returned instead of all. Defaults to False.

**Returns:**

Dict[str, Process]: Dictionary with process keys as dict keys and the respective processes as dict values.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L819)</span>

### Runtime.has_free_port

```python
has_free_port(self, port:  int) -> bool
```

Checks if the port is available on the runtime. 

**Args:**

 - `port` (int):  The port which will be checked.

**Returns:**

 - `bool`:  True if port is free, else False.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L600)</span>

### Runtime.is_valid_runtime

```python
is_valid_runtime(self) -> bool
```

Checks if a given host is a valid `Runtime`.

**Returns:**

 - `bool`:  True, if it is a valid remote runtime.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L835)</span>

### Runtime.print_info

```python
print_info(self)
```

Print the Runtime info formatted as table.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L686)</span>

### Runtime.print_log

```python
print_log(self)
```

Print the execution logs of each `RuntimeTask` that was executed in the `Runtime`. 
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L806)</span>

### Runtime.stop_process

```python
stop_process(self, key:  str)
```

Stop a process by its key. 

**Args:**

 - `key` (str):  The key identifying the process.

**Raises:**

 - `ValueError`:  Unknown process key.

<span style="float:right;">[[source]](/lazycluster/runtimes.py#L1064)</span>
