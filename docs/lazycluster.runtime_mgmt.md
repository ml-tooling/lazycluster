<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `lazycluster.runtime_mgmt`
Runtime management module. This module contains convenient classes for working with `Runtimes` and `RuntimeTasks`. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RuntimeGroup`
A `RuntimeGroup` is the representation of logically related `Runtimes`. 

The group provides convenient methods for managing those related `Runtimes`. Most methods are wrappers around their counterparts in the `Runtime` class. Typical usage examples are exposing a port (i.e. a service such as a DB) in the `RuntimeGroup`, transfer files, or execute  a `RuntimeTask` on the contained `Runtimes`. Additionally, all concrete RuntimeCluster (e.g. HyperoptCluster) implementations rely on `RuntimeGroups` for example. 



**Examples:**
 Execute a `RuntimeTask` in a `RuntimeGroup` 

```python
# Create instances
group = RuntimeGroup([Runtime('host-1'), Runtime('host-2')])
# group = RuntimeGroup(hosts=['host-1', 'host-2'])
my_task = RuntimeTask('group-demo').run_command('echo Hello Group!')

# Execute a RuntimeTask in a single Runtime
single_task = group.execute_task(my_task)
print(single_task.execution_log[0])

# Execute a RuntimeTask in the whole RuntimeGroup
task_list = group.execute_task(my_task, broadcast=True)

# Execute a RuntimeTask on a single Runtime contained in the RuntimeGroup
task = group.execute_task(my_task)
``` 

A DB is running on localhost on port `local_port` and the DB is only accessible from localhost. But you also want to access the service on the other `Runtimes` on port `runtime_port`. Then you can use this method to expose the service which is running on the local machine to the remote machines. 

```python
# Expose a port to all Runtimes contained in the Runtime. If a port list is given the next free port is
# chosen and returned.
group_port = group.expose_port_to_runtimes(local_port=60000, runtime_port=list(range(60000,60010)))
print('Local port 60000 is now exposed to port ' + str(group_port) + ' in the RuntimeGroup!')
``` 

A DB is running on a remote host on port `runtime_port` and the DB is only accessible from the remote machine itself. But you also want to access the service to other `Runtimes` in the group. Then you can use this method to expose the service which is running on one `Runtime` to the whole group. 

```python
# Expose a port from a Runtime to all other ones in the RuntimeGroup. If a port list is given the next
# free port is chosen and returned.
group_port = group.expose_port_from_runtime_to_group(host='host-1', runtime_port=60000,
                                                         group_port=list(range(60000,60010)))
print('Port 60000 of `host-1` is now exposed to port ' + str(group_port) + ' in the RuntimeGroup!')
``` 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    runtimes: Optional[List[Runtime]] = None,
    hosts: Optional[List[str]] = None,
    working_dir: Optional[str] = None
)
```

Initialization method. 



**Args:**
 
 - <b>`runtimes`</b>:  List of `Runtimes`. If not given, then `hosts` must be supplied. 
 - <b>`hosts`</b>:  List of hosts, which will be used to instantiate `Runtime` objects. If not given, then `runtimes`  must be supplied. 
 - <b>`working_dir`</b>:  The directory which shall act as working directory on all Runtimes. Defaults to None. See the `Runtime` docs for  further details. 



**Raises:**
 
 - <b>`ValueError`</b>:  Either `runtimes` or `hosts` must be supplied. Not both or none. 
 - <b>`InvalidRuntimeError`</b>:  If a runtime cannot be instantiated via host. 


---

#### <kbd>property</kbd> function_returns

Getter for function return data from a remote function execution. 

Blocks thread until a `RuntimeTasks` finished executing and gives back the return data of the remotely executed python functions. The data is returned in the same order as the Tasks were started. 



**Note:**

> Only function returns from `RuntimeTasks` that were started via the `RuntimeGroup` will be returned. If a contained `Runtime` executed further `RuntimeTasks` directly, then those data will only be returned when querying the respective `RuntimeTask` directly. 
>

