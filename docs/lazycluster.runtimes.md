<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `lazycluster.runtimes`
Runtimes module. 

This module comprises classes for executing so called `RuntimeTasks` in `Runtimes` by leveraging the power of ssh. The `RuntimeTask` class is a container for defining a sequence of elegantly task steps. This `RuntimeTask` can then be executed either standalone or by passing it over to a `Runtime` instance. Passwordless ssh should be configured for all hosts that should act as a `Runtime` to be able to conveniently manage those entities. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RuntimeTask`
This class provides the functionality for executing a sequence of elementary operations over ssh. 

The [fabric](http://docs.fabfile.org/en/2.5/api/connection.html) library is used for handling ssh connections. A `RuntimeTask` can be composed from four different operations which we call steps, namely adding a step for running a shell command via `run_command()`, sending a file to a host via `send_file()`, retrieving a file from a host via `get_file()` or adding a step for executing a python function on a host via `run_function()`. The current restriction for running functions is that these functions need to be serializable via cloudpickle. To actually execute a `RuntimeTask`, i.e. the sequence of task steps, either a call to `execute()` is necessary or a handover to the `execute_task()` method of the `Runtime` class is necessary. Usually, a `RuntimeTask` or `RuntimeGroup` will be executed in a `Runtime` or in a `RuntimeGroup`. See its documentation for further details. 



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

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L66"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(name: Optional[str] = None)
```

Initialization method. 



**Args:**
 
 - <b>`name`</b>:  The name of the task. Defaults to None and consequently a unique identifier is generated via Python's  id() function. 


---

#### <kbd>property</kbd> env_variables

Environment parameters used when executing a task. 

---

#### <kbd>property</kbd> execution_log

The execution log as list. 

The list is empty as long as a task was not yet executed. Each log entry corresponds to a single task step and the log index starts at `0`. If th execution of an individual step does not produce and outut the list entry will be empty. 



**Returns:**
 
 - <b>`List[str]`</b>:  List with logs of the `RuntimeTask` execution. 

---

#### <kbd>property</kbd> execution_log_file_path

The execution log file path. This property is read-only and will be updated each time the `RuntimeTask` gets executed. 



**Returns:**
 
 - <b>`Optional[str]`</b>:  The path of the execution log. 

---

#### <kbd>property</kbd> function_returns

The return data produced by functions which were executed as a consequence of a `task.run_function()` call. 

Internally, a function return is saved as a pickled file. This method unpickles each file one after another and yields the data. Moreover, the return data will be yielded in the same order as the functions were executed. 



**Yields:**
 
 - <b>`Generator[object, None, None]`</b>:  Generator object yielding the return data of the functions executed during task execution. 

---

#### <kbd>property</kbd> process

The process object in which the task were executed. None, if not yet or synchronously executed. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L147"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `cleanup`

```python
cleanup() → None
```

Remove temporary used resources, like temporary directories if created. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L461"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute`

```python
execute(connection: Connection, debug: bool = False) → None
```

Execute the task on a remote host using a fabric connection. 



**Note:**

> Each individual task step will be executed relatively to the current directory of the fabric connection. Although, the current directory might have changed in the previous task step. Each directory change is temporary limited to a single task step. If the task gets executed via a `Runtime`, then the current directory will be the Runtimes working directory. See the `Runtime` docs for further details. Moreover, beside the regular Python log or the `debug` option you can access the execution logs via task.`execution.log`. The log gets updated after each task step. 
>

**Args:**
 
 - <b>`connection`</b>:  Fabric connection object managing the ssh connection to the remote host. 
 - <b>`debug `</b>:  If `True`, stdout/stderr from the remote host will be printed to stdout. If, `False`  then the stdout/stderr will be written to an execution log file. Defaults to `False`. 



**Raises:**
 
 - <b>`ValueError`</b>:  If cxn is broken and connection can not be established. 
 - <b>`TaskExecutionError`</b>:  If an executed task step can't be executed successfully. 
 - <b>`OSError`</b>:  In case of file transfer and non existent paths. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L259"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_file`

```python
get_file(remote_path: str, local_path: Optional[str] = None) → RuntimeTask
```

Create a task step for getting either a single file or a folder from another host to localhost. 



