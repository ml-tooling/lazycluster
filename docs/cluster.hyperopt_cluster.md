
**Source:** [/lazycluster/cluster/hyperopt_cluster.py#L0](/lazycluster/cluster/hyperopt_cluster.py#L0)


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/hyperopt_cluster.py#L15)</span>

## LocalMongoLauncher class

Concrete implementation of the `MasterLauncher` interface. See its documentation to get a list of the inherited
methods and attributes.

This class implements the logic for starting a MongoDB instance on localhost. Hence, we simply treat the MongoDB
instance as master node.

#### LocalMongoLauncher.port
 
The port where the master instance is started on. Will be None if not yet started.

**Returns:**

 - `int`:  The master port.

#### LocalMongoLauncher.process
 
The process object where the master instance was started in.

**Returns:**

 - `Popen`:  The process object.

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/hyperopt_cluster.py#L23)</span>

### LocalMongoLauncher.`__init__`

```python
__init__(self, runtime_group:  lazycluster.runtime_mgmt.RuntimeGroup)
```

Initialization method.

**Args:**

 - `runtime_group`:  The group where the workers will be started.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/hyperopt_cluster.py#L104)</span>

### LocalMongoLauncher.cleanup

```python
cleanup(self)
```

Release all resources.
  
-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/hyperopt_cluster.py#L87)</span>

### LocalMongoLauncher.get_mongod_start_cmd

```python
get_mongod_start_cmd(self) → str
```

Get the shell command for starting mongod as a deamon process.

**Returns:**

 - `str`:  The shell command.
-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/hyperopt_cluster.py#L96)</span>

### LocalMongoLauncher.get_mongod_stop_cmd

```python
get_mongod_stop_cmd(self) → str
```

Get the shell command for stopping the currently running mongod process.

**Returns:**

 - `str`:  The shell command.
-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/hyperopt_cluster.py#L32)</span>

### LocalMongoLauncher.start

```python
start(
    self,
    ports:  Union[List[int],
    int],
    timeout:  int  =  3
) → List[int]
```

Launch a master instance.

**Args:**

 - `ports`:  Port where the DB should be started. If a list is given then the first port that is free in the
  `RuntimeGroup` will be used. The actual chosen port can be requested via the property `port`.
 - `timeout`:  Timeout (s) after which an MasterStartError is raised if DB instance not started yet. Defaults to
  3 seconds.

**Returns:**

List[int]: In case a port list was given the updated port list will be returned. Otherwise an empty list.

**Raises:**

 - `PortInUseError`:  If a single port is given and it is not free in the `RuntimeGroup`.
 - `NoPortsLeftError`:  If a port list was given and none of the ports is actually free in the `RuntimeGroup`.
 - `MasterStartError`:  If master was not started after the specified `timeout`.

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/hyperopt_cluster.py#L117)</span>

## RoundRobinLauncher class

Concrete WorkerLauncher implementation for launching hyperopt workers in a round robin manner. See its
documentation to get a list of the inherited methods and attributes.

#### RoundRobinLauncher.ports_per_host
 
Dictionary with the host as key and a port list as value. The list contains all ports where a worker instance
is reachable on the respective host.

**Returns:**

  Dict[str, List[int]]: The ports per host as a dictionary.

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/hyperopt_cluster.py#L122)</span>

### RoundRobinLauncher.`__init__`

```python
__init__(
    self,
    runtime_group:  lazycluster.runtime_mgmt.RuntimeGroup,
    dbname:  str,
    poll_interval:  float
)
```

Initialization method.

**Args:**

 - `runtime_group`:  The group where the workers will be started.
 - `dbname`:  The name of the mongodb instance.
 - `poll_interval`:  The poll interval of the hyperopt worker.

Raises.
 - `ValueError`:  In case dbname is empty.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/hyperopt_cluster.py#L194)</span>

### RoundRobinLauncher.cleanup

```python
cleanup(self)
```

Release all resources.
  
-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L141)</span>

### RoundRobinLauncher.setup_worker_ssh_tunnels

```python
setup_worker_ssh_tunnels(self)
```

Set up ssh tunnel for workers such that all communication is routed over the
local machine and all entities can talk to each other on localhost.

**Note:**

  This method needs to be called if the communication between the worker instances is necessary, e.g. in case
  of DASK or Apache Flink, where data needs to be shuffled between the different entities.

**Raises:**

 - `ValueError`:  If host is not contained.
 - `PortInUseError`:  If `group_port` is occupied on the local machine.
 - `NoPortsLeftError`:  If `group_ports` was given and none of the ports was free.
-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/hyperopt_cluster.py#L146)</span>

### RoundRobinLauncher.start

```python
start(
    self,
    worker_count:  int,
    master_port:  int,
    ports:  List[int]  =  None
) → List[int]
```

Launches the worker instances in the `RuntimeGroup`.

**Args:**

 - `worker_count`:  The number of worker instances to be started in the group.
 - `master_port`:   The port of the master instance.
 - `ports`:  Without use here. Only here because we need to adhere to the interface defined by the
  WorkerLauncher class.
