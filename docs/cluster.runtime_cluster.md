
**Source:** [/lazycluster/cluster/runtime_cluster.py#L0](/lazycluster/cluster/runtime_cluster.py#L0)


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L14)</span>

## MasterLauncher class

Abstract class for implementing the strategy for launching the master instance of the cluster. 


#### MasterLauncher.port
 
The port where the master instance is started on. Will be None if not yet started.



**Returns:**


 - `int`:  The master port.


#### MasterLauncher.process
 
The process object where the master instance was started in.



**Returns:**


 - `Popen`:  The process object.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L17)</span>

### MasterLauncher.`__init__`

```python
__init__(self, runtime_group:  lazycluster.runtime_mgmt.RuntimeGroup)
```

Initialization method.



**Args:**


 - `runtime_group`:  The group where the workers will be started.



-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L73)</span>

### MasterLauncher.cleanup

```python
cleanup(self)
```

Release all resources.

  

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L50)</span>

### MasterLauncher.start

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


 - `ports`:  Port where the master should be started. If a list is given then the first port that is free in the

  `RuntimeGroup` will be used. The actual chosen port can requested via the property `port`.

 - `timeout`:  Timeout (s) after which an MasterStartError is raised if master instance not started yet.



**Returns:**


List[int]: In case a port list was given the updated port list will be returned. Otherwise an empty list.



**Raises:**


 - `PortInUseError`:  If a single port is given and it is not free in the `RuntimeGroup`.

 - `NoPortsLeftError`:  If a port list was given and none of the ports is actually free in the `RuntimeGroup`.

 - `MasterStartError`:  If master was not started after the specified `timeout`.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L81)</span>

## WorkerLauncher class

Abstract class for implementing the strategy for launching worker instances within a RuntimeGroup.



In order to implement a new concrete `WorkerLauncher` subclass you need to implement the start method. Please

consider the comments of the start method because some internal variables need to be set in the concrete

implementation.



Moreover, the `setup_worker_ssh_tunnels()` method can be used to setup ssh tunnels so that all entities can talk to

each other.


#### WorkerLauncher.ports_per_host
 
Dictionary with the host as key and a port list as value. The list contains all ports where a worker instance

is reachable on the respective host.



**Returns:**


  Dict[str, List[int]]: The ports per host as a dictionary.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L92)</span>

### WorkerLauncher.`__init__`

```python
__init__(self, runtime_group:  lazycluster.runtime_mgmt.RuntimeGroup)
```

Initialization method.



**Args:**


 - `runtime_group`:  The group where the workers will be started in.



-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L159)</span>

### WorkerLauncher.cleanup

```python
cleanup(self)
```

Release all resources.

  

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L141)</span>

### WorkerLauncher.setup_worker_ssh_tunnels

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
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L119)</span>

### WorkerLauncher.start

```python
start(
    self,
    worker_count:  int,
    master_port:  int,
    ports:  List[int]
) → List[int]
```

Launches the worker instances in the `RuntimeGroup`.



**Args:**


 - `worker_count`:  The number of worker instances to be started in the group.

 - `master_port`:   The port of the master instance.

 - `ports`:  The ports to be used for starting the workers. Only ports from the list will be chosen that are

  actually free.

**Returns:**


List[int]: The updated port list after starting the workers, i.e. the used ones were removed.



**Raises:**


 - `NoPortsLeftError`:  If there are not enough free ports for starting all workers.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L166)</span>

## RuntimeCluster class

Abstract cluster class.



All further cluster implementations should inherit from this class either directly (e.g. the abstract class

`MasterWorkerCluster`) or indirectly (e.g. the DaskCluster which is an concrete implementation of the

`MasterWorkerCluster`).





-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L178)</span>

## MasterWorkerCluster class

Class for clusters following a master-worker architecture.



Usually you want to inherit from this class and do not want to use it directly. It is recommended to treat this

class as an abstract class or an interface.



**Examples:**


  Create a cluster with all `Runtimes` detected by the `RuntimeManager`.

  ´´´python

  from lazycluster import RuntimeManager

  cluster = MyMasterWorkerClusterImpl(RuntimeManager().create_group())

  cluster.start()

  ´´´

  Use different strategies for launching the master and the worker instance as the default ones by providing

  custom implementation of `MasterLauncher` and `WorkerLauncher`.

  ´´´python

  cluster = MyMasterWorkerClusterImpl(RuntimeManager().create_group(),

  MyMasterLauncherImpl(),

  MyWorkerLauncherImpl)

  cluster.start()

  ```


#### MasterWorkerCluster.master_port
 
The port where the master instance was started. None, if not yet started.



**Returns:**


 - `int`:  The master port.


#### MasterWorkerCluster.runtime_group
 
The RuntimeGroup.



**Returns:**


 - `RuntimeGroup`:  The used group.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L205)</span>

### MasterWorkerCluster.`__init__`

```python
__init__(
    self,
    runtime_group:  lazycluster.runtime_mgmt.RuntimeGroup,
    ports:  Union[List[int],
    NoneType]  =  None,
    master_launcher:  Union[lazycluster.cluster.runtime_cluster.MasterLauncher,
    NoneType]  =  None,
    worker_launcher:  Union[lazycluster.cluster.runtime_cluster.WorkerLauncher,
    NoneType]  =  None
)
```

Initialization method.



**Args:**


 - `runtime_group`:  The `RuntimeGroup` contains all `Runtimes` which can be used for starting the cluster

  entities.

 - `ports`:  The list of ports which will be used to instantiate a cluster. Defaults to

  list(range(self.DEFAULT_PORT_RANGE_START, self.DEFAULT_PORT_RANGE_END).)

 - `master_launcher`:  Optionally, an instance implementing the `MasterLauncher` interface can be given, which

  implements the strategy for launching the master instances in the cluster. If None, then

  the default of the concrete cluster implementation will be chosen.

 - `worker_launcher`:  Optionally, an instance implementing the `WorkerLauncher` interface can be given, which

  implements the strategy for launching the worker instances. If None, then the default of

  the concrete cluster implementation will be chosen.



-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L353)</span>

### MasterWorkerCluster.cleanup

```python
cleanup(self)
```

Release all resources.

  

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L344)</span>

### MasterWorkerCluster.print_log

```python
print_log(self)
```

Print the execution log.



**Note:**


  This method is a convenient wrapper for the equivalent method of the contained `RuntimeGroup`.

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L256)</span>

### MasterWorkerCluster.start

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
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L272)</span>

### MasterWorkerCluster.start_master

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

### MasterWorkerCluster.start_workers

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