**Args:**
 
 - <b>`remote_path`</b>:  Path to file on host. 
 - <b>`local_path`</b>:  Path to file on local machine. The remote file is downloaded  to the current working directory  (as seen by os.getcwd) using its remote filename if local_path is None. This is the default  behavior of fabric. 



**Returns:**
 
 - <b>`RuntimeTask`</b>:  self. 



**Raises:**
 
 - <b>`ValueError`</b>:  If remote path is emtpy. 
 - <b>`OSError`</b>:  In case of non existent paths. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L572"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `join`

```python
join() → None
```

Block the execution until the `RuntimeTask` finished its asynchronous execution. 



**Note:**

> If self.omit_on_join is set, then the execution is omitted in order to prevent a deadlock. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L597"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_log`

```python
print_log() → None
```

Print the execution log. Each log entry will be printed separately. The log index will be prepended. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L289"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_command`

```python
run_command(command: str) → RuntimeTask
```

Create a task step for running a given shell command. 



**Args:**
 
 - <b>`command`</b>:  Shell command. 



**Returns:**
 
 - <b>`RuntimeTask`</b>:  self. 



**Raises:**
 
 - <b>`ValueError`</b>:  If command is emtpy. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L310"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_function`

```python
run_function(function: Callable[, Any], **func_kwargs: Any) → RuntimeTask
```

Create a task step for executing a given python function on a remote host. 

The function will be transferred to the remote host via ssh and cloudpickle. The return data can be requested via the property `function_returns`. 



**Note:**

> Hence, the function must be serializable via cloudpickle and all dependencies must be available in its correct versions on the remote host for now. We are planning to improve the dependency handling. 
>

**Args:**
 
 - <b>`function`</b>:  The function to be executed remotely. 
 - <b>`**func_kwargs`</b>:  kwargs which will be passed to the function. 



**Returns:**
 
 - <b>`RuntimeTask`</b>:  self. 



**Raises:**
 
 - <b>`ValueError`</b>:  If function is empty. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L231"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `send_file`

```python
send_file(local_path: str, remote_path: Optional[str] = None) → RuntimeTask
```

Create a task step for sending either a single file or a folder from localhost to another host. 



**Args:**
 
 - <b>`local_path`</b>:  Path to file on local machine. 
 - <b>`remote_path`</b>:  Path on the remote host. Defaults to the connection working directory. See  `RuntimeTask.execute()` docs for further details. 



**Returns:**
 
 - <b>`RuntimeTask`</b>:  self. 



**Raises:**
 
 - <b>`ValueError`</b>:  If local_path is emtpy. 


---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L818"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Runtime`
A `Runtime` is the logical representation of a remote host. 

Typically, the host is another server or a virtual machine / container on another server. This python class provides several methods for utilizing remote resources such as the port exposure from / to a `Runtime` as well as the execution of `RuntimeTasks`. A `Runtime` has a working directory. Usually, the execution of a `RuntimeTask` is conducted relatively to this directory if no other path is explicitly given. The working directory can be manually set during the initialization. Otherwise, a temporary directory gets created that might eventually be removed. 

A Runtime has a working directory (property: `working_dir`) which is a temporary directory per default and gets deleted `atexit` in this case. If you set this directory manually, either via `__init__()` or via the property `working_dir` then it won't be removed. Moreover, the working directory will also be set as environment variable on the Runtime. It is accessible via the env variable name stated in the constant `Runtime.WORKING_DIR_ENV_VAR_NAME`. This might be especially of interest when executing python functions remotely. 



**Note:**