**Returns:**
 
 - <b>`Generator[object, None, None]`</b>:  The unpickled return data. 

---

#### <kbd>property</kbd> hosts

Contained hosts in the group. 



**Returns:**
 
 - <b>`List[str]`</b>:  List with hosts of all `Runtimes`. 

---

#### <kbd>property</kbd> runtime_count

The count of runtimes contained in the group. 



**Returns:**
 
 - <b>`int`</b>:  The count. 

---

#### <kbd>property</kbd> runtimes

Contained Runtimes in the group. 



**Returns:**
 
 - <b>`List[Runtime]`</b>:  List with all `Runtimes`. 

---

#### <kbd>property</kbd> task_processes

Processes from all contained `Runtimes` which were started to execute a `RuntimeTask`. 



**Returns:**
 
 - <b>`List[Process]`</b>:  Process list. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L205"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_env_variables`

```python
add_env_variables(env_variables: Dict) → None
```

Update the environment variables of all contained Runtimes. 

If a variable already exists it gets updated and if not it will be added. 



**Note:**

> This is a convenient wrapper and internally calls Runtime.add_env_variables(). 
>

**Args:**
 
 - <b>`env_variables`</b>:  The env variables used for the update. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L274"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_runtime`

```python
add_runtime(
    host: Optional[str] = None,
    runtime: Optional[Runtime] = None
) → None
```

Add a `Runtime` to the group either by host or as a `Runtime` object. 



**Args:**
 
 - <b>`host`</b>:  The host of the runtime. Defaults to None. 
 - <b>`runtime`</b>:  The `Runtime` object to be added to the group. Defaults to None. 



**Raises:**
 
 - <b>`ValueError`</b>:  If the same host is already contained. Or if both host and runtime is given. We refuse  the temptation to guess. Also if no argument is supplied. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L781"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `cleanup`

```python
cleanup() → None
```

Release all acquired resources and terminate all processes by calling the cleanup method on all contained `Runtimes`. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L689"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `clear_tasks`

```python
clear_tasks() → None
```

Clears all internal state related to `RuntimeTasks`. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L678"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `contains_runtime`

```python
contains_runtime(host: str) → bool
```

Check if the group contains a `Runtime` identified by host. 



**Args:**
 
 - <b>`host`</b>:  The `Runtime` to be looked for. 



**Returns:**
 
 - <b>`bool`</b>:  True if runtime is contained in the group, else False. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L472"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute_task`

```python
execute_task(
    task: RuntimeTask,
    host: Optional[str] = None,
    broadcast: bool = False,
    execute_async: bool = True,
    omit_on_join: bool = False,
    debug: bool = False
) → Union[RuntimeTask, List[RuntimeTask]]
```

Execute a `RuntimeTask` in the whole group or in a single `Runtime`. 



**Note:**

> When broadcasting a `RuntimeTask` in the group then actually deep copies of the RuntimeTask are created (by using its custom __deepcopy__ implementation), since each RuntimeTask holds state related to its own execution. Thus, multiple `RuntimeTasks` will be returned in this case. 
>

**Args:**
 
 - <b>`task`</b>:  The RuntimeTask to be executed. 
 - <b>`host`</b>:  If `RuntimeTask` should be executed in one Runtime. Optionally, the host could be set in order to ensure  the execution in a specific Runtime. Defaults to None. Consequently, the least busy `Runtime` will be  chosen. 
 - <b>`broadcast`</b>:  True, if the `RuntimeTask` will be executed on all `Runtimes`. Defaults to False. 
 - <b>`execute_async`</b>:  True, if execution will take place async. Defaults to True. 
 - <b>`omit_on_join`</b>:  If True, then a call to join() won't wait for the termination of the corresponding process.  Defaults to False. This parameter has no effect in case of synchronous execution. 
 - <b>`debug `</b>:  If `True`, stdout/stderr from the remote host will be printed to stdout. If, `False`  then the stdout/stderr will be written to execution log files. Defaults to `False`. 



