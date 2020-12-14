<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `lazycluster.cluster.runtime_cluster`
Module comprising the abstract RuntimeCluster class with its related `launcher strategy` classes. 

Note: The design of the launcher classes follows the strategy pattern. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `MasterLauncher`
Abstract class for implementing the strategy for launching the master instance of the cluster. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(runtime_group: RuntimeGroup)
```

Initialization method. 



**Args:**
 
 - <b>`runtime_group`</b>:  The group where the workers will be started. 


---

#### <kbd>property</kbd> port

The port where the master instance is started on. Will be None if not yet started. 



**Returns:**
 
 - <b>`Optional[int]`</b>:  The master port. 

---

#### <kbd>property</kbd> process

The process object where the master instance was started in. 



**Returns:**
 
 - <b>`Optional[Popen]`</b>:  The process object or None if not yet started. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L83"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `cleanup`

```python
cleanup() → None
```

Release all resources. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `start`

```python
start(
    ports: Union[List[int], int],
    timeout: int = 3,
    debug: bool = False
) → List[int]
```

Launch a master instance. 



**Note:**

> If you create a custom subclass of MasterLauncher which will not start the master instance on localhost then you should pass the debug flag on to `execute_task()` of the `RuntimeGroup` or `Runtime` so that you can benefit from the debug feature of `RuntimeTask.execute()`. 
>

**Args:**
 
 - <b>`ports`</b>:  Port where the master should be started. If a list is given then the first port that is free in the  `RuntimeGroup` will be used. The actual chosen port can requested via the property `port`. 
 - <b>`timeout`</b>:  Timeout (s) after which an MasterStartError is raised if master instance not started yet. 
 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then  the stdout/stderr will be added to python logger with level debug after each task step. Defaults to  `False`. 



**Returns:**
 
 - <b>`List[int]`</b>:  In case a port list was given the updated port list will be returned. Otherwise an empty list. 



**Raises:**
 
 - <b>`PortInUseError`</b>:  If a single port is given and it is not free in the `RuntimeGroup`. 
 - <b>`NoPortsLeftError`</b>:  If a port list was given and none of the ports is actually free in the `RuntimeGroup`. 
 - <b>`MasterStartError`</b>:  If master was not started after the specified `timeout`. 


---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L90"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `WorkerLauncher`
Abstract class for implementing the strategy for launching worker instances within a RuntimeGroup. 

In order to implement a new concrete `WorkerLauncher` subclass you need to implement the start method. Please consider the comments of the start method because some internal variables need to be set in the concrete implementation. 

Moreover, the `setup_worker_ssh_tunnels()` method can be used to setup ssh tunnels so that all entities can talk to each other. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(runtime_group: RuntimeGroup)
```

Initialization method. 



**Args:**
 
 - <b>`runtime_group`</b>:  The group where the workers will be started in. 


---

#### <kbd>property</kbd> ports_per_host

Dictionary with the host as key and a port list as value. The list contains all ports where a worker instance is reachable on the respective host. 



**Returns:**
 
 - <b>`Dict[str, List[int]]`</b>:  The ports per host as a dictionary. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L176"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `cleanup`

```python
cleanup() → None
```

Release all resources. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L157"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `setup_worker_ssh_tunnels`

```python
setup_worker_ssh_tunnels() → None
```

Set up ssh tunnel for workers such that all communication is routed over the local machine and all entities can talk to each other on localhost. 



**Note:**

> This method needs to be called if the communication between the worker instances is necessary, e.g. in case of DASK or Apache Flink, where data needs to be shuffled between the different entities. 
>

**Raises:**
 
 - <b>`ValueError`</b>:  If host is not contained. 
 - <b>`PortInUseError`</b>:  If `group_port` is occupied on the local machine. 
 - <b>`NoPortsLeftError`</b>:  If `group_ports` was given and none of the ports was free. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L129"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `start`

```python
start(
    worker_count: int,
    master_port: int,
    ports: List[int],
    debug: bool = False
) → List[int]
```

Launches the worker instances in the `RuntimeGroup`. 



**Args:**
 
 - <b>`worker_count`</b>:  The number of worker instances to be started in the group. 
 - <b>`master_port`</b>:   The port of the master instance. 
 - <b>`ports`</b>:  The ports to be used for starting the workers. Only ports from the list will be chosen that are  actually free. 
 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then  the stdout/stderr will be added to python logger with level debug after each task step. Defaults to  `False`. 



**Returns:**
 
 - <b>`List[int]`</b>:  The updated port list after starting the workers, i.e. the used ones were removed. 



**Raises:**
 
 - <b>`NoPortsLeftError`</b>:  If there are not enough free ports for starting all workers. 


---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L182"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RuntimeCluster`
Abstract cluster class. 

All further cluster implementations should inherit from this class either directly (e.g. the abstract class `MasterWorkerCluster`) or indirectly (e.g. the DaskCluster which is an concrete implementation of the `MasterWorkerCluster`). 