> [Passwordless SSH access](https://linuxize.com/post/how-to-setup-passwordless-ssh-login/) should be be setup in advance. Otherwise the connection kwargs of fabric must be used for setting up the ssh connection. 
>

**Examples:**
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

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L861"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    host: str,
    working_dir: Optional[str] = None,
    connection_kwargs: Optional[Dict] = None
)
```

Initialization method. 



**Note:**

> The working directory will also be set as environment variable (see `Runtime.env_variables`) on the Runtime. It is accessible via the env variable name stated in the constant `Runtime.WORKING_DIR_ENV_VAR_NAME`. This might be especially of interest when executing functions remotely. 
>

**Args:**
 
 - <b>`host`</b>:  The host of the `Runtime`. 
 - <b>`working_dir`</b>:  The directory which shall act as working directory. If set, then the full path will be created  on the remote host in case it does not exist. All individual Steps of a `RuntimeTask` will be  executed relatively to this directory. Defaults to None. Consequently, a temporary directory  will be created and used as working dir. If the working directory is a temporary one it will be  cleaned up either `atexit` or when calling `cleanup()` manually. 


 - <b>`connection_kwargs`</b>:  kwargs that will be passed on to the fabric connection. Please check the fabric docs  for further details. 



**Raises:**
 
 - <b>`InvalidRuntimeError`</b>:  If `is_valid_runtime()` check fails. 
 - <b>`PathCreationError`</b>:  If the `working_dir` path could not be created successfully. 


---

#### <kbd>property</kbd> alive_process_count

The number of alive processes. 



**Returns:**
 
 - <b>`int`</b>:  The count. 

---

#### <kbd>property</kbd> alive_task_process_count

The number of alive processes which were started to execute a `RuntimeTask`. 



**Returns:**
 
 - <b>`int`</b>:  The count. 

---

#### <kbd>property</kbd> class_name

Getter for the class name as string. 



**Returns:**
 
 - <b>`str`</b>:  Class name. 

---

#### <kbd>property</kbd> cpu_cores

Information about the available CPUs. 

If you are in a container the CPU quota will be given if set. Otherwise, the number of physical CPUs on the host machine is given. 



**Raises:**
 
 - <b>`LazyclusterError`</b>:  Data could not be read succesfully. 



**Returns:**
 
 - <b>`int`</b>:  Number of CPU cores 

---

#### <kbd>property</kbd> env_variables

The environment variables for the Runtime. 

These variables are accessible on the Runtime and can be used when executing Python functions or shell commands. 



**Note:**

> The working directory is always accessible as environment variable on the Runtime. The respective variable name is given by the value of the constant `self.WORKING_DIR_ENV_VAR_NAME`. 

---

#### <kbd>property</kbd> function_returns

Return data of remote executed functions. 

The return data produced by Python functions which were executed as a consequence of `task.run_function()`. The call will be passed on to the `function_returns` property of the `RuntimeTask`. The order is determined by the order in which the `RuntimeTasks` were executed in the `Runtime`. 



**Yields:**
 
 - <b>`Generator[object, None, None]`</b>:  Generator object yielding the return data of the functions executed during  task execution. 

---

#### <kbd>property</kbd> gpu_count

The count of GPUs. 



**Returns:**
 
 - <b>`int`</b>:  The number of GPUs 

---

#### <kbd>property</kbd> gpus

GPU information as list. Each list entry contains information for one GPU. 



**Returns:**
 
 - <b>`list`</b>:  List with GPU information. 

---

#### <kbd>property</kbd> host

The host of the runtime. 



**Returns:**
 
 - <b>`str`</b>:   The host of the runtime. 

---

#### <kbd>property</kbd> info

Information about the runtime. 



**Returns:**
 
 - <b>`dict`</b>:  Runtime information. 

---

#### <kbd>property</kbd> memory

Information about the total memory in bytes. 



**Returns:**
 
 - <b>`str`</b>:  Total memory in bytes. 

---

#### <kbd>property</kbd> memory_in_mb

Memory information in mb. 



**Returns:**
 
 - <b>`int`</b>:  Total memory in mega bytes. 

---

#### <kbd>property</kbd> os

Operating system information. 



**Returns:**
 
 - <b>`str`</b>:  OS. 

---

#### <kbd>property</kbd> python_version

The installed python version. 



**Returns:**
 
 - <b>`str`</b>:  Python version. 

---

#### <kbd>property</kbd> task_processes

All processes that were started to execute a `RuntimeTask` asynchronously. 



**Returns:**
 
 - <b>`List[Process]`</b>:  RuntimeTask processes. 

---

#### <kbd>property</kbd> working_dir

The path of the working directory that was set during object initialization. 



**Note:**

> The working directory will also be set as environment variable on the Runtime. It is accessible via the env variable name stated in the constant `Runtime.WORKING_DIR_ENV_VAR_NAME`. This might be especially of interest when executing python functions remotely. Moreover, The full path will be created on the remote host in case it does not exist. 
>

**Returns:**
 
 - <b>`str`</b>:  The path of the working directory. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1169"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_env_variables`

