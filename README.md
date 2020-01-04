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


> **Concept Definition:** *[RuntimeTask](./docs/runtimes.md#runtimetask-class)* <a name="task"></a>
>
> A `RuntimeTask` is a composition of multiple elemantary task steps, such as `send file`, `get file`, `run shell command`, `run python function`. A `RuntimeTask` can be executed on a remote host either by handing it over to a `Runtime` object or standalone by handing over a [fabric Connection](http://docs.fabfile.org/en/2.5/api/connection.html) object to the execute method of the `RuntimeTask`. Consequently, all invididual task steps are executed sequentially. Moreover, a `RuntimeTask` object captures the stdout of the remote execution as logs. An example for a `RuntimeTask` could be to send a csv file to a `Runtime`, execute a python function that is transforming the csv file and finally get the file back. 

> **Concept Definition:** *[Runtime](./docs/runtimes.md#runtime-class)* <a name="runtime"></a>
>
> A `Runtime` is the logical representation of a remote host. Typically, the host is another server or a virtual machine / container on another server. This python class provides several methods for utilizing remote resources such as the port exposure from / to a `Runtime` as well as the execution of `RuntimeTasks`. A `Runtime` has a working directory. Usually, the execution of a `RuntimeTask` is conducted relatively to this directory if no other path is explicitly given. The working directory can be manually set during the initialization. Otherwise, a temporary directory gets created that might eventually be removed.
 

> **Concept Definition:** *[RuntimeGroup](./docs/runtimes.md#runtimetask-class)* 
>
> A `RuntimeGroup` is the representation of logically related `Runtimes` and provides convenient methods for managing those related `Runtimes`. Most methods are wrappers around their counterparts in the `Runtime` class. Typical usage examples are exposing a port (i.e. a service such as a DB) in the `RuntimeGroup`, transfer files, or execute  a `RuntimeTask` on the contained `Runtimes`. Additionally, all concrete [RuntimeCluster](./docs/cluster.runtime_cluster.md#runtimecluster-class) (e.g. the [HyperoptCluster](./docs/cluster.hyperopt_cluster.md#hyperoptcluster-class))implementations rely on `RuntimeGroups` for example.


> **Concept Definition:** *Manager*<a name="manager"></a>
>
> The `manager` refers to the host where you are actually using the lazycluster library, since all desired lazycluster entities are managed from here. **Caution**: It is not to be confused with the [RuntimeManager](./docs/runtime_mgmt.md#runtimemanager-class) class.
---

<br>

## Getting started

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
- Unix based OS

**Runtime host requirements:**
- Python >= 3.6
- ssh server (e.g. openssh-server)
- [passwordless ssh](https://linuxize.com/post/how-to-setup-passwordless-ssh-login/) to the host (recommended)
- Unix based OS

**Note:**

  Passwordless ssh needs to be setup for the hosts to be used as [Runtimes](./docs/runtimes.md#runtime-class) for the most convenient user experience. Otherwise, you need to pass the connection details to Runtime.\_\_init__ via connection_kwargs. These parameters will be passed on to the [fabric.Connection](http://docs.fabfile.org/en/2.4/api/connection.html#connect-kwargs-arg).

### Usage example
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

### Use CLI to manage local ssh configuration to enable [Runtime](./docs/runtimes.md#runtime-class) use
<details>
<summary><b>Details</b> (click to expand...)</summary>

#### Add host to ssh config 
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

#### Delete the ssh config of `Runtime`
*Note:* Corresponding remote ikernel will be deleted too if present.
```bash
lazycluster delete-runtime host-1
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

### Use [RuntimeManager](./docs/runtime_mgmt.md#runtimemanager-class) to create a [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class) based on the local ssh config
The [RuntimeManager](./docs/runtime_mgmt.md#runtimemanager-class) can automatically detect all available [Runtimes](./docs/runtimes.md#runtime-class) based on the [manager's](#manager) local ssh config and eventually create a necessary [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class) for you.
<details>
<summary><b>Details</b> (click to expand...)</summary>

```python
from lazycluster import RuntimeManager, RuntimeGroup

runtime_group = RuntimeManager().create_group()
```
</details>

### Expose a service from a [Runtime](./docs/runtimes.md#runtime-class)
A DB is running on a remote host on port `runtime_port` and the DB is only accessible from the remote host. 
But you also want to access the service from the [manager](#manager) on port `local_port`. Then you can use this 
method to expose the service which is running on the remote host to the [manager](#manager).
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
A DB is running on the [manager](#manager) on port `local_port` and the DB is only accessible from the [manager](#manager). 
But you also want to access the service on the remote `Runtime` on port `runtime_port`. Then you can use 
this method to expose the service which is running on the [manager](#manager) to the remote host.
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

### Expose a service to a whole [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class) or from one contained [Runtime](./docs/runtimes.md#runtime-class) in the [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class)
Now we extend the two previous examples by using a `RuntimeGroup` instead of just a single `Runtime`.
<details>
<summary><b>Details</b> (click to expand...)</summary>

```python
from lazycluster import RuntimeGroup

# Create a RuntimeGroup
runtime_group = RuntimeGroup('host1', 'host-2', 'host-3')

# Make the local port 50000 accessible on all Runtimes contained in the RuntimeGroup.
# Note: The port can also be exposed to a subset of the contained Runtimes by using the
# method parameter exclude_hosts.
runtime_group.expose_port_to_runtimes(50000)


# Make the port 40000 which is running on host-1 accessible on all other Runtimes in the RuntimeGroup
runtime_group.expose_port_from_runtime_to_group('host-1', 40000)
```
</details>

### Simple preprocessing example
Read a local (on the [manager](#manager)) CSV file and upper case chunks in parallel using [RuntimeTasks](./docs/runtimes.md#runtimetask-class)
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

### Scalable analytics with [Dask](https://dask.org/)
Most simple way to use DASK in a cluster based on a [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class) created by the [RuntimeManager](./docs/runtime_mgmt.md#runtimemanager-class). The `RuntimeManager` can automatically detect all available [Runtimes](./docs/runtimes.md#runtime-class) based on the [manager's](#manager) ssh config and eventually create a necessary `RuntimeGroup` for you. This `RuntimeGroup` is then handed over to [DaskCluster](./docs/cluster.dask_cluster.md#daskcluster-class) during initialization.

The DASK `scheduler` instance gets started [manager](#manager). Additionally, multiple DASK `worker` processes get started in the `RuntimeGroup`, i.e. in the contained `Runtimes`. The default number of workers is equal to the number of `Runtimes` contained in the `RuntimeGroup`.

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

### Distributed hyperparameter tuning with [Hyperopt](https://github.com/hyperopt/hyperopt/wiki/Parallelizing-Evaluations-During-Search-via-MongoDB)
Most simple way to use Hyperopt in a cluster based on a [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class) created by the [RuntimeManager](./docs/runtime_mgmt.md#runtimemanager-class). The `RuntimeManager` can automatically detect all available [Runtimes](./docs/runtimes.md#runtime-class) based on the [manager's](#manager) ssh config and eventually create a necessary `RuntimeGroup` for you. This `RuntimeGroup` is then handed over to [HyperoptCluster](./docs/cluster.hyperopt_cluster.md#hyperoptcluster-class) during initialization.

A MongoDB instance gets started on the [manager](#manager). Additionally, multiple hyperopt `worker` processes get started in the `RuntimeGroup`, i.e. on the contained `Runtimes`. The default number of workers is equal to the number of `Runtimes` contained in the `RuntimeGroup`.

**Prerequisites:** 
- [MongoDB server must be installed](https://docs.mongodb.com/manual/administration/install-on-linux/) on the [manager](#manager).
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

**Note:** The call to `fmin` is also done on the [manager](#manager). The `objective_function` gets sent to the hyperopt workers by fmin via MongoDB. So there is no need to trigger the execution of `fmin` or the `objective_function` on the individual `Runtimes`. See [hyperopt docs](https://github.com/hyperopt/hyperopt/wiki/Parallelizing-Evaluations-During-Search-via-MongoDB) for detailed explanation.  

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

### Logging, exception handling and debugging
`lazycluster` aims to abstract away the complexity implied by using multiple distributed [Runtimes](./docs/runtimes.md#runtime-class) and provides an intuitive high level API fur this purpose. The lazycluster [manager](#manager) orchestrates the individual components of the distributed setup. A common use case could be to use lazycluster in order to launch a distributed [hyperopt cluster](https://github.com/hyperopt/hyperopt/wiki/Parallelizing-Evaluations-During-Search-via-MongoDB). In this case, we have the lazycluster [manager](#manager), that starts a [MongoDB](https://www.mongodb.com/) instance, starts the hyperopt worker processes on multiple Runtimes and ensures the required communication via ssh between these instances. Each individual component could potentially fail including the 3rd party ones such as hyperopt workers. Since `lazycluster` is a generic library and debugging a distributed system is  an instrinsically non-trivial task, we tried to emphasize logging and good exception handling practices so that you can stay lazy.

#### Standard Python log
We use the standard Python [logging module](https://docs.python.org/3.6/library/logging.html#formatter-objects) in order to log everything of interest on the [manager](#manager).
<details>
<summary><b>Details</b> (click to expand...)</summary>

Per default we recommend to set the basicConfig log level to `logging.INFO`. Consequently, you will get relevant status updates about the progress of launching a cluster for example. Of course, you can adjust the log level to `logging.DEBUG` or anything you like. 

We like to use the following basic configuration when using lazycluster in a [Jupyter](https://jupyter.org/) notebook:
```python
import logging

logging.basicConfig(format='[%(levelname)s] %(name)s %(message)s', 
                    level=logging.INFO,
                    stream=sys.stdout)
```

**Note:**
Some 3rd party libraries produce a lot of INFO messages, which are usually not of interest for the user. This is particular true for [Paramiko](http://www.paramiko.org/). We base most ssh handling on [Fabric](http://www.fabfile.org/) which is based on Paramiko. We decided to set the log level for these libraries to `logging.Error` per default. This happens in the `__init__.py` module of the lazycluster package. And will be set once when importing the first module or class from `lazycluster`. If you want to change the log level of 3rd party libs you can set it the following way:
```python
import logging
from lazycluster import Environment

# Effects logs of all libraries that were initially set to logging.ERROR
lazycluster.Environment.set_third_party_log_level(logging.INFO)

# Of course, you can set the log level manually for each library / module
logging.getLogger('paramiko').setLevel(logging.DEBUG)
logging.getLogger('lazycluster').setLevel(logging.INFO)
```
See `set_third_party_log_level()` of the [Environment](./docs/utils.md#environment) class for a full list of affected libraries.
</details>

<br />

#### Execution log
The execution log aims to provide a central access point to logs produced on the Runtimes.
<details>
<summary><b>Details</b> (click to expand...)</summary>

This type of log contains mainly the stdout produced when executing a [RuntimeTask](#task) on a [Runtime](#runtime). If you are new to lazycluster or you never used the lower level API directly, then you might think the execution log is not relevant for you. But it is :) Also the concrete cluster implementations (e.g. [DaskCluster](./docs/cluster.dask_cluster.md#daskcluster-class) or [HyperoptCluster](./docs/cluster.hyperopt_cluster.md#hyperoptcluster-class)) are built on top of the lower-level API. You can think of it as the kind of log which you can use to understand what actually happened on your `Runtimes`.

You can access the execution log in two different ways. Either by accessing the `execution_log` property of a `RuntimeTask` or by checking the generated log files on the manager. Moreover, the `Runtime` as well as the `RuntimeGroup` provide a `print_log()` function which prints the `execution_log` of the `RuntimeTasks` that were executed on the `Runtimes`. The `execution_log` property is a list and can be accessed via index. Each log entry corresponds to the output of a single (fully executed) step of the `RuntimeTask`. This might be useful if you need to access the ouput of a concrete `RuntimeTask` step. See the [concept definition](#task) and the [class documentation](./docs/runtimes.md#runtimetask-class) of the `RuntimeTask` for further details.

```python
from lazycluster import Runtime, RuntimeTask

# Create the task
task = RuntimeTask('exec-log-demo')

# Add 2 individual task steps
task.run_command('echo Hello')
task.run_command('echo lazycluster!')

# Create a Runtime 
runtime = Runtime('host-1')

# Execute the task remotely on the Runtime
runtime.execute_task(task)

# Access th elog per index
print(task.execution_log[0]) # => 'Hello'
print(task.execution_log[1]) # => 'lazycluster!'

# Let the Runtime print the log
runtime.print_log()
```

**Note:**
It should be noted that `RuntimeTask.run_function()` is actually not a single task step. A call to this method will produce multiple steps, since the Python function that needs to be executed will be send as a pickle file to the remote host. There it gets unpickled, executed and the return data is sent back as a pickle file. This means if you intend to access the exectution log you should be aware that the log contains multiple log entries for the `run_function()` call. But the number of steps per call is fixed. Moreover, you should think about using the return value of a a remotely executed Python function instead of using the execution log for this purpose.

The execution log is written to log files as well by using the [FileLogger](./docs/utils.md#FileLogger) class. The respective directory is per default `./lazycluster/log` on the [manager](#manager). The log directory contains a subfolder for each Runtime (i.e. host) that executed at least one `RuntimeTask`. Inside a Runtime folder you will find one log file per executed RuntimeTask. Each logfile name is generated by concatenating the name of the `RuntimeTask` and a current timestamp. You can configure the path were the log directory gets created by adjusting the lazycluster main directory. See [Environment](./docs/utils.md#environment) for this purpose.

**Attention:**
Sometimes it might happen that the RuntimeTask.`execution_log` property does not contain the full log. This might especially occur when executing a `RuntimeTask` asynchronously and the execution of the `RuntimeTask` failed. In this case always check the log files on the manager when debugging. Moreover, keep in mind that each log entry gets written after its execution. This means if you execute a `RuntimeTask` with just one step that takes some time, then you can access the log on the manager earliest when this step finished its execution.
</details>

<br />

#### Exception handling
Our exception handling concept follows the idea to use standard python classes whenever appropriate. Otherwise, we create a library specific error (i.e. exception) class. 
<details>
<summary><b>Details</b> (click to expand...)</summary>

Each created error class inherits from our base class [LazyclusterError](./docs/exceptions#lazyclusterError) which in turn inherits from Pythons's [Exception](https://docs.python.org/3.6/tutorial/errors.html#user-defined-exceptions) class. We aim to be informative as possible with our used exceptions to guide you to a solution to your problem. So feel encouraged to provide feedback on misleading or unclear error messages, since we strongly believe that guided errors are essential so that you can stay as lazy as possible.

</details>

---

<br>

## Contribution

- Pull requests are encouraged and always welcome. Read [`CONTRIBUTING.md`](https://github.com/ml-tooling/lazycluster/tree/master/CONTRIBUTING.md) and check out [help-wanted](https://github.com/ml-tooling/lazycluster/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3A"help+wanted"+sort%3Areactions-%2B1-desc+) issues.
- Submit github issues for any [feature enhancements](https://github.com/ml-tooling/lazycluster/issues/new?assignees=&labels=feature-request&template=02_feature-request.md&title=), [bugs](https://github.com/ml-tooling/lazycluster/issues/new?assignees=&labels=bug&template=01_bug-report.md&title=), or [documentation](https://github.com/ml-tooling/lazycluster/issues/new?assignees=&labels=enhancement%2C+docs&template=03_documentation.md&title=) problems. 
- By participating in this project you agree to abide by its [Code of Conduct](https://github.com/ml-tooling/lazycluster/tree/master/CODE_OF_CONDUCT.md).

---

Licensed **Apache 2.0**. Created and maintained with ❤️ by developers from SAP in Berlin.