---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L194"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `MasterWorkerCluster`
Class for clusters following a master-worker architecture. 

Usually you want to inherit from this class and do not want to use it directly. It is recommended to treat this class as an abstract class or an interface. 



**Examples:**
  Create a cluster with all `Runtimes` detected by the `RuntimeManager`. 

```python
     from lazycluster import RuntimeManager
     cluster = MyMasterWorkerClusterImpl(RuntimeManager().create_group())
     cluster.start()
    ``` 

 Use different strategies for launching the master and the worker instance as the default ones by providing  custom implementation of `MasterLauncher` and `WorkerLauncher`. 

```python
     cluster = MyMasterWorkerClusterImpl(RuntimeManager().create_group(),
                                         MyMasterLauncherImpl(),
                                         MyWorkerLauncherImpl()
     cluster.start()
    ``` 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L224"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    runtime_group: RuntimeGroup,
    ports: Optional[List[int]] = None,
    master_launcher: Optional[MasterLauncher] = None,
    worker_launcher: Optional[WorkerLauncher] = None
)
```

Initialization method. 



**Args:**
 
 - <b>`runtime_group`</b>:  The `RuntimeGroup` contains all `Runtimes` which can be used for starting the cluster  entities. 
 - <b>`ports`</b>:  The list of ports which will be used to instantiate a cluster. Defaults to  `list(range(self.DEFAULT_PORT_RANGE_START, self.DEFAULT_PORT_RANGE_END)`. 
 - <b>`master_launcher`</b>:  Optionally, an instance implementing the `MasterLauncher` interface can be given, which  implements the strategy for launching the master instances in the cluster. If None, then  the default of the concrete cluster implementation will be chosen. 
 - <b>`worker_launcher`</b>:  Optionally, an instance implementing the `WorkerLauncher` interface can be given, which  implements the strategy for launching the worker instances. If None, then the default of  the concrete cluster implementation will be chosen. 


---

#### <kbd>property</kbd> master_port

The port where the master instance was started. None, if not yet started. 



**Returns:**
 
 - <b>`Optional[int]`</b>:  The master port. 

---

#### <kbd>property</kbd> runtime_group

The RuntimeGroup. 



**Returns:**
 
 - <b>`RuntimeGroup`</b>:  The used group. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L411"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `cleanup`

```python
cleanup() → None
```

Release all resources. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L402"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_log`

```python
print_log() → None
```

Print the execution log. 



**Note:**

> This method is a convenient wrapper for the equivalent method of the contained `RuntimeGroup`. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L283"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `start`

```python
start(
    worker_count: Optional[int] = None,
    master_port: Optional[int] = None,
    debug: bool = False
) → None
```

Convenient method for launching the cluster. 

Internally, `self.start_master()` and `self.start_workers()` will be called. 



**Args:**
 
 - <b>`master_port`</b>:  Port of the cluster master. Will be passed on to `self.start()`, hence see respective method  for further details. 
 - <b>`worker_count`</b>:  The number of worker instances to be started in the cluster. Will be passed on to  `self.start()`, hence see respective method for further details. 
 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then  the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to  `False`. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L307"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `start_master`

```python
start_master(
    master_port: Optional[int] = None,
    timeout: int = 3,
    debug: bool = False
) → None
```

Start the master instance. 



**Note:**

> How the master is actually started is determined by the the actual `MasterLauncher` implementation. Another implementation adhering to the `MasterLauncher` interface can be provided in the constructor of the cluster class. 
>

**Args:**
 
 - <b>`master_port`</b>:  Port of the master instance. Defaults to `self.DEFAULT_MASTER_PORT`, but another one is chosen if  the port is not free within the group. The actual chosen port can be requested via  self.master_port. 
 - <b>`timeout`</b>:  Timeout (s) after which an MasterStartError is raised if master instance not started yet. 
 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. Has no effect for  if the master instance is started locally, what default MasterLauncher implementations usually do. 



**Raises:**
 
 - <b>`PortInUseError`</b>:  If a single port is given and it is not free in the `RuntimeGroup`. 
 - <b>`NoPortsLeftError`</b>:  If there are no free ports left in the port list for instantiating the master. 
 - <b>`MasterStartError`</b>:  If master was not started after the specified `timeout`. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/runtime_cluster.py#L364"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `start_workers`

```python
start_workers(count: Optional[int] = None, debug: bool = False) → None
```

Start the worker instances. 



**Note:**

> How workers are actually started is determined by the the actual `WorkerLauncher` implementation. Another implementation adhering to the `WorkerLauncher` interface can be provided in the constructor of the cluster class. 
>

**Args:**
 
 - <b>`count`</b>:  The number of worker instances to be started in the cluster. Defaults to the number of runtimes in  the cluster. 
 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then  the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to  `False`. 



**Raises:**
 
 - <b>`NoPortsLeftError`</b>:  If there are no free ports left in the port list for instantiating new worker entities. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
