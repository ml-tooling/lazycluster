<h1 align="center">
     lazycluster
    <br>
</h1>

<p align="center">
    <strong>Distributed machine learning made simple.</strong>
</p>

<p align="center">
    <a href="https://github.com/ml-tooling/lazycluster/blob/master/LICENSE" title="ML Hub License"><img src="https://img.shields.io/badge/License-Apache%202.0-green.svg"></a>
    <a href="https://gitter.im/ml-tooling/lazycluster" title="Chat on Gitter"><img src="https://badges.gitter.im/ml-tooling/lazycluster.svg"></a>
    <a href="https://twitter.com/mltooling" title="ML Tooling on Twitter"><img src="https://img.shields.io/twitter/follow/mltooling.svg?style=social"></a>
</p>

<p align="center">
  <a href="#getting-started">Getting Started</a> •
  <a href="#highlights">Highlights</a> •
  <a href="#features">Features</a> •
  <a href="./docs">API Docs</a> •
  <a href="#support">Support</a> •
  <a href="https://github.com/ml-tooling/ml-workspace/issues/new?labels=bug&template=01_bug-report.md">Report a Bug</a> •
  <a href="#contribution">Contribution</a>
</p>

**lazycluster** is a Python library intended to liberate data scientists and machine learning engineers by abstracting 
away cluster management and configuration so that they are able to focus on their actual tasks. Especially, the easy 
and convenient cluster setup with Python for various distributed machine learning frameworks is emphasized.

## Highlights

