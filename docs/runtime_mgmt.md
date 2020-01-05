
**Source:** [/lazycluster/runtime_mgmt.py#L0](/lazycluster/runtime_mgmt.py#L0)


-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L16)</span>

## RuntimeGroup class

A `RuntimeGroup` is the representation of logically related `Runtimes` and provides convenient methods for

managing those related `Runtimes`. Most methods are wrappers around their counterparts in the `Runtime` class.

Typical usage examples are exposing a port (i.e. a service such as a DB) in the `RuntimeGroup`, transfer files, or

execute  a `RuntimeTask` on the contained `Runtimes`. Additionally, all concrete RuntimeCluster

(e.g. HyperoptCluster) implementations rely on `RuntimeGroups` for example.



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

  A DB is running on localhost on port `local_port` and the DB is only accessible

  from localhost. But you also want to access the service on the other `Runtimes` on port

  `runtime_port`. Then you can use this method to expose the service which is running on the

  local machine to the remote machines.

  ```python

  # Expose a port to all Runtimes contained in the Runtime. If a port list is given the next free port is

  # chosen and returned.

  group_port = group.expose_port_to_runtimes(local_port=60000, runtime_port=list(range(60000,60010)))

  print('Local port 60000 is now exposed to port ' + str(group_port) + ' in the RuntimeGroup!')

  ```

  A DB is running on a remote host on port `runtime_port` and the DB is only accessible from the remote

  machine itself. But you also want to access the service to other `Runtimes` in the group. Then you can use

  this method to expose the service which is running on one `Runtime` to the whole group.

  ```python

  # Expose a port from a Runtime to all other ones in the RuntimeGroup. If a port list is given the next

  # free port is chosen and returned.

  group_port = group.expose_port_from_runtime_to_group(host='host-1', runtime_port=60000,

  group_port=list(range(60000,60010)))

  print('Port 60000 of `host-1` is now exposed to port ' + str(group_port) + ' in the RuntimeGroup!')

  ```


#### RuntimeGroup.function_returns
 
Function return data. Blocks thread until a `RuntimeTasks` finished executing and gives back the return data

of the remotely executed python functions. The data is returned in the same order as the Tasks were started.



**Note:**


  Only function returns from `RuntimeTasks` that were started via the `RuntimeGroup` will be returned. If a

  contained `Runtime` executed further tasks directly, then those data will only be returned when querying the

  respective task directly.



**Returns:**


  Generator[object, None, None]: The unpickled return data.


#### RuntimeGroup.hosts
 
Contained hosts in the group.



**Returns:**


  List[str]: List with hosts of all `Runtimes`.


#### RuntimeGroup.runtime_count
 
The count of runtimes contained in the group.



**Returns:**


 - `int`:  The count.


#### RuntimeGroup.runtimes
 
Contained Runtimes in the group.



**Returns:**


  List[Runtime]: List with all `Runtimes`.


#### RuntimeGroup.task_processes
 
Processes from all contained `Runtimes` which were started to execute a `RuntimeTask`.



**Returns:**


  List[Process]: Process list.


-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L67)</span>

### RuntimeGroup.`__init__`

```python
__init__(
    self,
    runtimes:  Union[List[lazycluster.runtimes.Runtime],
    NoneType]  =  None,
    hosts:  Union[List[str],
    NoneType]  =  None
)
```

Initialization method.



**Args:**


 - `runtimes`:  List of `Runtimes`. If not given, then `hosts` must be supplied.

 - `hosts`:  List of hosts, which will be used to instantiate `Runtime` objects. If not given, then `runtimes`

  must be supplied.

**Raises:**


 - `ValueError`:  Either `runtimes` or `hosts` must be supplied. Not both or none.

 - `InvalidRuntimeError`:  If a runtime cannot be instantiated via host.



-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L176)</span>

### RuntimeGroup.add_env_variables

```python
add_env_variables(self, env_variables:  Dict)
```

Update the environment variables of all contained Runtimes. If a variable already

exists it gets updated and if not it will be added.



**Note:**


  This is a convenient wrapper and internally calls Runtime.add_env_variables().



**Args:**


 - `env_variables`:  The env variables used for the update.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L238)</span>

### RuntimeGroup.add_runtime

```python
add_runtime(
    self,
    host:  Union[str,
    NoneType]  =  None,
    runtime:  Union[lazycluster.runtimes.Runtime,
    NoneType]  =  None
)
```

Add a `Runtime` to the group either by host or as a `Runtime` object.



**Args:**


 - `host`:  The host of the runtime. Defaults to None.

 - `runtime`:  The `Runtime` object to be added to the group. Defaults to None.



