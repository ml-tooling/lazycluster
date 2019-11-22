
**Source:** [/lazycluster/runtimes.py#L0](/lazycluster/runtimes.py#L0)


-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L28)</span>

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

#### RuntimeTask.execution_log
 
The execution log as list. The list is empty as long as a task was not yet executed. Each log entry
corresponds to a single task step and the log index starts at `0`. If th execution of an individual step does not
produce and outut the list entry will be empty.

#### RuntimeTask.function_returns
 
The return data produced by functions which were executed as a consequence of a `task.run_function()`
call.

Internally, a function return is saved as a pickled file. This method unpickles each file one after
another and yields the data. Moreover, the return data will be yielded in the same order as the functions were
executed.

**Yields:**

   Generator[object, None, None]: Generator object yielding the return data of the functions executed during
   task execution.


#### RuntimeTask.name
 
The task name.

**Returns:**

 - `str`:  Task name

#### RuntimeTask.process
 
The process object in which the task were executed. None, if not yet or synchronously executed.
  

-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L58)</span>

### RuntimeTask.`__init__`

```python
__init__(self, name:  Union[str, NoneType]  =  None)
```

Initialization method.

**Args:**

 - `name`:  The name of the task. Defaults to None and consequently a unique identifier is generated via Python's
  id() function.


-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L90)</span>

### RuntimeTask.cleanup

```python
cleanup(self)
```

Remove temporary used resources, like temporary directories if created.
  
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L297)</span>

### RuntimeTask.execute

```python
execute(
    self,
    connection:  fabric.connection.Connection,
    debug:  bool  =  False
)
```

Execute the task on a remote host using a fabric connection.

**Note:**

  Each individual task step will be executed relatively to the current directory of the fabric connection.
  Although, the current directory might have changed in the previous task step. Each directory change is
  temporary limited to a single task step.
  If the task gets executed via a `Runtime`, then the current directory will be the Runtimes working
  directory. See the `Runtime` docs for further details.
  Moreover, beside the regular Python log or the `debug` option you can access the execution logs via
  task.`execution.log`. The log gets updated after each task step.

**Args:**

 - `connection`:  Fabric connection object managing the ssh connection to the remote host.
debug : If `True`, stdout/stderr from the remote host will be printed to stdout of localhost. If, `False`
  then the stdout/stderr will be added to python logger with level debug after each task step.
**Raises:**

 - `ValueError`:  If cxn is broken and connection can not be established.
 - `TaskExecutionError`:  If an executed task step can't be executed successfully.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L172)</span>

### RuntimeTask.get_file

```python
get_file(
    self,
    remote_path:  str,
    local_path:  Union[str,
    NoneType]  =  None
) → 'RuntimeTask'
```

Create a task step for getting either a single file or a folder from another host to localhost.

**Args:**

 - `remote_path`:  Path to file on host.
 - `local_path`:  Path to file on local machine. The remote file is downloaded  to the current working directory
  (as seen by os.getcwd) using its remote filename if local_path is None. This is the default
  behavior of fabric.

**Returns:**

 - `RuntimeTask`:  self.

**Raises:**

 - `ValueError`:  If remote path is emtpy.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L392)</span>

### RuntimeTask.join

```python
join(self)
```

Block the execution until the `RuntimeTask` finished its asynchronous execution.
  
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L398)</span>

### RuntimeTask.print_log

```python
print_log(self)
```

Print the execution log. Each log entry will be printed separately. The log index will be prepended.
  
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L195)</span>

### RuntimeTask.run_command

```python
run_command(self, command:  str) → 'RuntimeTask'
```

Create a task step for running a given shell command. 

**Args:**

 - `command`:  Shell command.

**Returns:**

 - `RuntimeTask`:  self.

**Raises:**

 - `ValueError`:  If command is emtpy.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L213)</span>

### RuntimeTask.run_function

```python
run_function(
    self,
    function:  <built-in function callable>,
    **func_kwargs
) → 'RuntimeTask'
```

Create a task step for executing a given python function on a remote host. The function will be transferred
to the remote host via ssh and cloudpickle. The return data can be requested via the property `function_returns`

**Note:**

  Hence, the function must be serializable via cloudpickle and all dependencies must be available in its
  correct versions on the remote host for now. We are planning to improve the dependency handling.

**Args:**

 - `function`:  The function to be executed remotely.
 - `func_kwargs`:  kwargs which will be passed to the function.

**Returns:**

 - `RuntimeTask`:  self.

**Raises:**

 - `ValueError`:  If function is empty.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L148)</span>

### RuntimeTask.send_file

```python
send_file(
    self,
    local_path:  str,
    remote_path:  Union[str,
    NoneType]  =  None
) → 'RuntimeTask'
```

Create a task step for sending either a single file or a folder from localhost to another host.

**Args:**

 - `local_path`:  Path to file on local machine.
 - `remote_path`:  Path on the remote host. Defaults to the connection working directory. See
  `RuntimeTask.execute()` docs for further details.

**Returns:**

 - `RuntimeTask`:  self.

**Raises:**

 - `ValueError`:  If file locally not found.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L444)</span>