```python
add_env_variables(env_variables: Dict) → None
```

Update the environment variables. If a variable already exists it gets updated and if not it will be added. 



**Args:**
 
 - <b>`env_variables`</b>:  The env variables used for the update. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1688"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `check_filter`

```python
check_filter(
    gpu_required: bool = False,
    min_memory: Optional[int] = None,
    min_cpu_cores: Optional[int] = None,
    installed_executables: Optional[str, List[str]] = None,
    filter_commands: Optional[str, List[str]] = None
) → bool
```

Checks the `Runtime` object for certain filter criteria. 



**Args:**
 
 - <b>`gpu_required`</b>:  True, if gpu availability is required. Defaults to False. 
 - <b>`min_memory`</b>:  The minimal amount of memory in MB. Defaults to None, i.e. not restricted. 
 - <b>`min_cpu_cores`</b>:  The minimum number of cpu cores required. Defaults to None, i.e. not restricted. 
 - <b>`installed_executables`</b>:  Possibility to check if an executable is installed. E.g. if the executable `ping` is  installed. 
 - <b>`filter_commands`</b>:  Shell commands that can be used for generic filtering. See examples. A filter command must  echo true to be evaluated to True, everything else will be interpreted as False. Defaults  to None. 



**Returns:**
 
 - <b>`bool`</b>:  True, if all filters were successfully checked otherwise False. 



**Examples:**
 ```python
    # Check if the `Runtime` has a specific executable installed
    # such as `ping` the network administration software utility.
    check_passed = runtime.check_filter(installed_executables='ping')
    # Check if a variable `WORKSPACE_VERSION` is set on the `Runtime`
    filter_str = '[ ! -z "$WORKSPACE_VERSION" ] && echo "true" || echo "false"'
    check_passed = runtime.check_filter(filer_commands=filter_str)
    ``` 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1838"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `cleanup`

```python
cleanup() → None
```

Release all acquired resources and terminate all processes. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1494"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `clear_tasks`

```python
clear_tasks() → None
```

Clears all internal state related to `RuntimeTasks`. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1779"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_dir`

```python
create_dir(path: str) → None
```

Create a directory. All folders in the path will be created if not existing. 



**Args:**
 
 - <b>`path`</b>:  The full path of the directory to be created. 



**Raises:**
 
 - <b>`PathCreationError`</b>:  If the path could not be created successfully. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1764"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_tempdir`

```python
create_tempdir() → str
```

Create a temporary directory and return its name/path. 



**Returns:**
 
 - <b>`str`</b>:  The name/path of the directory. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1799"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_dir`

```python
delete_dir(path: str) → bool
```

Delete a directory recursively. If at least one contained file could not be removed then False is returned. 



**Args:**
 
 - <b>`path`</b>:  The full path of the directory to be deleted. 



**Returns:**
 
 - <b>`bool`</b>:  True if the directory could be deleted successfully. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1865"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `echo`

```python
echo(msg: str) → str
```

Convenient method for echoing a string on the `Runtime` and returning the result. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1421"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute_function`

```python
execute_function(
    function: Callable[, Any],
    execute_async: bool = False,
    debug: bool = False,
    **func_kwargs: Any
) → RuntimeTask
```

Execute a Python function on the Runtime. 



**Note:**

> Internally, creates a RuntimeTask for executing the given python function on a remote host. The function will be transferred to the remote host via ssh and cloudpickle. The return data can be requested via the property `function_returns` of the Runtime or of the returned RuntimeTask. Hence, the function must be serializable via cloudpickle and all dependencies must be available in its correct versions on the Runtime. 
>

**Args:**
 
 - <b>`function`</b>:  The function to be executed remotely. 
 - <b>`execute_async`</b>:  The execution will be done in a separate process if True. Defaults to False. 
 - <b>`debug `</b>:  If `True`, stdout/stderr from the remote host will be printed to stdout. If, `False`  then the stdout/stderr will be written to execution log files. Defaults to `False`. 
 - <b>`**func_kwargs`</b>:  kwargs which will be passed to the function. 



**Returns:**
 
 - <b>`RuntimeTask`</b>:  self. 



