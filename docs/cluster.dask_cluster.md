
**Source:** [/lazycluster/cluster/dask_cluster.py#L0](/lazycluster/cluster/dask_cluster.py#L0)


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L17)</span>

## LocalMasterLauncher class

Concrete implementation of the `MasterLauncher` interface. See its documentation to get a list of the

inherited methods and attributes.



This class implements the logic for starting a the DASK master instance (i.e. scheduler in DASK terms) on localhost.


#### LocalMasterLauncher.port
 
The port where the master instance is started on. Will be None if not yet started.



**Returns:**


 - `int`:  The master port.


#### LocalMasterLauncher.process
 
The process object where the master instance was started in.



**Returns:**


 - `Popen`:  The process object.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L18)</span>

### LocalMasterLauncher.`__init__`

```python
__init__(self, runtime_group:  lazycluster.runtime_mgmt.RuntimeGroup)
```

Initialization method.



**Args:**


 - `runtime_group`:  The group where the workers will be started.



-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L78)</span>

### LocalMasterLauncher.cleanup

```python
cleanup(self)
```

Release all resources.

  

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L24)</span>

### LocalMasterLauncher.start

```python
start(
    self,
    ports:  Union[List[int],
    int],
    timeout:  int  =  3,
    debug:  bool  =  False
) → List[int]
```

Launch a master instance.



**Note:**


  If you create a custom subclass of MasterLauncher which will not start the master instance on localhost

  then you should pass the debug flag on to `execute_task()` of the `RuntimeGroup` or `Runtime` so that you

  can benefit from the debug feature of `RuntimeTask.execute()`.



**Args:**


 - `ports`:  Port where the master should be started. If a list is given then the first port that is free in the

  `RuntimeGroup` will be used. The actual chosen port can be requested via the property `port`.

 - `timeout`:  Timeout (s) after which an MasterStartError is raised if master instance not started yet.

 - `debug`:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then

  the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to

  `False`.



**Returns:**


List[int]: In case a port list was given the updated port list will be returned. Otherwise an empty list.



**Raises:**


 - `PortInUseError`:  If a single port is given and it is not free in the `RuntimeGroup`.

 - `NoPortsLeftError`:  If a port list was given and none of the ports is actually free in the `RuntimeGroup`.

 - `MasterStartError`:  If master was not started after the specified `timeout`.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L85)</span>

## RoundRobinLauncher class

WorkerLauncher implementation for launching DASK workers in a round robin manner. See its documentation to get

a list of the inherited methods and attributes.


#### RoundRobinLauncher.ports_per_host
 
Dictionary with the host as key and a port list as value. The list contains all ports where a worker instance

is reachable on the respective host.



**Returns:**


  Dict[str, List[int]]: The ports per host as a dictionary.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L90)</span>

### RoundRobinLauncher.`__init__`

```python
__init__(self, runtime_group:  lazycluster.runtime_mgmt.RuntimeGroup)
```

Initialization method.



**Args:**


 - `runtime_group`:  The group where the workers will be started.



-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L172)</span>

### RoundRobinLauncher.cleanup

```python
cleanup(self)
```

Release all resources.

  

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L154)</span>

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
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L101)</span>

### RoundRobinLauncher.start

```python
start(
    self,
    worker_count:  int,
    master_port:  int,
    ports:  List[int],
    debug:  bool  =  False
) → List[int]
```

Launches the worker instances in the `RuntimeGroup`.



**Args:**


 - `worker_count`:  The number of worker instances to be started in the group.

 - `master_port`:   The port of the master instance.

 - `ports`:  The ports to be used for starting the workers. Only ports from the list will be chosen

  that are actually free.

 - `debug`:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then

  the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to

  `False`.



**Returns:**


List[int]: The updated port list after starting the workers, i.e. the used ones were removed.



**Raises:**


 - `NoPortsLeftError`:  If there are not enough free ports for starting all workers.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L179)</span>

## DaskCluster class

Convenient class for launching a Dask cluster in a `RuntimeGroup`.



DaskCluster inherits from MasterWorkerCluster. See its documentation to get a list of the inherited methods

and attributes.



The number of DASK workers defaults to the number of `Runtimes` in the used `RuntimeGroup`. This number can be

adjusted so that more or less workers than available `Runtimes` can be used. Per default the desired number of