**Returns:**
 
 - <b>`RuntimeTask or List[RuntimeTask]`</b>:  Either a single `RuntimeTask` object in case the execution took place  in a single `Runtime` or a list of `RuntimeTasks` if executed in all. 



**Raises:**
 
 - <b>`ValueError`</b>:  If `host` is given and not contained as `Runtime` in the group. 
 - <b>`TaskExecutionError`</b>:  If an executed `RuntimeTask` step can't be executed successfully. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L392"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `expose_port_from_runtime_to_group`

```python
expose_port_from_runtime_to_group(
    host: str,
    runtime_port: int,
    group_port: Optional[int, List[int]] = None
)
```

Expose a port from a `Runtime` to all other `Runtimes` in the `RuntimeGroup`. 

All traffic to the `group_port` is forwarded to the `runtime_port` of the runtime. 



**Args:**
 
 - <b>`host`</b>:  The host of the `Runtime`. 
 - <b>`runtime_port`</b>:  The port on the runtime. 
 - <b>`group_port`</b>:  The port on the other runtimes where the `runtime_port` shall be exposed to. May raise  PortInUseError if a single port is given. If a list is used to automatically find a free port  then a NoPortsLeftError may be raised. Defaults to runtime_port. 



**Returns:**
 
 - <b>`int`</b>:  The `group_port` that was eventually used. 



**Raises:**
 
 - <b>`ValueError`</b>:  If host is not contained. 
 - <b>`PortInUseError`</b>:  If `group_port` is occupied on the local machine. 
 - <b>`NoPortsLeftError`</b>:  If `group_ports` was given and none of the ports was free. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L322"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `expose_port_to_runtimes`

```python
expose_port_to_runtimes(
    local_port: int,
    runtime_port: Optional[int, List[int]] = None,
    exclude_hosts: Optional[str, List[str]] = None
)
```

Expose a port from localhost to all Runtimes beside the excluded ones. 

All traffic on the `runtime_port` is forwarded to the `local_port` on the local machine. This corresponds to remote port forwarding in ssh tunneling terms. Additionally, all relevant runtimes will be checked if the port is actually free. 



**Args:**
 
 - <b>`local_port`</b>:  The port on the local machine. 
 - <b>`runtime_port`</b>:  The port on the runtimes where the `local_port` shall be exposed to. May raise PortInUseError  if a single port is given. If a list is used to automatically find a free port then a  NoPortsLeftError may be raised. Defaults to `local_port`. 
 - <b>`exclude_hosts`</b>:  List with hosts where the port should not be exposed to. Defaults to None. Consequently, all  `Runtimes` will be considered. 



**Returns:**
 
 - <b>`int`</b>:  The port which was actually exposed to the `Runtimes`. 



**Raises:**
 
 - <b>`PortInUseError`</b>:  If `runtime_port` is already in use on at least one Runtime. 
 - <b>`ValueError`</b>:  Only hosts or `exclude_hosts` must be provided or host is not contained in the group. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L238"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `fill_runtime_info_buffers_async`

```python
fill_runtime_info_buffers_async() → None
```

Trigger the reading of runtime information asynchronously and buffer the result. 



**Note:**

> The actual reading of `Runtime.info data takes place when requesting the attribute the first time. Consequently, the result gets buffered in the respective Runtime instance. The actual reading of the data takes places on the remote host and takes some seconds. This method enables you to read the information in a separate processes so that the execution time stays more or less the same independent of the actual amount of Runtimes used. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L604"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_free_port`

```python
get_free_port(ports: List[int], enforce_check_on_localhost: bool = False)
```

Return the first port from the list which is currently not in use in the whole group. 



**Args:**
 
 - <b>`ports`</b>:  The list of ports that will be used to find a free port in the group. 
 - <b>`enforce_check_on_localhost`</b>:  If true the port check will be executed on localhost as well, although  localhost might not be a `Runtime` instance contained in the `RuntimeGroup`. 