## Runtime class

Runtime for executing `RuntimeTasks` in it or exposing ports from / to localhost.

**Note:**

  Passwordless ssh access should be be setup in advance. Otherwise the connection kwargs of fabric must be used
  for setting up the ssh connection. See prerequisites in project README.

**Examples:**

  ```python
  # Execute a RuntimeTask synchronously
  Runtime('host-1').execute_task(my_task, execute_async=False)
  # Expose a port from localhost to the remote host so that a service running on localhost
  # is accessible from the remote host as well.
  Runtime('host-1').expose_port_to_runtime(8786)
  # Expose a port from a remote `Runtime` to to localhost so that a service running on the `Runtime`
  # is accessible from localhost as well.
  Runtime('host-1').expose_port_from_runtime(8787)
  ```

#### Runtime.alive_process_count
 
The number of alive processes.

**Returns:**

 - `int`:  The count.

#### Runtime.alive_task_process_count
 
The number of alive processes which were started to execute a `RuntimeTask`.

**Returns:**

 - `int`:  The count.

#### Runtime.class_name
 
The class name  as string. 

#### Runtime.cpu_cores
 
Information about the available CPUs. If you are in a container
the CPU quota will be given if set. Otherwise, the number of physical CPUs
on the host machine is given.

**Returns:**

 - `str`:  CPU quota.

#### Runtime.function_returns
 
The return data produced by Python functions which were executed as a consequence of
  `task.run_function()`. The call will be passed on to the `function_returns` property of the `RuntimeTask`.
  The order is determined by the order in which the `RuntimeTasks` were executed in the `Runtime`.

**Yields:**

  Generator[object, None, None]: Generator object yielding the return data of the functions executed during
  task execution.

#### Runtime.gpu_count
 
The count of GPUs.

**Returns:**

 - `int`:  The number of GPUs

#### Runtime.gpus
 
GPU information as list. Each list entry contains information for one GPU.

**Returns:**

 - `list`:  List with GPU information.

#### Runtime.host
 
The host of the runtime.

**Returns:**

 - `str`:   The host of the runtime.

#### Runtime.info
 
Information about the runtime.

**Returns:**

 - `dict`:  Runtime information.

#### Runtime.memory
 
Information about the total memory in bytes.

**Returns:**

 - `str`:  Total memory in bytes.

#### Runtime.memory_in_mb
 
Memory information in mb.

**Returns:**

 - `str`:  Total memory in mega bytes.

#### Runtime.os
 
Operating system information.

**Returns:**

 - `str`:  OS.

#### Runtime.python_version
 
The installed python version.

**Returns:**

 - `str`:  Python version.

#### Runtime.task_processes
 
All processes that were started to execute a `RuntimeTask` asynchronously.

**Returns:**

  List[Process]: RuntimeTask processes.

#### Runtime.working_dir
 
The path of the working directory that was set during object initialization.

**Returns:**

 - `str`:  The path of thw working directory.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L472)</span>

### Runtime.`__init__`

```python
__init__(
    self,
    host:  str,
    working_dir:  Union[str,
    NoneType]  =  None,
    **connection_kwargs
)
```

Initialization method.

**Args:**

 - `host`:  The host of the `Runtime`.
 - `working_dir`:  The directory which shall act as workind directory. All individual Steps of a
  `RuntimeTask` will be executed relatively to this directory. Defaults to None.
  Consequently, a temporary directory will be created and used as working dir.
  If the working directory is a temporary one it will be cleaned up either
  `atexit` or when calling `cleanup()` manually.

 - `connection_kwargs`:  kwargs that will be passed on to the fabric connection. Please check the fabric docs
  for further details.

**Raises:**

 - `InvalidRuntimeError`:  If `Runtime` could not be instantiated successfully.