**Returns:**

List[int]: The updated port list after starting the workers, i.e. the used ones were removed.

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/hyperopt_cluster.py#L201)</span>

## HyperoptCluster class

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

#### HyperoptCluster.dbname
 
The name of the MongoDB database to be used for experiments.
  

#### HyperoptCluster.master_port
 
The port where the master instance was started. None, if not yet started.

**Returns:**

 - `int`:  The master port.

#### HyperoptCluster.mongo_trial_url
 
The MongoDB url indicating what mongod process and which database to use.

**Note:**

  The format is the format required by the hyperopt MongoTrials object.

**Returns:**

 - `str`:  URL string.

#### HyperoptCluster.mongo_url
 
The MongoDB url indicating what mongod process and which database to use.

**Note:**

  The format is `mongo://host:port/dbname`.

**Returns:**

 - `str`:  URL string.

#### HyperoptCluster.runtime_group
 
The RuntimeGroup.

**Returns:**

 - `RuntimeGroup`:  The used group.

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/hyperopt_cluster.py#L220)</span>

### HyperoptCluster.`__init__`

```python
__init__(
    self,
    runtime_group:  lazycluster.runtime_mgmt.RuntimeGroup,
    master_launcher:  Union[lazycluster.cluster.runtime_cluster.MasterLauncher,
    NoneType]  =  None,
    worker_launcher:  Union[lazycluster.cluster.runtime_cluster.WorkerLauncher,
    NoneType]  =  None,
    dbpath:  str  =  '/data/db',
    dbname:  str  =  'hyperopt',
    worker_poll_intervall:  float  =  0.1
)
```

Initialization method.

**Args:**

 - `runtime_group`:  The `RuntimeGroup` contains all `Runtimes` which can be used for starting the entities.
 - `master_launcher`:  Optionally, an instance implementing the `MasterLauncher` interface can be given, which
  implements the strategy for launching the master instances in the cluster. If None, then
  `LocalMasterLauncher` is used.
 - `worker_launcher`:  Optionally, an instance implementing the `WorkerLauncher` interface can be given, which
  implements the strategy for launching the worker instances. If None, then
  `RoundRobinLauncher` is used.
 - `dbpath`:  The directory where the db files will be kept. Defaults to `/data/db`.
 - `dbname`:  The name of the database to be used for experiments. See MongoTrials url scheme in hyperopt
  documentation for more details. Defaults to ´hyperopt´.
 - `worker_poll_intervall`:  The poll interval of the hyperopt worker. Defaults to `0.1`.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/hyperopt_cluster.py#L310)</span>

### HyperoptCluster.cleanup

```python
cleanup(self)
```

Release all resources.
  
-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L256)</span>

### HyperoptCluster.start

```python
start(
    self,
    worker_count:  Union[int,
    NoneType]  =  None,
    master_port:  Union[int,
    NoneType]  =  None
)
```

Convenient method for launching the cluster.

Internally, `self.start_master()` and `self.start_workers()` will be called.

**Args:**

 - `master_port`:  Port of the cluster master. Will be passed on to `self.start()`, hence see respective method
  for further details.
 - `worker_count`:  The number of worker instances to be started in the cluster. Will be passed on to
  `self.start()`, hence see respective method for further details.
-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/hyperopt_cluster.py#L288)</span>

### HyperoptCluster.start_master

```python
start_master(
    self,
    master_port:  Union[int,
    NoneType]  =  None,
    timeout:  int  =  3
)
```

Start the master instance.

**Note:**

  How the master is actually started is determined by the the actual `MasterLauncher` implementation. Another
  implementation adhering to the `MasterLauncher` interface can be provided in the constructor of the cluster
  class.

**Args:**

 - `master_port`:  Port of the master instance. Defaults to self.DEFAULT_MASTER_PORT, but another one is chosen if
  the port is not free within the group. The actual chosen port can be requested via
  self.master_port.
 - `timeout`:  Timeout (s) after which an MasterStartError is raised if master instance not started yet.

**Raises:**

 - `PortInUseError`:  If a single port is given and it is not free in the `RuntimeGroup`.
 - `NoPortsLeftError`:  If there are no free ports left in the port list for instantiating the master.
 - `MasterStartError`:  If master was not started after the specified `timeout`.
-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L318)</span>

### HyperoptCluster.start_workers

```python
start_workers(self, count:  Union[int, NoneType]  =  None)
```

Start the worker instances.

**Note:**

  How workers are actually started is determined by the the actual `WorkerLauncher` implementation. Another
  implementation adhering to the `WorkerLauncher` interface can be provided in the constructor of the cluster
  class.

**Args:**

 - `count`:  The number of worker instances to be started in the cluster. Defaults to the number of runtimes in
  the cluster.
**Raises:**

  - `NoPortsLeftError`:  If there are no free ports left in the port list for instantiating new worker entities.


