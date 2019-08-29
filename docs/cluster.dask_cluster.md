
**Source:** [/lazycluster/cluster/dask_cluster.py#L0](/lazycluster/cluster/dask_cluster.py#L0)


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L16)</span>

## LocalMasterLauncher class

Concrete implementation of the `MasterLauncher` interface.

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
<span style="float:right;">[[source]](/lazycluster/cluster/runtime_cluster.py#L16)</span>

### LocalMasterLauncher.`__init__`

```python
__init__(self, runtime_group: lazycluster.runtime_mgmt.RuntimeGroup)
```

Constructor method.

**Args:**

 - `runtime_group` (RuntimeGroup):  The group where the workers will be started.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L22)</span>

### LocalMasterLauncher.start

```python
start(
    self,
    ports: Union[List[int],
    int],
    timeout: int = 3
) → List[int]
```

Launch a master instance.

**Args:**

 - `ports` (Union[List[int], int]):  Port where the master should be started. If a list is given then the
  first port that is free in the `RuntimeGroup` will be used. The actual
  chosen port can requested via the property `port`.
 - `timeout` (int):  Timeout (s) after which an MasterStartError is raised if master instance not started yet.

**Returns:**

List[int]: In case a port list was given the updated port list will be returned. Otherwise an empty list.

**Raises:**

 - `PortInUseError`:  If a single port is given and it is not free in the `RuntimeGroup`.
 - `NoPortsLeftError`:  If a port list was given and none of the ports is actually free in the `RuntimeGroup`.
 - `MasterStartError`:  If master was not started after the specified `timeout`.

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L68)</span>

## RoundRobinLauncher class

WorkerLauncher implementation for launching DASK workers in a round robin manner. 

#### RoundRobinLauncher.ports_per_host
 
Dictionary with the host as key and a port list as value. The list contains all ports where a worker instance
is reachable on the respective host.

**Returns:**

  Dict[str, List[int]]: The ports per host as a dictionary.

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L71)</span>

### RoundRobinLauncher.`__init__`

```python
__init__(self, runtime_group: lazycluster.runtime_mgmt.RuntimeGroup)
```

Initialization method.

**Args:**

 - `runtime_group` (RuntimeGroup):  The group where the workers will be started.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L80)</span>

### RoundRobinLauncher.start

```python
start(
    self,
    worker_count: int,
    master_port: int,
    ports: List[int]
) → List[int]
```

Launches the worker instances in the `RuntimeGroup`.

**Args:**

 - `worker_count` (int):  The number of worker instances to be started in the group.
 - `master_port` (int):   The port of the master instance.
 - `ports` (List[int]):  The ports to be used for starting the workers. Only ports from the list will be chosen
  that are actually free.
**Returns:**

List[int]: The updated port list after starting the workers, i.e. the used ones were removed.

**Raises:**

 - `NoPortsLeftError`:  If there are not enough free ports for starting all workers.

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L147)</span>

## DaskCluster class

Convenient class for launching a Dask cluster in a `RuntimeGroup`. 

The number of DASK workers defaults to the number of `Runtimes` in the used `RuntimeGroup`. This number can be
adjusted so that more or less workers than available `Runtimes` can be used. Per default the desired number of
workers is started in a round robin way as implemented in `RoundRobinLauncher`. Consequently, this leads to an
equal distribution of DASK workers in the `RuntimeGroup`. You can provide a custom implementation inheriting from
the `lazycluster.WorkerLauncher` class in order to execute a different strategy how workers should be started. The
DASK master (i.e. scheduler) will always be started on localhost as implemented in `LocalMasterLauncher`. This
behavior can also be changed by providing a custom implementation inheriting from the `lazycluster.MasterLauncher`.

**Examples:**

  Most simple way to launch a cluster based on a `RuntimeGroup` created by the `RuntimeManager`.
  >>> from lazycluster import RuntimeManager
  >>> cluster = DaskCluster(RuntimeManager().create_group())
  >>> cluster.start()

  Use different strategies for launching the master and the worker instance by providing custom implementation of
  `MasterLauncher` and `WorkerLauncher`.
  >>> cluster = DaskCluster(RuntimeManager().create_group(),
  ...                       MyMasterLauncherImpl(),
  ...                       MyWorkerLauncherImpl)
  >>> cluster.start()

#### DaskCluster.master_port
 
The port where the master instance was started. None, if not yet started.

**Returns:**

 - `int`:  The master port.

-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L175)</span>

### DaskCluster.`__init__`

```python
__init__(
    self,
    runtime_group: lazycluster.runtime_mgmt.RuntimeGroup,
    ports: Union[List[int],
    NoneType] = None,
    master_launcher: Union[lazycluster.cluster.runtime_cluster.MasterLauncher,
    NoneType] = None,
    worker_launcher: Union[lazycluster.cluster.runtime_cluster.WorkerLauncher,
    NoneType] = None
)
```

Initialization method.

**Args:**

 - `runtime_group` (RuntimeGroup):  The `RuntimeGroup` contains all `Runtimes` which can be used for starting the
  DASK entities.
ports (Optional[List[int]]: The list of ports which will be used to instantiate a cluster. Defaults to
  list(range(self.DEFAULT_PORT_RANGE_START,
  self.DEFAULT_PORT_RANGE_END)).
 - `master_launcher` (Optional[MasterLauncher]):  Optionally, an instance implementing the `MasterLauncher`
  interface can be given, which implements the strategy for
  launching the master instances in the cluster. If None, then
  `LocalMasterLauncher` is used.
 - `worker_launcher` (Optional[WorkerLauncher]):  Optionally, an instance implementing the `WorkerLauncher`
  interface can be given, which implements the strategy for
  launching the worker instances. If None, then
  `RoundRobinLauncher` is used.


-------------------
<span style="float:right;">[[source]](/lazycluster/cluster/dask_cluster.py#L200)</span>

### DaskCluster.get_client

```python
get_client(self, timeout: int = 2) → distributed.client.Client
```

Get a connected Dask client. 

**Args:**

 - `timeout` (int):  The timeout (s) value passed on to the Dask `Client` constructor. Defaults to 2.

**Raises:**

 - `TimeoutError`:  If client connection `timeout` expires.