**Raises:**


 - `ValueError`:  If the same host is already contained. Or if both host and runtime is given. We refuse

  the temptation to guess. Also if no argument is supplied.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L639)</span>

### RuntimeGroup.cleanup

```python
cleanup(self)
```

Release all acquired resources and terminate all processes by calling the cleanup method on all contained

`Runtimes`.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L565)</span>

### RuntimeGroup.clear_tasks

```python
clear_tasks(self)
```

Clears all internal state related to `RuntimeTasks`.

  

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L554)</span>

### RuntimeGroup.contains_runtime

```python
contains_runtime(self, host:  str) → bool
```

Check if the group contains a `Runtime` identified by host.



**Args:**


 - `host`:  The `Runtime` to be looked for.



**Returns:**


 - `bool`:  True if runtime is contained in the group, else False.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L389)</span>

### RuntimeGroup.execute_task

```python
execute_task(
    self,
    task:  lazycluster.runtimes.RuntimeTask,
    host:  Union[str,
    NoneType]  =  None,
    broadcast:  bool  =  False,
    execute_async:  bool  =  True,
    debug:  bool  =  False
) → lazycluster.runtimes.RuntimeTask
```

Execute a `RuntimeTask` in the whole group or in a single `Runtime`.



**Note:**


  When broadcasting a task in the group then actually deep copies of the RuntimeTask are created (by using

  its custom __deepcopy__ implementation), since each task holds state related to its own execution. Thus,

  multiple tasks will be returned in this case.



**Args:**


 - `task`:  The task to be executed.

 - `host`:  If task should be executed in one Runtime. Optionally, the host could be set in order to ensure

  the execution in a specific Runtime. Defaults to None. Consequently, the least busy `Runtime` will be

  chosen.

 - `broadcast`:  True, if the task will be executed on all `Runtimes`. Defaults to False.

 - `execute_async`:  True, if execution will take place async. Defaults to True.

 - `debug`:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then

  the stdout/stderr will be added to python logger with level debug after each task step. Defaults to

  `False`.



**Returns:**


RuntimeTask or List[RuntimeTask]: Either a single `RuntimeTask` object in case the execution took place

  in a single `Runtime` or a list of `RuntimeTasks` if executed in all.



**Raises:**


 - `ValueError`:  If `host` is given and not contained as `Runtime` in the group.

 - `TaskExecutionError`:  If an executed task step can't be executed successfully.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L326)</span>

### RuntimeGroup.expose_port_from_runtime_to_group

```python
expose_port_from_runtime_to_group(
    self,
    host:  str,
    runtime_port:  int,
    group_port:  Union[int,
    List[int],
    NoneType]  =  None
) → int
```

Expose a port from a `Runtime` to all other `Runtimes` in the `RuntimeGroup` so that all traffic to the

`group_port` is forwarded to the `runtime_port` of the runtime.



**Args:**


 - `host`:  The host of the `Runtime`.

 - `runtime_port`:  The port on the runtime.

 - `group_port`:  The port on the other runtimes where the `runtime_port` shall be exposed to. May raise

  PortInUseError if a single port is given. If a list is used to automatically find a free port

  then a NoPortsLeftError may be raised. Defaults to runtime_port.



**Returns:**


 - `int`:  The `group_port` that was eventually used.



**Raises:**


 - `ValueError`:  If host is not contained.

 - `PortInUseError`:  If `group_port` is occupied on the local machine.

 - `NoPortsLeftError`:  If `group_ports` was given and none of the ports was free.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L277)</span>

### RuntimeGroup.expose_port_to_runtimes

```python
expose_port_to_runtimes(
    self,
    local_port:  int,
    runtime_port:  Union[int,
    List[int],
    NoneType]  =  None,
    exclude_hosts:  Union[str,
    List[str],
    NoneType]  =  None
) → int
```

Expose a port from localhost to all Runtimes beside the excluded ones so that all traffic on the

`runtime_port` is forwarded to the `local_port` on the local machine. This corresponds to remote

port forwarding in ssh tunneling terms. Additionally, all relevant runtimes will be checked if the port is

actually free.



**Args:**


 - `local_port`:  The port on the local machine.

 - `runtime_port`:  The port on the runtimes where the `local_port` shall be exposed to. May raise PortInUseError

  if a single port is given. If a list is used to automatically find a free port then a

  NoPortsLeftError may be raised. Defaults to `local_port`.

 - `exclude_hosts`:  List with hosts where the port should not be exposed to. Defaults to None. Consequently, all

  `Runtimes` will be considered.



