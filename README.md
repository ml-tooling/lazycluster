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
  <a href="#api-docs">API Docs</a> •
  <a href="#support">Support</a> •
  <a href="https://github.com/ml-tooling/ml-workspace/issues/new?labels=bug&template=01_bug-report.md">Report a Bug</a> •
  <a href="#contribution">Contribution</a>
</p>

**lazycluster** is a Python library intended to liberate data scientists and machine learning engineers by abstracting 
away cluster management and configuration so that they are be able to focus on its actual tasks. Especially, the easy 
and convenient cluster setup with Python for various distributed machine learning frameworks is emphasized.

## Highlights

- **High-Level API for starting clusters:** 
    - <a href="#">DASK</a>
    - <a href="#">PyTorch</a> *(WIP)* 
    - *Further supported *lazyclusters* to come ...*
- **Lower-level API for:**
    - Managing <a href="#">Runtimes</a> or <a href="#">RuntimeGroups</a> to:
        - a-/synchronously execute <a href="#">RuntimeTasks</a> remotely by leveraging the power of ssh
        - expose services (e.g. a DB) from or to a <a href="#">Runtimes</a> or in a whole <a href="#">RuntimeGroup</a>

## Getting Started

### Installation

`pip install lazycluster` 

### Usage Example

Prerequisite: Passwordless ssh needs to be setup for the used hosts.

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

# The stdout from from the executing `Runtime` can be accessed via the execution log of teh `RuntimeTask`
task.print_log()

# Print the return of the `hello()` call
generator = task.function_returns
print(next(generator))
```
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

## Features

_WIP: Describe with high level features code examples. E.g. DaskCluster, Chunked Preprocessing, Runtime Group Port Handling..._

## Contribution

- Pull requests are encouraged and always welcome. Read [`CONTRIBUTING.md`](https://github.com/ml-tooling/lazycluster/tree/master/CONTRIBUTING.md) and check out [help-wanted](https://github.com/ml-tooling/lazycluster/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3A"help+wanted"+sort%3Areactions-%2B1-desc+) issues.
- Submit github issues for any [feature enhancements](https://github.com/ml-tooling/lazycluster/issues/new?assignees=&labels=feature-request&template=02_feature-request.md&title=), [bugs](https://github.com/ml-tooling/lazycluster/issues/new?assignees=&labels=bug&template=01_bug-report.md&title=), or [documentation](https://github.com/ml-tooling/lazycluster/issues/new?assignees=&labels=enhancement%2C+docs&template=03_documentation.md&title=) problems. 
- By participating in this project you agree to abide by its [Code of Conduct](https://github.com/ml-tooling/lazycluster/tree/master/CODE_OF_CONDUCT.md).

---

Licensed **Apache 2.0**. Created and maintained with ❤️ by developers from SAP in Berlin.