**Returns:**
 
 - <b>`int`</b>:  The first port from the list which is not yet used within the whole group. 



**Raises:**
 
 - <b>`NoPortsLeftError`</b>:  If the port list is empty and no free port was found yet. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L705"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_runtime`

```python
get_runtime(host: Optional[str] = None) → Runtime
```

Get a contained `Runtime`. 

A runtime identified by the `host` or 'the least busy one' will be returned if not host is given, i.e. the one with the fewest alive processes executing a `RuntimeTask`. 



**Note:**

> The current behavior of the 'least busy runtime' is intended to be changed to a smarter approach as soon as there will be the concrete need. So feel free to reach out to us or provide an alternative approach as PR. 
>

**Args:**
 
 - <b>`host`</b>:  The host which identifies the runtime. 



**Returns:**
 
 - <b>`Runtime`</b>:  Runtime object. 



**Raises:**
 
 - <b>`ValueError`</b>:  Hostname is not contained in the group. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L730"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_runtimes`

```python
get_runtimes(
    include_hosts: Optional[str, List[str]] = None,
    exclude_hosts: Optional[str, List[str]] = None
) → Dict[str, Runtime]
```

Convenient methods for getting relevant `Runtimes` contained in the group. 



**Args:**
 
 - <b>`include_hosts`</b>:  If supplied, only the specified `Runtimes` will be  returned. Defaults to None, i.e. not restricted. 
 - <b>`exclude_hosts`</b>:  If supplied, all `Runtimes` beside the here specified ones will be returned. Defaults to an  empty list, i.e. not restricted. 



**Raises:**
 
 - <b>`ValueError`</b>:  If include_hosts and exclude_hosts is provided or if a host from `include_host` is not contained  in the group. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L646"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `has_free_port`

```python
has_free_port(port: int, exclude_hosts: Optional[List[str], str] = None) → bool
```

Check if a given port is free on `Runtimes` contained in the group. 

The check can be restricted to a specific subset of contained `Runtimes` by excluding some hosts. 



**Args:**
 
 - <b>`port`</b>:  The port to be checked in the group. 
 - <b>`exclude_hosts`</b>:  If supplied, the check will be omitted in these `Runtimes`. Defaults to None, i.e. not  restricted. 



**Returns:**
 
 - <b>`bool`</b>:  True if port is free on all `Runtimes`, else False. 



**Raises:**
 
 - <b>`ValueError`</b>:  Only hosts or exclude_hosts must be provided or Hostname is  not contained in the group. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L590"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `join`

```python
join() → None
```

Blocks until `RuntimeTasks` which were started via the `group.execute_task()` method terminated. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L219"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_hosts`

```python
print_hosts() → None
```

Print the hosts of the group. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L598"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_log`

```python
print_log() → None
```

Print the execution logs of the contained `Runtimes` that were executed in the group. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L228"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_runtime_info`

```python
print_runtime_info() → None
```

Print information of contained `Runtimes`. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L309"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove_runtime`

```python
remove_runtime(host: str) → None
```

Remove a runtime from the group by host. 



**Args:**
 
 - <b>`host`</b>:  The host of the `Runtime` to be removed from the group. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L549"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `send_file`

```python
send_file(
    local_path: str,
    remote_path: Optional[str] = None,
    execute_async: Optional[bool] = True
) → List[RuntimeTask]
```

Send either a single file or a folder from the manager to all `Runtimes` of the group. 



**Note:**

> This method is a convenient wrapper around the Runtime's send file functionality. See `Runtime.send_file()´ for further details. 
>

**Args:**
 
 - <b>`local_path`</b>:  Path to file on local machine. 
 - <b>`remote_path`</b>:  Path on the `Runtime`. Defaults to the `Runtime.working_dir`. See  `RuntimeTask.execute()` docs for further details. 
 - <b>`execute_async`</b>:  Each individual sending will be done in a separate process if True. Defaults to True. 