**Raises:**
 
 - <b>`ValueError`</b>:  If function is empty. 
 - <b>`TaskExecutionError`</b>:  If there was an error during the execution. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1297"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute_task`

```python
execute_task(
    task: RuntimeTask,
    execute_async: Optional[bool] = True,
    omit_on_join: bool = False,
    debug: bool = False
) → None
```

Execute a given `RuntimeTask` in the `Runtime`. 



**Note:**

> Each execution will initialize the execution log of the `RuntimeTask`. 
>

**Args:**
 
 - <b>`task`</b>:  The RuntimeTask to be executed. 
 - <b>`execute_async`</b>:  The execution will be done in a separate process if True. Defaults to True. 
 - <b>`omit_on_join`</b>:  If True, then a call to join() won't wait for the termination of the corresponding process.  Defaults to False. This parameter has no effect in case of synchronous execution. 
 - <b>`debug `</b>:  If `True`, stdout/stderr from the remote host will be printed to stdout. If, `False`  then the stdout/stderr will be written to execution log files. Defaults to `False`. 



**Raises:**
 
 - <b>`TaskExecutionError`</b>:  If an executed task step can't be executed successfully. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1475"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execution_log`

```python
execution_log(task_name: str) → List[str]
```

Get the execution log of a `RuntimeTask` which was executed in the Runtime. 



**Args:**
 
 - <b>`task_name`</b> (str):  The name of the `RuntimeTask` 



**Raises:**
 
 - <b>`ValueError`</b>:  The RuntimeTask `task_name` was not executed on the Runtime 



**Returns:**
 
 - <b>`List[str]`</b>:  Execution log 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1548"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `expose_port_from_runtime`

```python
expose_port_from_runtime(
    runtime_port: int,
    local_port: Optional[int] = None
) → str
```

Expose a port from a `Runtime`. 

Expose a port from a `Runtime` to localhost so that all traffic to the `local_port` is forwarded to the `runtime_port` of the `Runtime`. This corresponds to local port forwarding in ssh tunneling terms. 



**Args:**
 
 - <b>`runtime_port`</b>:  The port on the runtime. 
 - <b>`local_port`</b>:  The port on the local machine. Defaults to `runtime_port`. 



**Returns:**
 
 - <b>`str`</b>:  Process key, which can be used for manually stopping the process running the port exposure. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1506"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `expose_port_to_runtime`

```python
expose_port_to_runtime(
    local_port: int,
    runtime_port: Optional[int] = None
) → str
```

Espose a port to a `Runtime`. 

Expose a port from localhost to the `Runtime` so that all traffic on the `runtime_port` is forwarded to the `local_port` on localhost. 



**Args:**
 
 - <b>`local_port`</b>:  The port on the local machine. 
 - <b>`runtime_port`</b>:  The port on the runtime. Defaults to `local_port`. 



**Returns:**
 
 - <b>`str`</b>:  Process key, which can be used for manually stopping the process running the port exposure for example. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1386"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_file`

```python
get_file(
    remote_path: str,
    local_path: Optional[str] = None,
    execute_async: Optional[bool] = False
) → RuntimeTask
```

Get either a single file or a folder from the Runtime to the manager. 



**Note:**

> This method is a convenient wrapper around the RuntimeTask's get file functionality. But it directly executes the file transfer in contrast to the get_file() method of the RuntimeTask. 
>

**Args:**
 
 - <b>`remote_path`</b>:  Path to file on host. 
 - <b>`local_path`</b>:  Path to file on local machine (i.e. manager). The remote file is downloaded  to the current  working directory (as seen by os.getcwd) using its remote filename if local_path is None.  This is the default behavior of fabric.Connection.get(). 
 - <b>`execute_async`</b>:  The execution will be done in a separate process if True. Defaults to False. 



**Returns:**
 
 - <b>`RuntimeTask`</b>:  self. 



**Raises:**
 
 - <b>`ValueError`</b>:  If remote path is emtpy. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1279"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_free_port`

```python
get_free_port(ports: List[int])
```

Returns the first port from the list which is currently not in use in the `Runtime`. 



**Args:**
 
 - <b>`ports`</b>:  The list of ports that will be used to check if the port is currently in use. 



