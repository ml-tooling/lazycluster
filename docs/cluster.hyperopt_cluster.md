
<a href="/lazycluster/cluster/hyperopt_cluster.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `lazycluster.cluster.hyperopt_cluster`
Module for conveniently managing a Hyperopt cluster. https://github.com/hyperopt/hyperopt



-------------------
<a href="/lazycluster/cluster/hyperopt_cluster.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LocalMongoLauncher`
Concrete implementation of the `MasterLauncher` interface. See its documentation to get a list of the inherited
methods and attributes.

This class implements the logic for starting a MongoDB instance on localhost. Hence, we simply treat the MongoDB
instance as master node.


#### <kbd>property</kbd> LocalMongoLauncher.port
 The port where the master instance is started on. Will be None if not yet started.


**Returns:**


 - <b>`int`</b>:  The master port.


#### <kbd>property</kbd> LocalMongoLauncher.process
 The process object where the master instance was started in.


**Returns:**


 - <b>`Popen`</b>:  The process object.


-------------------
<a href="/lazycluster/cluster/hyperopt_cluster.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `LocalMongoLauncher.__init__`

```python
__init__(runtime_group: lazycluster.runtime_mgmt.RuntimeGroup)
```
Initialization method.


**Args:**


 - <b>`runtime_group`</b>:  The group where the workers will be started.



-------------------
<a href="/lazycluster/cluster/hyperopt_cluster.py#L119"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `LocalMongoLauncher.cleanup`

```python
cleanup()
```
Release all resources.
 

-------------------
<a href="/lazycluster/cluster/hyperopt_cluster.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `LocalMongoLauncher.get_mongod_start_cmd`

```python
get_mongod_start_cmd() → str
```
Get the shell command for starting mongod as a deamon process.


**Returns:**


 - <b>`str`</b>:  The shell command.

-------------------
<a href="/lazycluster/cluster/hyperopt_cluster.py#L111"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `LocalMongoLauncher.get_mongod_stop_cmd`

```python
get_mongod_stop_cmd() → str
```
Get the shell command for stopping the currently running mongod process.


**Returns:**


 - <b>`str`</b>:  The shell command.

-------------------
<a href="/lazycluster/cluster/hyperopt_cluster.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `LocalMongoLauncher.start`

```python
start(
    ports: Union[List[int], int],
    timeout: int = 0,
    debug: bool = False
) → List[int]
```
Launch a master instance.


**Note:**

 If you create a custom subclass of MasterLauncher which will not start the master instance on localhost
 then you should pass the debug flag on to `execute_task()` of the `RuntimeGroup` or `Runtime` so that you
 can benefit from the debug feature of `RuntimeTask.execute()`.


**Args:**


 - <b>`ports`</b>:  Port where the DB should be started. If a list is given then the first port that is free in the
 `RuntimeGroup` will be used. The actual chosen port can be requested via the property `port`.

 - <b>`timeout`</b>:  Timeout (s) after which an MasterStartError is raised if DB instance not started yet. Defaults to
 3 seconds.

 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then
 the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to
 `False`.


**Returns:**


 - <b>`List[int]`</b>:  In case a port list was given the updated port list will be returned. Otherwise an empty list.


**Raises:**


 - <b>`PortInUseError`</b>:  If a single port is given and it is not free in the `RuntimeGroup`.

 - <b>`NoPortsLeftError`</b>:  If a port list was given and none of the ports is actually free in the `RuntimeGroup`.

 - <b>`MasterStartError`</b>:  If master was not started after the specified `timeout`.


-------------------
<a href="/lazycluster/cluster/hyperopt_cluster.py#L132"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RoundRobinLauncher`
Concrete WorkerLauncher implementation for launching hyperopt workers in a round robin manner. See its
documentation to get a list of the inherited methods and attributes.


#### <kbd>property</kbd> RoundRobinLauncher.ports_per_host
 Dictionary with the host as key and a port list as value. The list contains all ports where a worker instance
is reachable on the respective host.


**Returns:**


 - <b>`Dict[str, List[int]]`</b>:  The ports per host as a dictionary.


-------------------
<a href="/lazycluster/cluster/hyperopt_cluster.py#L137"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RoundRobinLauncher.__init__`

