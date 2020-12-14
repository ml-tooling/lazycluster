<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/exceptions.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `lazycluster.cluster.exceptions`
Exception module for cluster classes. 



**Note:**

> It is intended that the lazycluster.exception.LazyclusterError should be the parent class of all defined exception classes here. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/exceptions.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `MasterStartError`
Error indicating that the cluster master instance could not be started successfully. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/cluster/exceptions.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(host: str, port: int, cause: str)
```

Initialization method. 



**Args:**
 
 - <b>`host`</b>:  The host where the cluster master instance should be started. 
 - <b>`port`</b>:  The port of the cluster master instance. 
 - <b>`cause`</b>:  More detailed information of the actual root 







---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
