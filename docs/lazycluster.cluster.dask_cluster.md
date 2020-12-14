<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/dask_cluster.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `lazycluster.cluster.dask_cluster`
Module for conveniently managing a [DASK](http://distributed.dask.org) cluster. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/dask_cluster.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LocalMasterLauncher`
Concrete implementation of the `MasterLauncher` interface. See its documentation to get a list of the inherited methods and attributes. 

This class implements the logic for starting a the DASK master instance (i.e. scheduler in DASK terms) on localhost. 


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

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/dask_cluster.py#L92"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `cleanup`

```python
cleanup() → None
```

Release all resources. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/dask_cluster.py#L21"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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
 
 - <b>`ports`</b>:  Port where the master should be started. If a list is given then the first port that is free in the  `RuntimeGroup` will be used. The actual chosen port can be requested via the property `port`. 
 - <b>`timeout`</b>:  Timeout (s) after which an MasterStartError is raised if master instance not started yet. 
 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then  the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to  `False`. 



**Returns:**
 
 - <b>`List[int]`</b>:  In case a port list was given the updated port list will be returned. Otherwise an empty list. 



**Raises:**
 
 - <b>`PortInUseError`</b>:  If a single port is given and it is not free in the `RuntimeGroup`. 
 - <b>`NoPortsLeftError`</b>:  If a port list was given and none of the ports is actually free in the `RuntimeGroup`. 
 - <b>`MasterStartError`</b>:  If master was not started after the specified `timeout`. 


---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/dask_cluster.py#L98"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RoundRobinLauncher`
WorkerLauncher implementation for launching DASK workers in a round robin manner. See its documentation to get a list of the inherited methods and attributes. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/dask_cluster.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(runtime_group: RuntimeGroup)
```

Initialization method. 



**Args:**
 
 - <b>`runtime_group`</b>:  The group where the workers will be started. 


---

#### <kbd>property</kbd> ports_per_host

Dictionary with the host as key and a port list as value. The list contains all ports where a worker instance is reachable on the respective host. 



**Returns:**
 
 - <b>`Dict[str, List[int]]`</b>:  The ports per host as a dictionary. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/dask_cluster.py#L211"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `cleanup`

```python
cleanup() → None
```

Release all resources. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/dask_cluster.py#L112"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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
 - <b>`ports`</b>:  The ports to be used for starting the workers. Only ports from the list will be chosen  that are actually free. 
 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then  the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to  `False`. 



**Returns:**
 
 - <b>`List[int]`</b>:  The updated port list after starting the workers, i.e. the used ones were removed. 



**Raises:**
 
 - <b>`NoPortsLeftError`</b>:  If there are not enough free ports for starting all workers. 


---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/dask_cluster.py#L217"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `DaskCluster`
Convenient class for launching a Dask cluster in a `RuntimeGroup`. 

DaskCluster inherits from MasterWorkerCluster. See its documentation to get a list of the inherited methods and attributes. 

The number of DASK workers defaults to the number of `Runtimes` in the used `RuntimeGroup`. This number can be adjusted so that more or less workers than available `Runtimes` can be used. Per default the desired number of workers is started in a round robin way as implemented in `RoundRobinLauncher`. Consequently, this leads to an equal distribution of DASK workers in the `RuntimeGroup`. You can provide a custom implementation inheriting from the `WorkerLauncher` class in order to execute a different strategy how workers should be started. The DASK master (i.e. scheduler) will always be started on localhost as implemented in `LocalMasterLauncher`. This behavior can also be changed by providing a custom implementation inheriting from the `MasterLauncher`. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/dask_cluster.py#L235"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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
 
 - <b>`runtime_group`</b>:  The `RuntimeGroup` contains all `Runtimes` which can be used for starting the DASK entities. 
 - <b>`ports`</b>:  The list of ports which will be used to instantiate a cluster. Defaults to  `list(range(self.DEFAULT_PORT_RANGE_START, self.DEFAULT_PORT_RANGE_END))`. 
 - <b>`master_launcher`</b>:  Optionally, an instance implementing the `MasterLauncher` interface can be given, which  implements the strategy for launching the master instances in the cluster. If None, then  `LocalMasterLauncher` is used. 
 - <b>`worker_launcher`</b>:  Optionally, an instance implementing the `WorkerLauncher` interface can be given, which  implements the strategy for launching the worker instances. If None, then  `RoundRobinLauncher` is used. 


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

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/dask_cluster.py#L279"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `cleanup`

```python
cleanup() → None
```

Release all resources. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/dask_cluster.py#L266"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_client`

```python
get_client(timeout: int = 2) → Client
```

Get a connected Dask client. 



**Args:**
 
 - <b>`timeout`</b>:  The timeout (s) value passed on to the Dask `Client` constructor. Defaults to 2. 



**Raises:**
 
 - <b>`TimeoutError`</b>:  If client connection `timeout` expires. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