```python
__init__(
    runtime_group: lazycluster.runtime_mgmt.RuntimeGroup,
    dbname: str,
    poll_interval: float
)
```
Initialization method.


**Args:**


 - <b>`runtime_group`</b>:  The group where the workers will be started.

 - <b>`dbname`</b>:  The name of the mongodb instance.

 - <b>`poll_interval`</b>:  The poll interval of the hyperopt worker.

Raises.

 - <b>`ValueError`</b>:  In case dbname is empty.



-------------------
<a href="/lazycluster/cluster/hyperopt_cluster.py#L213"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RoundRobinLauncher.cleanup`

```python
cleanup()
```
Release all resources.
 

-------------------
<a href="/lazycluster/cluster/runtime_cluster.py#L154"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RoundRobinLauncher.setup_worker_ssh_tunnels`

```python
setup_worker_ssh_tunnels()
```
Set up ssh tunnel for workers such that all communication is routed over the
local machine and all entities can talk to each other on localhost.


**Note:**

 This method needs to be called if the communication between the worker instances is necessary, e.g. in case
 of DASK or Apache Flink, where data needs to be shuffled between the different entities.


**Raises:**


 - <b>`ValueError`</b>:  If host is not contained.

 - <b>`PortInUseError`</b>:  If `group_port` is occupied on the local machine.

 - <b>`NoPortsLeftError`</b>:  If `group_ports` was given and none of the ports was free.

-------------------
<a href="/lazycluster/cluster/hyperopt_cluster.py#L161"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RoundRobinLauncher.start`

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

 - <b>`ports`</b>:  Without use here. Only here because we need to adhere to the interface defined by the
 WorkerLauncher class.

 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then
 the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to
 `False`.


**Returns:**


 - <b>`List[int]`</b>:  The updated port list after starting the workers, i.e. the used ones were removed.


-------------------
<a href="/lazycluster/cluster/hyperopt_cluster.py#L220"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `HyperoptCluster`
Convenient class for launching a Hyperopt cluster in a `RuntimeGroup`.

HyperoptCluster inherits from MasterWorkerCluster. See its documentation to get a list of the inherited methods
and attributes.

The number of hyperopt workers defaults to the number of `Runtimes` in the used `RuntimeGroup`. This number can be
adjusted so that more or less workers than available `Runtimes` can be used. Per default the desired number of
workers is started in a round robin way as implemented in `RoundRobinLauncher`. Consequently, this leads to an
equal distribution of hyperopt workers in the `RuntimeGroup`. You can provide a custom implementation inheriting
from the `WorkerLauncher` class in order to execute a different strategy how workers should be started. The
master instance (i.e. the mongoDB) will always be started on localhost as implemented in `LocalMasterLauncher`. This
behavior can also be changed by providing a custom implementation inheriting from the `MasterLauncher`.


#### <kbd>property</kbd> HyperoptCluster.dbname
 The name of the MongoDB database to be used for experiments.
 


#### <kbd>property</kbd> HyperoptCluster.master_port
 The port where the master instance was started. None, if not yet started.


**Returns:**


 - <b>`int`</b>:  The master port.


#### <kbd>property</kbd> HyperoptCluster.mongo_trial_url
 The MongoDB url indicating what mongod process and which database to use.


**Note:**

 The format is the format required by the hyperopt MongoTrials object.


**Returns:**


 - <b>`str`</b>:  URL string.


#### <kbd>property</kbd> HyperoptCluster.mongo_url
 The MongoDB url indicating what mongod process and which database to use.


**Note:**

 The format is `mongo://host:port/dbname`.


**Returns:**


 - <b>`str`</b>:  URL string.


#### <kbd>property</kbd> HyperoptCluster.runtime_group
 The RuntimeGroup.


**Returns:**


 - <b>`RuntimeGroup`</b>:  The used group.


-------------------
<a href="/lazycluster/cluster/hyperopt_cluster.py#L239"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `HyperoptCluster.__init__`

```python
__init__(
    runtime_group: lazycluster.runtime_mgmt.RuntimeGroup,
    master_launcher: Optional[lazycluster.cluster.runtime_cluster.MasterLauncher] = None,
    worker_launcher: Optional[lazycluster.cluster.runtime_cluster.WorkerLauncher] = None,
    dbpath: Optional[str] = None,
    dbname: str = 'hyperopt',
    worker_poll_intervall: float = 0.1
)
```
Initialization method.