-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L943)</span>

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
) → bool
```

Checks the `Runtime` object for certain filter criteria.

**Args:**

 - `gpu_required`:  True, if gpu availability is required. Defaults to False.
 - `min_memory`:  The minimal amount of memory in MB. Defaults to None, i.e. not restricted.
 - `min_cpu_cores`:  The minimum number of cpu cores required. Defaults to None, i.e. not restricted.
 - `installed_executables`:  Possibility to check if an executable is installed. E.g. if the executable `ping` is
  installed.
 - `filter_commands`:  Shell commands that can be used for generic filtering. See examples. A filter command must
  echo true to be evaluated to True, everything else will be interpreted as False. Defaults
  to None.

**Returns:**

 - `bool`:  True, if all filters were successfully checked otherwise False.

**Examples:**

```python
# Check if the `Runtime` has a specific executable installed
# such as `ping` the network administration software utility.
check_passed = runtime.check_filter(installed_executables='ping')
# Check if a variable `WORKSPACE_VERSION` is set on the `Runtime`
filter_str = '[ ! -z "$WORKSPACE_VERSION" ] && echo "true" || echo "false"'
check_passed = runtime.check_filter(filer_commands=filter_str)
```
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L1051)</span>

### Runtime.cleanup

```python
cleanup(self)
```

Release all acquired resources and terminate all processes.
  
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L790)</span>

### Runtime.clear_tasks

```python
clear_tasks(self)
```

Clears all internal state related to `RuntimeTasks`.
  
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L1021)</span>

### Runtime.create_dir

```python
create_dir(self, path)
```

Create a directory. All folders in the path will be created if not existing.

**Args:**

 - `path`:  The full path of the directory to be created.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L1007)</span>

### Runtime.create_tempdir

```python
create_tempdir(self) → str
```

Create a temporary directory and return its name/path.

**Returns:**

 - `str`:  The name/path of the directory.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L1034)</span>

### Runtime.delete_dir

```python
delete_dir(self, path:  str) → bool
```

Delete a directory recursively. If at least one contained file could not be removed then False is returned.

**Args:**

 - `path`:  The full path of the directory to be deleted.

**Returns:**

 - `bool`:  True if the directory could be deleted successfully.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L743)</span>

### Runtime.execute_task

```python
execute_task(
    self,
    task:  lazycluster.runtimes.RuntimeTask,
    execute_async:  Union[bool,
    NoneType]  =  True,
    debug:  bool  =  False
)
```

Execute a given `RuntimeTask` in the `Runtime`.

**Args:**

 - `task`:  The task to be executed.
 - `execute_async`:  The execution will be done in a separate thread if True. Defaults to True.
 - `debug`:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then
  the stdout/stderr will be added to python logger with level debug after each task step.

**Raises:**

 - `TaskExecutionError`:  If an executed task step can't be executed successfully.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L827)</span>

### Runtime.expose_port_from_runtime

```python
expose_port_from_runtime(
    self,
    runtime_port:  int,
    local_port:  Union[int,
    NoneType]  =  None
) → str
```

Expose a port from a `Runtime` to localhost so that all traffic to the `local_port` is forwarded to the
`runtime_port` of the `Runtime`. This corresponds to local port forwarding in ssh tunneling terms.

**Args:**

 - `runtime_port`:  The port on the runtime.
 - `local_port`:  The port on the local machine. Defaults to `runtime_port`.

**Returns:**

 - `str`:  Process key, which can be used for manually stopping the process running the port exposure.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L797)</span>

### Runtime.expose_port_to_runtime

```python
expose_port_to_runtime(
    self,
    local_port:  int,
    runtime_port:  Union[int,
    NoneType]  =  None
) → str
```

Expose a port from localhost to the `Runtime` so that all traffic on the `runtime_port` is forwarded to the
`local_port` on localhost.

**Args:**

 - `local_port`:  The port on the local machine.
 - `runtime_port`:  The port on the runtime. Defaults to `local_port`.

**Returns:**

 - `str`:  Process key, which can be used for manually stopping the process running the port exposure for example.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L725)</span>

### Runtime.get_free_port

```python
get_free_port(self, ports:  List[int]) → int
```

Returns the first port from the list which is currently not in use in the `Runtime`.

**Args:**

 - `ports`:  The list of ports that will be used to check if the port is currently in use.

**Returns:**

 - `int`:  The first port from the list which is not yet used within the whole group.

**Raises:**

 - `NoPortsLeftError`:  If the port list is empty and no free port was found yet.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L857)</span>

### Runtime.get_process

```python
get_process(self, key:  str) → multiprocessing.context.Process
```

Get an individual process by process key.

**Args:**

 - `key`:  The key identifying the process.

**Returns:**

 - `Process`:  The desired process.

**Raises:**

 - `ValueError`:  Unknown process key.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L873)</span>

### Runtime.get_processes

```python
get_processes(
    self,
    only_alive:  bool  =  False
) → Dict[str, multiprocessing.context.Process]
```

Get all managed processes or only the alive ones as dictionary with the process key as dict key. An
individual process can be retrieved by key via `get_process()`.

**Args:**

 - `only_alive`:  True, if only alive processes shall be returned instead of all. Defaults to False.

**Returns:**

Dict[str, Process]: Dictionary with process keys as dict keys and the respective processes as dict values.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L908)</span>

### Runtime.has_free_port

```python
has_free_port(self, port:  int) → bool
```

Checks if the port is available on the runtime. 

**Args:**

 - `port`:  The port which will be checked.

**Returns:**

 - `bool`:  True if port is free, else False.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L693)</span>

### Runtime.is_valid_runtime

```python
is_valid_runtime(self) → bool
```

Checks if a given host is a valid `Runtime`.

**Returns:**

 - `bool`:  True, if it is a valid remote runtime.
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L924)</span>

### Runtime.print_info

```python
print_info(self)
```

Print the Runtime info formatted as table.
  
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L784)</span>

### Runtime.print_log

```python
print_log(self)
```

Print the execution logs of each `RuntimeTask` that was executed in the `Runtime`.
  
-------------------
<span style="float:right;">[[source]](/lazycluster/runtimes.py#L895)</span>

### Runtime.stop_process

```python
stop_process(self, key:  str)
```

Stop a process by its key. 

**Args:**

 - `key`:  The key identifying the process.

**Raises:**

 - `ValueError`:  Unknown process key.