**Returns:**
 
 - <b>`List[RuntimeTask]`</b>:  The `RuntimeTasks` that were internally created by the respective `Runtimes`. 



**Raises:**
 
 - <b>`ValueError`</b>:  If local_path is emtpy. 
 - <b>`TaskExecutionError`</b>:  If an executed `RuntimeTask` step can't be executed successfully. 
 - <b>`OSError`</b>:  In case of non existent paths. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L193"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_env_variables`

```python
set_env_variables(env_variables: Dict) → None
```

Set environment variables used when executing a task. 



**Note:**

> This is a convenient wrapper and internally uses Runtime.env_variables. 
>

**Args:**
 
 - <b>`env_variables`</b>:  The env variables as dictionary. 


---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L800"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RuntimeManager`
The `RuntimeManager` can be used for a simplified resource management. 

It aims to automatically detect valid `Runtimes` based on the ssh configuration. It can be used to create a `RuntimeGroup` based on the automatically detected instances and possibly based on further filters such as GPU availability. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L808"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__() → None
```

Initialization method. 



**Raises:**
 
 - <b>`NoRuntimeDetectedError`</b>:  If no `Runtime` could be automatically detected. 




---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L867"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_group`

```python
create_group(
    include_hosts: Optional[str, List[str]] = None,
    exclude_hosts: Optional[str, List[str]] = None,
    gpu_required: bool = False,
    min_memory: Optional[int] = None,
    min_cpu_cores: Optional[int] = None,
    installed_executables: Optional[str, List[str]] = None,
    filter_commands: Optional[str, List[str]] = None,
    working_dir: Optional[str] = None
) → RuntimeGroup
```

Create a runtime group with either all detected `Runtimes` or with a subset thereof. 



**Args:**
 
 - <b>`include_hosts`</b>:  Only these hosts will be included in the `RuntimeGroup`. Defaults to None, i.e. not  restricted. 
 - <b>`exclude_hosts`</b>:  If supplied, all detected `Runtimes` beside the here specified ones will be included in the  group. Defaults to None, i.e. not restricted. 
 - <b>`gpu_required`</b>:  True, if gpu availability is required. Defaults to False. 
 - <b>`min_memory`</b>:  The minimal amount of memory in MB. Defaults to None, i.e. not restricted. 
 - <b>`min_cpu_cores`</b>:  The minimum number of cpu cores required. Defaults to None, i.e. not restricted. 
 - <b>`installed_executables`</b>:  Possibility to only include `Runtimes` that have an specific executables installed. 
 - <b>`filter_commands`</b>:  Shell commands that can be used for generic filtering. 
 - <b>`working_dir`</b>:  The directory which shall act as working one. Defaults to None. See the `Runtime` docs for  further details. 



**Note:**

> The filter criteria are passed through the `check_filter()` method of the `Runtime` class. See its documentation for further details and examples. 
>

**Returns:**
 
 - <b>`RuntimeGroup`</b>:  The created `RuntimeGroup`. 



**Raises:**
 
 - <b>`ValueError`</b>:  Only hosts or excluded_hosts must be provided or Hostname is not contained in the group. 
 - <b>`NoRuntimesError`</b>:  If no `Runtime` matches the filter criteria or none could be detected. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L975"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_hosts`

```python
print_hosts() → None
```

Print detected hosts incl. the inactive ones. 



**Note:**

> Inactive means that the host is not reachable via ssh or the check vie Runtime.is_valid_runtime() failed. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L993"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_inactive_hosts`

```python
print_inactive_hosts() → None
```

Print the inactive hosts. 



**Note:**

> Inactive means that the host is not reachable via ssh or the check vie Runtime.is_valid_runtime() failed. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/runtime_mgmt.py#L957"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_runtime_info`

```python
print_runtime_info() → None
```

Print detailed information of detected `Runtimes` and moreover the names of inactive hosts. 



**Note:**

> Inactive means that the host is not reachable via ssh or the check vie Runtime.is_valid_runtime() failed. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