**Returns:**
 
 - <b>`int`</b>:  The first port from the list which is not yet used within the whole group. 



**Raises:**
 
 - <b>`NoPortsLeftError`</b>:  If the port list is empty and no free port was found yet. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1590"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_process`

```python
get_process(key: str) → Process
```

Get an individual process by process key. 



**Args:**
 
 - <b>`key`</b>:  The key identifying the process. 



**Returns:**
 
 - <b>`Process`</b>:  The desired process. 



**Raises:**
 
 - <b>`ValueError`</b>:  Unknown process key. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1606"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_processes`

```python
get_processes(only_alive: bool = False) → Dict[str, Process]
```

Get all managed processes or only the alive ones as dictionary with the process key as dict key. 

An individual process can be retrieved by key via `get_process()`. 



**Args:**
 
 - <b>`only_alive`</b>:  True, if only alive processes shall be returned instead of all. Defaults to False. 



**Returns:**
 
 - <b>`Dict[str, Process]`</b>:  Dictionary with process keys as dict keys and the respective processes as dict values. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1644"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `has_free_port`

```python
has_free_port(port: int) → bool
```

Checks if the port is available on the runtime. 



**Args:**
 
 - <b>`port`</b>:  The port which will be checked. 



**Returns:**
 
 - <b>`bool`</b>:  True if port is free, else False. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1193"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `is_port_exposure_process`

```python
is_port_exposure_process(process_key: str) → bool
```

Check if the process manages a port exposure. 

Check if the process which belongs to the given `process_key` is used for exposing a port, i.e. keeping an ssh tunnel alive. 



**Args:**
 
 - <b>`process_key`</b> (str):  The generated process identifier. 



**Returns:**
 
 - <b>`bool`</b>:  True, if process is used for port exposure. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1177"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `is_runtime_task_process`

```python
is_runtime_task_process(process_key: str) → bool
```

Check if the process manages the `RuntimeTask` execution. 

Checks if the process which belongs to a given `process_key` was started to execute a `RuntimeTask` based on an internal naming scheme of the process keys. 



**Args:**
 
 - <b>`process_key`</b>:  The generated process identifier. 



**Returns:**
 
 - <b>`bool`</b>:  True, if process was started to execute a `RuntimeTask` 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1214"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_valid_runtime`

```python
is_valid_runtime() → bool
```

Checks if a given host is a valid `Runtime`. 



**Returns:**
 
 - <b>`bool`</b>:  True, if it is a valid remote runtime. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1830"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `join`

```python
join() → None
```

Blocks until `RuntimeTasks` which were started via the `runtime.execute_task()` method terminated. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1665"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_info`

```python
print_info() → None
```

Print the Runtime info formatted as table. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1470"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_log`

```python
print_log() → None
```

Print the execution logs of each `RuntimeTask` that was executed in the `Runtime`. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1350"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `send_file`

```python
send_file(
    local_path: str,
    remote_path: Optional[str] = None,
    execute_async: Optional[bool] = False
) → RuntimeTask
```

Send either a single file or a folder from the manager to the Runtime. 



**Note:**

> This method is a convenient wrapper around the RuntimeTask's send file functionality. But it directly executes the file transfer in contrast to the send_file() method of the RuntimeTask. 
>

**Args:**
 
 - <b>`local_path`</b>:  Path to file on local machine. 
 - <b>`remote_path`</b>:  Path on the Runtime. Defaults to the self.working_dir. See  `RuntimeTask.execute()` docs for further details. 
 - <b>`execute_async`</b>:  The execution will be done in a separate process if True. Defaults to False. 



**Returns:**
 
 - <b>`RuntimeTask`</b>:  The task that were internally created for the file transfer. 



**Raises:**
 
 - <b>`ValueError`</b>:  If local_path is emtpy. 
 - <b>`TaskExecutionError`</b>:  If an executed task step can't be executed successfully. 
 - <b>`OSError`</b>:  In case of non existent paths.e 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtimes.py#L1630"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `stop_process`

```python
stop_process(key: str) → None
```

Stop a process by its key. 



**Args:**
 
 - <b>`key`</b>:  The key identifying the process. 



**Raises:**
 
 - <b>`ValueError`</b>:  Unknown process key. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