**Args:**


 - <b>`runtime_group`</b>:  The `RuntimeGroup` contains all `Runtimes` which can be used for starting the entities.

 - <b>`master_launcher`</b>:  Optionally, an instance implementing the `MasterLauncher` interface can be given, which
 implements the strategy for launching the master instances in the cluster. If None, then
 `LocalMasterLauncher` is used.

 - <b>`worker_launcher`</b>:  Optionally, an instance implementing the `WorkerLauncher` interface can be given, which
 implements the strategy for launching the worker instances. If None, then
 `RoundRobinLauncher` is used.

 - <b>`dbpath`</b>:  The directory where the db files will be kept. Defaults to a `mongodb` directory inside the
 `utils.Environment.main_directory`.

 - <b>`dbname`</b>:  The name of the database to be used for experiments. See MongoTrials url scheme in hyperopt
 documentation for more details. Defaults to ´hyperopt´.

 - <b>`worker_poll_intervall`</b>:  The poll interval of the hyperopt worker. Defaults to `0.1`.


**Raises:**


 - <b>`PermissionError`</b>:  If the `dbpath` does not exsist and could not be created due to lack of permissions.



-------------------
<a href="/lazycluster/cluster/hyperopt_cluster.py#L343"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `HyperoptCluster.cleanup`

```python
cleanup()
```
Release all resources.
 

-------------------
<a href="/lazycluster/cluster/runtime_cluster.py#L368"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `HyperoptCluster.print_log`

```python
print_log()
```
Print the execution log.


**Note:**

 This method is a convenient wrapper for the equivalent method of the contained `RuntimeGroup`.

-------------------
<a href="/lazycluster/cluster/runtime_cluster.py#L272"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `HyperoptCluster.start`

```python
start(
    worker_count: Optional[int] = None,
    master_port: Optional[int] = None,
    debug: bool = False
)
```
Convenient method for launching the cluster.

Internally, `self.start_master()` and `self.start_workers()` will be called.


**Args:**


 - <b>`master_port`</b>:  Port of the cluster master. Will be passed on to `self.start()`, hence see respective method
 for further details.

 - <b>`worker_count`</b>:  The number of worker instances to be started in the cluster. Will be passed on to
 `self.start()`, hence see respective method for further details.

 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then
 the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to
 `False`.

-------------------
<a href="/lazycluster/cluster/hyperopt_cluster.py#L319"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `HyperoptCluster.start_master`

```python
start_master(
    master_port: Optional[int] = None,
    timeout: int = 3,
    debug: bool = False
)
```
Start the master instance.


**Note:**

 How the master is actually started is determined by the the actual `MasterLauncher` implementation. Another
 implementation adhering to the `MasterLauncher` interface can be provided in the constructor of the cluster
 class.


**Args:**


 - <b>`master_port`</b>:  Port of the master instance. Defaults to self.DEFAULT_MASTER_PORT, but another one is chosen if
 the port is not free within the group. The actual chosen port can be requested via
 self.master_port.

 - <b>`timeout`</b>:  Timeout (s) after which an MasterStartError is raised if master instance not started yet.

 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. Has no effect for
 if the master instance is started locally, what default MasterLauncher implementations usually do.


**Raises:**


 - <b>`PortInUseError`</b>:  If a single port is given and it is not free in the `RuntimeGroup`.

 - <b>`NoPortsLeftError`</b>:  If there are no free ports left in the port list for instantiating the master.

 - <b>`MasterStartError`</b>:  If master was not started after the specified `timeout`.

-------------------
<a href="/lazycluster/cluster/runtime_cluster.py#L339"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `HyperoptCluster.start_workers`

```python
start_workers(count: Optional[int] = None, debug: bool = False)
```
Start the worker instances.


**Note:**

 How workers are actually started is determined by the the actual `WorkerLauncher` implementation. Another
 implementation adhering to the `WorkerLauncher` interface can be provided in the constructor of the cluster
 class.


**Args:**


 - <b>`count`</b>:  The number of worker instances to be started in the cluster. Defaults to the number of runtimes in
 the cluster.

 - <b>`debug`</b>:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then
 the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to
 `False`.

**Raises:**


  - <b>`NoPortsLeftError`</b>:  If there are no free ports left in the port list for instantiating new worker entities.