- **High-Level API for starting clusters:** 
    - [DASK](https://distributed.dask.org/en/latest/)
    - [Hyperopt](https://github.com/hyperopt/hyperopt) 
    - *More *lazyclusters* (e.g. PyTorch, Tensorflow, Horovod, Spark) to come ...*
- **Lower-level API for:**
    - Managing [Runtimes](./docs/runtimes.md#runtime-class) or [RuntimeGroups](./docs/runtime_mgmt.md#runtimegroup-class) to:
        - A-/synchronously execute [RuntimeTasks](./docs/runtimes.md#runtimetask-class) by leveraging the power of ssh
        - Expose services (e.g. a DB) from or to a [Runtime](./docs/runtimes.md#runtime-class) or in a whole [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class)
- **CLI**
    - List all available [Runtimes](./docs/runtimes.md#runtime-class)
    - Add a [Runtime](./docs/runtimes.md#runtime-class) configuration
    - Delete a [Runtime](./docs/runtimes.md#runtime-class) configuration

> **Concept Definition:** *[RuntimeTask](./docs/runtimes.md#runtimetask-class)* 
>
> A `RuntimeTask` is a composition of multiple elemantary task steps, such as `send file`, `get file`, `run shell command`, `run python function`. A `RuntimeTask` can be executed on a remote host either by handing it over to a `Runtime` object or standalone by handing over a [fabric Connection](http://docs.fabfile.org/en/2.5/api/connection.html) object to the execute method of the `RuntimeTask`. Consequently, all invididual task steps are executed sequentially. Moreover, a `RuntimeTask` object captures the stdout of the remote execution as logs. An example for a `RuntimeTask` could be to send a csv file to a `Runtime`, execute a python function that is transforming the csv file and finally get the file back. 

> **Concept Definition:** *[Runtime](./docs/runtimes.md#runtime-class)* 
>
> A `Runtime` is the logical representation of a remote host. Typically, the host is another server or a virtual machine / container on another server. This python class provides several methods for utilizing remote resources such as the port exposure from / to a `Runtime` as well as the execution of `RuntimeTasks`. A `Runtime` has a working directory. Usually, the execution of a `RuntimeTask` is conducted relatively to this directory if no other path is explicitly given. The working directory can be manually set during the initialization. Otherwise, a temporary directory gets created that might eventually be removed.
 

> **Concept Definition:** *[RuntimeGroup](./docs/runtimes.md#runtimetask-class)* 
>
> A `RuntimeGroup` is the representation of logically related `Runtimes` and provides convenient methods for managing those related `Runtimes`. Most methods are wrappers around their counterparts in the `Runtime` class. Typical usage examples are exposing a port (i.e. a service such as a DB) in the `RuntimeGroup`, transfer files, or execute  a `RuntimeTask` on the contained `Runtimes`. Additionally, all concrete [RuntimeCluster](./docs/cluster.runtime_cluster.md#runtimecluster-class) (e.g. the [HyperoptCluster](./docs/cluster.hyperopt_cluster.md#hyperoptcluster-class))implementations rely on `RuntimeGroups` for example.
---

<br>

## Getting Started

### Installation
```bash
pip install lazycluster
``` 
```bash
# Most up-to-date development version
pip install --upgrade git+https://github.com/ml-tooling/lazycluster.git@develop
``` 

### Prerequisites

**For lazycluster installation:**
- Python >= 3.6
- ssh client (e.g. openssh-client)

**Runtime Host Requirements:**
- Python >= 3.6
- ssh server (e.g. openssh-server)
- [passwordless ssh](https://linuxize.com/post/how-to-setup-passwordless-ssh-login/) to the host (recommended)

**Note:**

  Passwordless ssh needs to be setup for the hosts to be used as [Runtimes](./docs/runtimes.md#runtime-class) for the most convenient user experience. Otherwise, you need to pass the connection details to Runtime.\_\_init__ via connection_kwargs. These parameters will be passed on to the [fabric.Connection](http://docs.fabfile.org/en/2.4/api/connection.html#connect-kwargs-arg).

### Usage Example
```python
from lazycluster import RuntimeTask, Runtime

# Define a Python function which will be executed remotely
def hello(name:str):
    return 'Hello ' + name + '!'

# Compose a `RuntimeTask`
task = RuntimeTask('my-first_task').run_command('echo Hello World!') \
                                   .run_function(hello, name='World')
                                   
# Actually execute it remotely in a `Runtime`                                   
task = Runtime('host-1').execute_task(task, execute_async=False)

# The stdout from from the executing `Runtime` can be accessed via the execution log of the `RuntimeTask`
task.print_log()

# Print the return of the `hello()` call
generator = task.function_returns
print(next(generator))
```

---

<br>

## Support

The **lazycluster** project is maintained by [Jan Kalkan](https://www.linkedin.com/in/jan-kalkan-b5390284/). Please 
understand that we won't be able to provide individual support via email. We also believe that help is much more
valuable if it's shared publicly so that more people can benefit from it.

| Type                     | Channel                                              |
| ------------------------ | ------------------------------------------------------ |
| 🚨 **Bug Reports**       | <a href="https://github.com/ml-tooling/lazycluster/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3Abug+sort%3Areactions-%2B1-desc+" title="Open Bug Report"><img src="https://img.shields.io/github/issues/ml-tooling/lazycluster/bug.svg"></a>                                 |
| 🎁 **Feature Requests**  | <a href="https://github.com/ml-tooling/lazycluster/issues?q=is%3Aopen+is%3Aissue+label%3Afeature-request+sort%3Areactions-%2B1-desc" title="Open Feature Request"><img src="https://img.shields.io/github/issues/ml-tooling/lazycluster/feature-request.svg?label=feature%20requests"></a>                                 |
| 👩‍💻 **Usage Questions**   |  <a href="https://stackoverflow.com/questions/tagged/ml-tooling" title="Open Question on Stackoverflow"><img src="https://img.shields.io/badge/stackoverflow-ml--tooling-orange.svg"></a> <a href="https://gitter.im/ml-tooling/lazycluster" title="Chat on Gitter"><img src="https://badges.gitter.im/ml-tooling/lazycluster.svg"></a> |
| 🗯 **General Discussion** | <a href="https://gitter.im/ml-tooling/lazycluster" title="Chat on Gitter"><img src="https://badges.gitter.im/ml-tooling/lazycluster.svg"></a>  <a href="https://twitter.com/mltooling" title="ML Tooling on Twitter"><img src="https://img.shields.io/twitter/follow/mltooling.svg?style=social"></a>

---

<br>

## Features

### Use CLI to Manage Local SSH Configuration to Enable [Runtime](./docs/runtimes.md#runtime-class) Use
<details>
<summary><b>Details</b> (click to expand...)</summary>

#### Add Host to SSH config 
The host is named `localhost` for user `root` accessible on `localhost` port `22` using the private key file found under 
~/.ssh/id_rsa.

```bash
lazycluster add-runtime localhost root@localhost:22 --id_file ~/.ssh/id_rsa
```
![Runtime Added](./docs/img/cli-runtime-added.png)
#### List all available runtimes incl. additional information like cpu, memory, etc.
Moreover, also incative hosts will be shown. Inactive means, that the host could not be reached via ssh and instantiated as a vlaid Runtime.
```bash
lazycluster list-runtimes     # will give short list with hosts
lazycluster list-runtimes -l  # will give print additional host information
```
![List Runtimes](./docs/img/cli-list-runtimes.png)

#### Delete the ssh config for 
*Note:* Corresponding remote ikernel will be deleted too if present.
```bash
lazycluster delete-runtime localhost
```
![Runtime Deleted](./docs/img/cli-runtime-deleted.png)
</details>

### Create [Runtimes](./docs/runtimes.md#runtime-class) & [RuntimeGroups](./docs/runtime_mgmt.md#runtimegroup-class)
<details>
<summary><b>Details</b> (click to expand...)</summary>

```python
from lazycluster import Runtime, RuntimeGroup

rt_1 = Runtime('host-1')
rt_2 = Runtime('host-1', working_dir='/workspace')

runtime_group = RuntimeGroup([rt_1, rt_2])
runtime_group = RuntimeGroup(hosts=['host-1', 'host-2'])
```
</details>

### Use [RuntimeManager](./docs/runtime_mgmt.md#runtimemanager-class) to Create a [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class) Based on the Local ssh Config
The [RuntimeManager](./docs/runtime_mgmt.md#runtimemanager-class) can automatically detect all available [Runtimes](./docs/runtimes.md#runtime-class) based on your local ssh config and eventually create a necessary [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class) for you.
<details>
<summary><b>Details</b> (click to expand...)</summary>

```python
from lazycluster import RuntimeManager, RuntimeGroup

runtime_group = RuntimeManager().create_group()
```
</details>

### Expose a service from a [Runtime](./docs/runtimes.md#runtime-class)
A DB is running on a remote host on port `runtime_port` and the DB is only accessible from the remote host. 
But you also want to access the service from the local machine on port `local_port`. Then you can use this 
method to expose the service which is running on the remote host to localhost.
<details>
<summary><b>Details</b> (click to expand...)</summary>

```python
from lazycluster import Runtime

# Create a Runtime
runtime = Runtime('host-1')

# Make the port 50000 from the Runtime accessible on localhost
runtime.expose_port_from_runtime(50000)

# Make the local port 40000 accessible on the Runtime
runtime.expose_port_to_runtime(40000)
```
</details>

### Expose a service to a [Runtime](./docs/runtimes.md#runtime-class)
A DB is running on localhost on port `local_port` and the DB is only accessible from localhost. 
But you also want to access the service on the remote `Runtime` on port `runtime_port`. Then you can use 
this method to expose the service which is running on localhost to the remote host.
<details>
<summary><b>Details</b> (click to expand...)</summary>

```python
from lazycluster import Runtime

# Create a Runtime
runtime = Runtime('host-1')

# Make the port 50000 from the Runtime accessible on localhost
runtime.expose_port_from_runtime(50000)

# Make the local port 40000 accessible on the Runtime
runtime.expose_port_to_runtime(40000)
```
</details>

### Expose a Service to a Whole [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class) or From One Contained [Runtime](./docs/runtimes.md#runtime-class) in the [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class)
<details>
<summary><b>Details</b> (click to expand...)</summary>

```python
from lazycluster import RuntimeGroup

# Create a RuntimeGroup
runtime_group = RuntimeGroup('host1', 'host-2', 'host-3')

# Make the local port 50000 accessible on all Runtimes contained in the RuntimeGroup
runtime_group.expose_port_to_runtimes(50000)


# Make the port 40000 which is running on host-1 accessible on all other Runtimes in the RuntimeGroup
runtime_group.expose_port_from_runtime_to_group('host-1', 40000)
```
</details>

### Simple Preprocessing Example
Read a local CSV and upper case chunks in parallel using [RuntimeTasks](./docs/runtimes.md#runtimetask-class)
and a [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class).
<details>
<summary><b>Details</b> (click to expand...)</summary>

```python
from typing import List
import pandas as pd
from lazycluster import RuntimeTask, RuntimeManager

# Define the function to be executed remotely
def preprocess(docs: List[str]):
    return [str(doc).lower() for doc in docs]
    
file_path = '/path/to/file.csv'

runtime_group = RuntimeManager().create_group()

tasks = []

# Distribute chunks of the csv and start the preprocessing in parallel in the RuntimeGroup
for df_chunk in pd.read_csv(file_path, sep=';', chunksize=500):
    
    task = RuntimeTask().run_function(preprocess, docs=df_chunk['text'].tolist())
    
    tasks.append(runtime_group.execute_task(task))

# Wait until all executions are done   
runtime_group.join()    

# Get the return data and print it
index = 0
for chunk in runtime_group.function_returns:  
    print('Chunk: ' + str(index))
    index += 1
    print(chunk)
```
</details>

### Scalable Analytics w/ [Dask](https://dask.org/)
Most simple way to use DASK in a cluster based on a [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class) created by the [RuntimeManager](./docs/runtime_mgmt.md#runtimemanager-class). The `RuntimeManager` can automatically detect all available [Runtimes](./docs/runtimes.md#runtime-class) based on your local ssh config and eventually create a necessary `RuntimeGroup` for you. This `RuntimeGroup` is then handed over to [DaskCluster](./docs/cluster.dask_cluster.md#daskcluster-class) during initialization.

The DASK `scheduler` instance gets started on the host where the `DaskCluster` class will be instantiated. We call this host the `master` inspired by the naming of master-worker architectures. Additionally, multiple DASK `worker` processes get started in the `RuntimeGroup`. The default number of workers is equal to the number of `Runtimes` contained in the `RuntimeGroup`.

<details>
<summary><b>Details</b> (click to expand...)</summary>

```python
from lazycluster import RuntimeManager
from lazycluster.cluster.dask_cluster import DaskCluster

# 1st: Create a RuntimeGroup, e.g. by letting the RuntimeManager detect 
#      available hosts (i.e. Runtimes) and create the group for you. 
runtime_group = RuntimeManager().create_group()

# 2nd: Create the DaskCluster instance with the RuntimeGroup.
cluster = DaskCluster(runtime_group)

# 3rd: Let the DaskCluster instantiate all entities on Runtimes 
#      contained in the RuntimeGroup using default values. For custom 
#      configuration check the DaskCluster API documentation.
cluster.start()

# => Now, all cluster entities should be started and you can simply use 
#    it as documented in the hyperopt documentation.
```

Test the cluster setup

```python
# Define test functions to be executed in parallel via DASK
def square(x):
    return x ** 2

def neg(x):
    return -x

# Get a DASK client instance
client = cluster.get_client()

# Execute the computation
A = client.map(square, range(10))
B = client.map(neg, A)
total = client.submit(sum, B, )
res = total.result()

print('Result: ' + str(res))
```
</details>
<br/>

Use different strategies for launching the master and the worker instance by providing custom implementation of `MasterLauncher` and `WorkerLauncher`.
<details>
<summary><b>Details</b> (click to expand...)</summary>

```python
cluster = DaskCluster(RuntimeManager().create_group(),
                      MyMasterLauncherImpl(),
                      MyWorkerLauncherImpl())
cluster.start()
```
</details>

### Distributed Hyperparameter Tuning w/ [Hyperopt](https://github.com/hyperopt/hyperopt/wiki/Parallelizing-Evaluations-During-Search-via-MongoDB)
Most simple way to use Hyperopt in a cluster based on a [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class) created by the [RuntimeManager](./docs/runtime_mgmt.md#runtimemanager-class). The `RuntimeManager` can automatically detect all available [Runtimes](./docs/runtimes.md#runtime-class) based on your local ssh config and eventually create a necessary `RuntimeGroup` for you. This `RuntimeGroup` is then handed over to [HyperoptCluster](./docs/cluster.hyperopt_cluster.md#hyperoptcluster-class) during initialization.

A MongoDB instance gets started on the host where the [HyperoptCluster](./docs/cluster.hyperopt_cluster.md#hyperoptcluster-class) class will be instantiated. We call this host the `master` inspired by the naming of master-worker architectures. Additionally, multiple hyperopt `worker` processes get started in the `RuntimeGroup`. The default number of workers is equal to the number of `Runtimes` contained in the `RuntimeGroup`.

**Prerequisites:** 
- [MongoDB server must be installed](https://docs.mongodb.com/manual/administration/install-on-linux/) on the `master` host.  Moreover, no existing MongoDB instance must be running on the `master` on the port (Default: `27017`) and the dbpath (Default: `/data/db`) used by the `HyperoptCluster`.
  - **Note:** When using the [ml-workspace](https://github.com/ml-tooling/ml-workspace) as the `master` then you can use the provided install script for MongoDB which can be found under `/resources/tools`.
- [Hyperopt must be installed ](https://github.com/hyperopt/hyperopt) on all `Runtimes` where hyperopt workers will be started
    - **Note:** When using the [ml-workspace](https://github.com/ml-tooling/ml-workspace) as hosts for the `Runtimes` then hyperopt is already pre-installed.

<details>
<summary><b>Details</b> (click to expand...)</summary>

```python
from lazycluster import RuntimeManager
from lazycluster.cluster.hyperopt_cluster import HyperoptCluster

# 1st: Create a RuntimeGroup, e.g. by letting the RuntimeManager detect 
#      available hosts (i.e. Runtimes) and create the group for you. 
runtime_group = RuntimeManager().create_group()

# 2nd: Create the HyperoptCluster instance with the RuntimeGroup.
cluster = HyperoptCluster(runtime_group)

# 3rd: Let the HyperoptCluster instantiate all entities on Runtimes 
#      contained in the RuntimeGroup using default values. For custom 
#      configuration check the HyperoptCluster API documentation.
cluster.start()

# => Now, all cluster entities should be started and you can simply use 
#    it as documented in the hyperopt documentation.

```

Test the cluster setup using the simple [example](https://github.com/hyperopt/hyperopt/wiki/Parallelizing-Evaluations-During-Search-via-MongoDB) to minimize the sin function. 

**Note:** The call to `fmin` is also done on localhost (more specifially, on the host acting as). The `objective_function` gets sent to the hyperopt workers by fmin via MongoDB. So there is no need to trigger the execution of `fmin` or the `objective_function` on the individual `Runtimes`. See hyperopt docs for detailed explanation.  

```python
import math
from hyperopt import fmin, tpe, hp
from hyperopt.mongoexp import MongoTrials

# You can retrieve the the actual url required by MongoTrials form the cluster instance
trials = MongoTrials(cluster.mongo_trial_url, exp_key='exp1')
objective_function = math.sin
best = fmin(objective_function, hp.uniform('x', -2, 2), trials=trials, algo=tpe.suggest, max_evals=10)
```
</details>
<br/>

Use different strategies for launching the master and the worker instance by providing custom implementation of `MasterLauncher` and `WorkerLauncher`.
<details>
<summary><b>Details</b> (click to expand...)</summary>

```python
cluster = HyperoptCluster(RuntimeManager().create_group(),
                          MyMasterLauncherImpl(),
                          MyWorkerLauncherImpl())
cluster.start()
```
</details>

---

<br>

## Contribution

- Pull requests are encouraged and always welcome. Read [`CONTRIBUTING.md`](https://github.com/ml-tooling/lazycluster/tree/master/CONTRIBUTING.md) and check out [help-wanted](https://github.com/ml-tooling/lazycluster/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3A"help+wanted"+sort%3Areactions-%2B1-desc+) issues.
- Submit github issues for any [feature enhancements](https://github.com/ml-tooling/lazycluster/issues/new?assignees=&labels=feature-request&template=02_feature-request.md&title=), [bugs](https://github.com/ml-tooling/lazycluster/issues/new?assignees=&labels=bug&template=01_bug-report.md&title=), or [documentation](https://github.com/ml-tooling/lazycluster/issues/new?assignees=&labels=enhancement%2C+docs&template=03_documentation.md&title=) problems. 
- By participating in this project you agree to abide by its [Code of Conduct](https://github.com/ml-tooling/lazycluster/tree/master/CODE_OF_CONDUCT.md).

---

Licensed **Apache 2.0**. Created and maintained with ❤️ by developers from SAP in Berlin.
