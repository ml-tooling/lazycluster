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
    - [DASK](./docs/cluster.dask_cluster.md#daskcluster-class)
    - [Hyperopt](#) *(WIP)* 
    - *More *lazyclusters* (e.g. PyTorch, Tensorflow, Horovod, Spark) to come ...*
- **Lower-level API for:**
    - Managing [Runtimes](./docs/runtimes.md#runtime-class) or [RuntimeGroups](./docs/runtime_mgmt.md#runtimegroup-class) to:
        - A-/synchronously execute [RuntimeTasks](./docs/runtimes.md#runtimetask-class) by leveraging the power of ssh
        - Expose services (e.g. a DB) from or to a [Runtime](./docs/runtimes.md#runtime-class) or in a whole [RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class)
- **CLI**
    - List all available [Runtimes](./docs/runtimes.md#runtime-class)
    - Add a [Runtime](./docs/runtimes.md#runtime-class) configuration
    - Delete a [Runtime](./docs/runtimes.md#runtime-class) configuration

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
- passwordless ssh to the host (recommended)

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
```bash
lazycluster list-runtimes
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

### Easily Launch a [Dask Cluster](./docs/cluster.dask_cluster.md#daskcluster-class)
The [RuntimeManager](./docs/runtime_mgmt.md#runtimemanager-class) can automatically detect all available 
[Runtimes](./docs/runtimes.md#runtime-class) based on your local ssh config and eventually create a necessary 
[RuntimeGroup](./docs/runtime_mgmt.md#runtimegroup-class) for you.
Most simple way to launch a cluster based on a `RuntimeGroup` created by the `RuntimeManager`.
<details>
<summary><b>Details</b> (click to expand...)</summary>

```python
from lazycluster import RuntimeManager
from lazycluster.cluster.dask_cluster import DaskCluster

cluster = DaskCluster(RuntimeManager().create_group())
cluster.start()
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

Use different strategies for launching the master and the worker instance by providing custom implementation of 
`MasterLauncher` and `WorkerLauncher`.
<details>
<summary><b>Details</b> (click to expand...)</summary>

```python
cluster = DaskCluster(RuntimeManager().create_group(),
                      MyMasterLauncherImpl(),
                      MyWorkerLauncherImpl)
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