**Returns:**


 - `int`:  The port which was actually exposed to the `Runtimes`.



**Raises:**


 - `PortInUseError`:  If `runtime_port` is already in use on at least one Runtime.

 - `ValueError`:  Only hosts or `exclude_hosts` must be provided or host is not contained in the group.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L210)</span>

### RuntimeGroup.fill_runtime_info_buffers_async

```python
fill_runtime_info_buffers_async(self)
```

Trigger the reading of runtime information asynchronously and buffer the result.



**Note:**


  The actual reading of `Runtime.info data takes place when requesting the attribute the first time.

  Consequently, the result gets buffered in the respective Runtime instance. The actual reading of the data

  takes places on the remote host takes some seconds. This method enables you to read the information in

  seperate processes so that the execution time stays more or less the same independent of the actual amount

  of Runtimes used.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L500)</span>

### RuntimeGroup.get_free_port

```python
get_free_port(
    self,
    ports:  List[int],
    enforce_check_on_localhost:  bool  =  False
) → int
```

Return the first port from the list which is currently not in use in the whole group.



**Args:**


 - `ports`:  The list of ports that will be used to find a free port in the group.

 - `enforce_check_on_localhost`:  If true the port check will be executed on localhost as well, although

  localhost might not be a `Runtime` instance contained in the `RuntimeGroup`.



**Returns:**


 - `int`:  The first port from the list which is not yet used within the whole group.



**Raises:**


 - `NoPortsLeftError`:  If the port list is empty and no free port was found yet.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L576)</span>

### RuntimeGroup.get_runtime

```python
get_runtime(
    self,
    host:  Union[str,
    NoneType]  =  None
) → lazycluster.runtimes.Runtime
```

Returns a runtime identified by the `host` or 'the least busy one' will be returned if not host is given,

i.e. the one with the fewest alive processes executing a `RuntimeTask`.



**Note:**


  The current behavior of the 'least busy runtime' is intended to be changed to a smarter approach as soon as

  there will be the concrete need. So feel free to reach out to us or provide an alternative approach as PR.



**Args:**


 - `host`:  The host which identifies the runtime.



**Returns:**


 - `Runtime`:  Runtime object.



**Raises:**


 - `ValueError`:  Hostname is not contained in the group.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L600)</span>

### RuntimeGroup.get_runtimes

```python
get_runtimes(
    self,
    include_hosts:  Union[str,
    List[str],
    NoneType]  =  None,
    exclude_hosts:  Union[str,
    List[str],
    NoneType]  =  None
) → Dict[str, lazycluster.runtimes.Runtime]
```

Convenient methods for getting relevant `Runtimes` contained in the group.



**Args:**


 - `include_hosts`:  If supplied, only the specified `Runtimes` will be

  returned. Defaults to None, i.e. not restricted.

 - `exclude_hosts`:  If supplied, all `Runtimes` beside the here specified ones will be returned. Defaults to an

  empty list, i.e. not restricted.

**Raises:**


 - `ValueError`:  If include_hosts and exclude_hosts is provided or if a host from `include_host` is not contained

  in the group.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L529)</span>

### RuntimeGroup.has_free_port

```python
has_free_port(
    self,
    port:  int,
    exclude_hosts:  Union[List[str],
    str,
    NoneType]  =  None
) → bool
```

Check if a given port is free on `Runtimes` contained in the group. The check can be restricted to a

specific subset of contained `Runtimes` by excluding some hosts.



**Args:**


 - `port`:  The port to be checked in the group.

 - `exclude_hosts`:  If supplied, the check will be omitted in these `Runtimes`. Defaults to None, i.e. not

  restricted.



**Returns:**


 - `bool`:  True if port is free on all `Runtimes`, else False.



**Raises:**


 - `ValueError`:  Only hosts or exclude_hosts must be provided or Hostname is

  not contained in the group.                     

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L486)</span>

### RuntimeGroup.join

```python
join(self)
```

Blocks until `RuntimeTasks` which were started via the `group.execute_task()` method terminated.

  

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L189)</span>

### RuntimeGroup.print_hosts

```python
print_hosts(self)
```

Print the hosts of the group.

  

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L493)</span>

### RuntimeGroup.print_log

```python
print_log(self)
```

Print the execution logs of the contained `Runtimes` that were executed in the group.

  

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L199)</span>

### RuntimeGroup.print_runtime_info

```python
print_runtime_info(self)
```

Print information of contained `Runtimes`.

  

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L264)</span>

### RuntimeGroup.remove_runtime

```python
remove_runtime(self, host:  str)
```

Remove a runtime from the group by host.



**Args:**


 - `host`:  The host of the `Runtime` to be removed from the group.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L452)</span>

### RuntimeGroup.send_file

```python
send_file(
    self,
    local_path:  str,
    remote_path:  Union[str,
    NoneType]  =  None,
    execute_async:  Union[bool,
    NoneType]  =  True
) → List[lazycluster.runtimes.RuntimeTask]
```

Send either a single file or a folder from localhost to all `Runtimes` of the group.



**Note:**


  This method is a convenient wrapper around the Runtime's send file functionality. See `Runtime.send_file()´

  for further details.



