<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `lazycluster.cluster.hyperopt_cluster`
Module for conveniently managing a [Hyperopt](https://github.com/hyperopt/hyperopt) cluster. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `MongoLauncher`
Abstract implementation of the `MasterLauncher` interface used to implement a concrete launch strategy for mongodb instance used in hyperopt. 

This class implements the logic for starting a MongoDB instance on localhost. Hence, we simply treat the MongoDB instance as master node. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L21"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LocalMongoLauncher`
Concrete implementation of the `MasterLauncher` interface. See its documentation to get a list of the inherited methods and attributes. 

This class implements the logic for starting a MongoDB instance on localhost. Hence, we simply treat the MongoDB instance as master node. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L21"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L141"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `cleanup`

```python
cleanup() → None
```

Release all resources. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L122"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_mongod_start_cmd`

```python
get_mongod_start_cmd() → str
```

Get the shell command for starting mongod as a deamon process. 



**Returns:**
 
 - <b>`str`</b>:  The shell command. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L133"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_mongod_stop_cmd`

```python
get_mongod_stop_cmd() → str
```

Get the shell command for stopping the currently running mongod process. 



**Returns:**
 
 - <b>`str`</b>:  The shell command. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `start`

```python
start(
    ports: Union[List[int], int],
    timeout: int = 0,
    debug: bool = False
) → List[int]
```

Launch a master instance. 



**Note:**

> If you create a custom subclass of MasterLauncher which will not start the master instance on localhost then you should pass the debug flag on to `execute_task()` of the `RuntimeGroup` or `Runtime` so that you can benefit from the debug feature of `RuntimeTask.execute()`. 
>

**Args:**
 
 - <b>`ports`</b>:  Port where the DB should be started. If a list is given then the first port that is free in the  `RuntimeGroup` will be used. The actual chosen port can be requested via the property `port`. 
 - <b>`timeout`</b>:  Timeout (s) after which an MasterStartError is raised if DB instance not started yet. Defaults to  3 seconds. 
 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then  the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to  `False`. 



**Returns:**
 
 - <b>`List[int]`</b>:  In case a port list was given the updated port list will be returned. Otherwise an empty list. 



**Raises:**
 
 - <b>`PortInUseError`</b>:  If a single port is given and it is not free in the `RuntimeGroup`. 
 - <b>`NoPortsLeftError`</b>:  If a port list was given and none of the ports is actually free in the `RuntimeGroup`. 
 - <b>`MasterStartError`</b>:  If master was not started after the specified `timeout`. 


---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L153"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RoundRobinLauncher`
Concrete WorkerLauncher implementation for launching hyperopt workers in a round robin manner. 

See the `WorkerLauncher` documentation to get a list of the inherited methods and attributes. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(runtime_group: RuntimeGroup, dbname: str, poll_interval: float)
```

Initialization method. 



**Args:**
 
 - <b>`runtime_group`</b>:  The group where the workers will be started. 
 - <b>`dbname`</b>:  The name of the mongodb instance. 
 - <b>`poll_interval`</b>:  The poll interval of the hyperopt worker. 

Raises. 
 - <b>`ValueError`</b>:  In case dbname is empty. 


---

#### <kbd>property</kbd> ports_per_host

Dictionary with the host as key and a port list as value. The list contains all ports where a worker instance is reachable on the respective host. 



**Returns:**
 
 - <b>`Dict[str, List[int]]`</b>:  The ports per host as a dictionary. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L251"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `cleanup`

```python
cleanup() → None
```

Release all resources. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L183"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `start`

```python
start(
    worker_count: int,
    master_port: int,
    ports: List[int] = None,
    debug: bool = True
) → List[int]
```

Launches the worker instances in the `RuntimeGroup`. 



**Args:**
 
 - <b>`worker_count`</b>:  The number of worker instances to be started in the group. 
 - <b>`master_port`</b>:   The port of the master instance. 
 - <b>`ports`</b>:  Without use here. Only here because we need to adhere to the interface defined by the  WorkerLauncher class. 
 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then  the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to  `False`. 



**Returns:**
 
 - <b>`List[int]`</b>:  The updated port list after starting the workers, i.e. the used ones were removed. 


---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L257"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `HyperoptCluster`
Convenient class for launching a Hyperopt cluster in a `RuntimeGroup`. 

HyperoptCluster inherits from MasterWorkerCluster. See its documentation to get a list of the inherited methods and attributes. 

The number of hyperopt workers defaults to the number of `Runtimes` in the used `RuntimeGroup`. This number can be adjusted so that more or less workers than available `Runtimes` can be used. Per default the desired number of workers is started in a round robin way as implemented in `RoundRobinLauncher`. Consequently, this leads to an equal distribution of hyperopt workers in the `RuntimeGroup`. You can provide a custom implementation inheriting from the `WorkerLauncher` class in order to execute a different strategy how workers should be started. The master instance (i.e. the mongoDB) will always be started on localhost as implemented in `LocalMasterLauncher`. This behavior can also be changed by providing a custom implementation inheriting from the `MasterLauncher`. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L276"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    runtime_group: RuntimeGroup,
    mongo_launcher: Optional[MongoLauncher] = None,
    worker_launcher: Optional[WorkerLauncher] = None,
    dbpath: Optional[str] = None,
    dbname: str = 'hyperopt',
    worker_poll_intervall: float = 1
)
```

Initialization method. 



**Args:**
 
 - <b>`runtime_group`</b>:  The `RuntimeGroup` contains all `Runtimes` which can be used for starting the entities. 
 - <b>`mongo_launcher`</b>:  Optionally, an instance implementing the `MasterLauncher` interface can be given, which  implements the strategy for launching the master instances in the cluster. If None, then  `LocalMasterLauncher` is used. 
 - <b>`worker_launcher`</b>:  Optionally, an instance implementing the `WorkerLauncher` interface can be given, which  implements the strategy for launching the worker instances. If None, then  `RoundRobinLauncher` is used. 
 - <b>`dbpath`</b>:  The directory where the db files will be kept. Defaults to a `mongodb` directory inside the  `utils.Environment.main_directory`. 
 - <b>`dbname`</b>:  The name of the database to be used for experiments. See MongoTrials url scheme in hyperopt  documentation for more details. Defaults to ´hyperopt´. 
 - <b>`worker_poll_intervall`</b>:  The poll interval of the hyperopt worker. Defaults to `0.1`. 



**Raises:**
 
 - <b>`PermissionError`</b>:  If the `dbpath` does not exsist and could not be created due to lack of permissions. 


---

#### <kbd>property</kbd> dbname

The name of the MongoDB database to be used for experiments. 

---

#### <kbd>property</kbd> master_port

The port where the master instance was started. None, if not yet started. 



**Returns:**
 
 - <b>`Optional[int]`</b>:  The master port. 

---

#### <kbd>property</kbd> mongo_trial_url

The MongoDB url indicating what mongod process and which database to use. 



**Note:**

> The format is the format required by the hyperopt MongoTrials object. 
>

**Returns:**
 
 - <b>`str`</b>:  URL string. 

---

#### <kbd>property</kbd> mongo_url

The MongoDB url indicating what mongod process and which database to use. 



**Note:**

> The format is `mongo://host:port/dbname`. 
>

**Returns:**
 
 - <b>`str`</b>:  URL string. 

---

#### <kbd>property</kbd> runtime_group

The RuntimeGroup. 



**Returns:**
 
 - <b>`RuntimeGroup`</b>:  The used group. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L396"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `cleanup`

```python
cleanup() → None
```

Release all resources. 

---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/hyperopt_cluster.py#L370"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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
 
 - <b>`master_port`</b>:  Port of the master instance. Defaults to self.DEFAULT_MASTER_PORT, but another one is chosen if  the port is not free within the group. The actual chosen port can be requested via  self.master_port. 
 - <b>`timeout`</b>:  Timeout (s) after which an MasterStartError is raised if master instance not started yet. 
 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. Has no effect for  if the master instance is started locally, what default MasterLauncher implementations usually do. 



**Raises:**
 
 - <b>`PortInUseError`</b>:  If a single port is given and it is not free in the `RuntimeGroup`. 
 - <b>`NoPortsLeftError`</b>:  If there are no free ports left in the port list for instantiating the master. 
 - <b>`MasterStartError`</b>:  If master was not started after the specified `timeout`. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