workers is started in a round robin way as implemented in `RoundRobinLauncher`. Consequently, this leads to an

equal distribution of DASK workers in the `RuntimeGroup`. You can provide a custom implementation inheriting from

the `WorkerLauncher` class in order to execute a different strategy how workers should be started. The

DASK master (i.e. scheduler) will always be started on localhost as implemented in `LocalMasterLauncher`. This

behavior can also be changed by providing a custom implementation inheriting from the `MasterLauncher`.


#### DaskCluster.master_port
 
The port where the master instance was started. None, if not yet started.



**Returns:**


 - `int`:  The master port.


#### DaskCluster.runtime_group
 
The RuntimeGroup.



**Returns:**


 - `RuntimeGroup`:  The used group.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L197)</span>

### DaskCluster.`__init__`

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


 - `runtime_group`:  The `RuntimeGroup` contains all `Runtimes` which can be used for starting the DASK entities.

 - `ports`:  The list of ports which will be used to instantiate a cluster. Defaults to

  list(range(self.DEFAULT_PORT_RANGE_START,

  self.DEFAULT_PORT_RANGE_END)).

 - `master_launcher`:  Optionally, an instance implementing the `MasterLauncher` interface can be given, which

  implements the strategy for launching the master instances in the cluster. If None, then

  `LocalMasterLauncher` is used.

 - `worker_launcher`:  Optionally, an instance implementing the `WorkerLauncher` interface can be given, which

  implements the strategy for launching the worker instances. If None, then

  `RoundRobinLauncher` is used.



-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L232)</span>

### DaskCluster.cleanup

```python
cleanup(self)
```

Release all resources.

  

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L221)</span>

### DaskCluster.get_client

```python
get_client(self, timeout:  int  =  2) → distributed.client.Client
```

Get a connected Dask client. 



**Args:**


 - `timeout`:  The timeout (s) value passed on to the Dask `Client` constructor. Defaults to 2.



**Raises:**


 - `TimeoutError`:  If client connection `timeout` expires.

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L365)</span>

### DaskCluster.print_log

```python
print_log(self)
```

Print the execution log.



**Note:**


  This method is a convenient wrapper for the equivalent method of the contained `RuntimeGroup`.

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L269)</span>

### DaskCluster.start

```python
start(
    self,
    worker_count:  Union[int,
    NoneType]  =  None,
    master_port:  Union[int,
    NoneType]  =  None,
    debug:  bool  =  False
)
```

Convenient method for launching the cluster.



Internally, `self.start_master()` and `self.start_workers()` will be called.



**Args:**


 - `master_port`:  Port of the cluster master. Will be passed on to `self.start()`, hence see respective method

  for further details.

 - `worker_count`:  The number of worker instances to be started in the cluster. Will be passed on to

  `self.start()`, hence see respective method for further details.

 - `debug`:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then

  the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to

  `False`.

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L288)</span>

### DaskCluster.start_master

```python
start_master(
    self,
    master_port:  Union[int,
    NoneType]  =  None,
    timeout:  int  =  3,
    debug:  bool  =  False
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

 - `debug`:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. Has no effect for

  if the master instance is started locally, what default MasterLauncher implementations usually do.



**Raises:**


 - `PortInUseError`:  If a single port is given and it is not free in the `RuntimeGroup`.

 - `NoPortsLeftError`:  If there are no free ports left in the port list for instantiating the master.

 - `MasterStartError`:  If master was not started after the specified `timeout`.

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L336)</span>

### DaskCluster.start_workers

```python
start_workers(
    self,
    count:  Union[int,
    NoneType]  =  None,
    debug:  bool  =  False
)
```

Start the worker instances.



**Note:**


  How workers are actually started is determined by the the actual `WorkerLauncher` implementation. Another

  implementation adhering to the `WorkerLauncher` interface can be provided in the constructor of the cluster

  class.



**Args:**


 - `count`:  The number of worker instances to be started in the cluster. Defaults to the number of runtimes in

  the cluster.

 - `debug`:  If `True`, stdout/stderr from the runtime will be printed to stdout of localhost. If, `False` then

  the stdout/stderr will be added to python logger with level debug after each `RuntimeTask` step. Defaults to

  `False`.

**Raises:**


  - `NoPortsLeftError`:  If there are no free ports left in the port list for instantiating new worker entities.