**Args:**


 - `local_path`:  Path to file on local machine.

 - `remote_path`:  Path on the `Runtime`. Defaults to the `Runtime.working_dir`. See

  `RuntimeTask.execute()` docs for further details.

 - `execute_async`:  Each individual sending will be done in a separate process if True. Defaults to True.



**Returns:**


List[RuntimeTask]: The tasks that were internally created by the respective `Runtimes`.



**Raises:**


 - `ValueError`:  If local_path is emtpy.

 - `TaskExecutionError`:  If an executed task step can't be executed successfully.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L164)</span>

### RuntimeGroup.set_env_variables

```python
set_env_variables(self, env_variables:  Dict)
```

Set environment variables used when executing a task.



**Note:**


  This is a convenient wrapper and internally uses Runtime.env_variables.



**Args:**


 - `env_variables`:  The env variables as dictionary.


-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L660)</span>

## RuntimeManager class

The `RuntimeManager` can be used for a simplified resource management, since it aims to automatically detect

valid `Runtimes` based on the ssh configuration. It can be used to create a `RuntimeGroup` based on the

automatically detected instances and possibly based on further filters such as GPU availability.


-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L666)</span>

### RuntimeManager.`__init__`

```python
__init__(self)
```

Initialization method.



**Raises:**


 - `NoRuntimeDetectedError`:  If no `Runtime` could be automatically detected.



-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L716)</span>

### RuntimeManager.create_group

```python
create_group(
    self,
    include_hosts:  Union[str,
    List[str],
    NoneType]  =  None,
    exclude_hosts:  Union[str,
    List[str],
    NoneType]  =  None,
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
    NoneType]  =  None,
    working_dir:  Union[str,
    NoneType]  =  None
) → lazycluster.runtime_mgmt.RuntimeGroup
```

Create a runtime group with either all detected `Runtimes` or with a subset thereof.



**Args:**


 - `include_hosts`:  Only these hosts will be included in the `RuntimeGroup`. Defaults to None, i.e. not

  restricted.

 - `exclude_hosts`:  If supplied, all detected `Runtimes` beside the here specified ones will be included in the

  group. Defaults to None, i.e. not restricted.

gpu_required): True, if gpu availability is required. Defaults to False.

 - `min_memory`:  The minimal amount of memory in MB. Defaults to None, i.e. not restricted.

 - `min_cpu_cores`:  The minimum number of cpu cores required. Defaults to None, i.e. not restricted.

 - `installed_executables`:  Possibility to only include `Runtimes` that have an specific executables installed.

 - `filter_commands`:  Shell commands that can be used for generic filtering.

 - `working_dir`:  The directory which shall act as working one. Defaults to None. See the `Runtime` docs for

  further details.



**Note:**


The filter criteria are passed through the `check_filter()` method of the `Runtime` class. See its

documentation for further details and examples.



**Returns:**


 - `RuntimeGroup`:  The created `RuntimeGroup`.



**Raises:**


 - `ValueError`:  Only hosts or excluded_hosts must be provided or Hostname is not contained in the group.

 - `NoRuntimesError`:  If no `Runtime` matches the filter criteria.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L786)</span>

### RuntimeManager.print_hosts

```python
print_hosts(self)
```

Print detected hosts incl. the inactive ones.



**Note:**


  Inactive means that the host is not reachable via ssh or the check vie Runtime.is_valid_runtime() failed.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L802)</span>

### RuntimeManager.print_inactive_hosts

```python
print_inactive_hosts(self)
```

Print the inactive hosts.



**Note:**


  Inactive means that the host is not reachable via ssh or the check vie Runtime.is_valid_runtime() failed.

-------------------
<span style="float:right;">[[source]](/lazycluster/runtime_mgmt.py#L770)</span>

### RuntimeManager.print_runtime_info

```python
print_runtime_info(self)
```

Print detailed information of detected `Runtimes` and moreover the names of inactive hosts.



**Note:**


  Inactive means that the host is not reachable via ssh or the check vie Runtime.is_valid_runtime() failed.



