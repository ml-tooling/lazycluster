<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `lazycluster.exceptions`
Exception module. 



---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L6"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LazyclusterError`
Basic exception class for `lazycluster` library errors. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L9"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(msg: str, predecessor_excp: Optional[Exception] = None)
```

Constructor method. 



**Args:**
 
 - <b>`msg`</b>:  The error message. 
 - <b>`predecessor_excp`</b>:  Optionally, a predecessor exception can be passed on. 





---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TaskExecutionError`
This error relates to exceptions occured during RuntimeTask execution. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    task_step_index: int,
    task: Any,
    host: str,
    execution_log_file_path: str,
    output: str,
    predecessor_excp: Optional[Exception] = None
)
```

Initialization method. 



**Args:**
 
 - <b>`task_step_index`</b>:  The index of the task step, where an error occured. 
 - <b>`task`</b>:  The `RuntimeTask` during which execution the error occured. 
 - <b>`host`</b>:  The host where the execution failed. 
 - <b>`execution_log_file_path`</b>:  The path to the execution log file on the manager. 
 - <b>`output`</b>:  Thr ouput (stdout/stderr) generated on the Runtime during execution. 
 - <b>`predecessor_excp`</b>:  Optionally, a predecessor exception can be passed on. 





---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L59"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `InvalidRuntimeError`
Error indicating that a `Runtime` can not be instantiated properly. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L62"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(host: str)
```

Constructor method. 



**Args:**
 
 - <b>`host`</b>:  The host which cannot be instantiated as `Runtime`. 





---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L73"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `NoRuntimesDetectedError`
Error indicating that no `Runtime` could be detcted automatically by a `RuntimeManager` for example. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L76"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(predecessor_excp: Optional[Exception] = None)
```









---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L80"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PortInUseError`
Error indicating that a port is already in use in a `RuntimeGroup` or on the local machine. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L83"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    port: int,
    group: Optional[Any] = None,
    runtime: Optional[Any] = None
) → None
```

Constructor. 



**Args:**
 
 - <b>`port`</b> (int):  [description] 
 - <b>`group`</b> (Optional[Any], optional):  [description]. Defaults to None. 
 - <b>`runtime`</b> (Optional[Any], optional):  [description]. Defaults to None. 





---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L121"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `NoPortsLeftError`
Error indicating that there are no more ports left from the given port list. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L124"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__() → None
```

Constructor method. 





---

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L130"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PathCreationError`
Error indicating that a given path could not be created. 

<a href="https://github.com/ml-tooling/lazycluster/blob/main/src/lazycluster/exceptions.py#L133"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(path: str, host: Optional[str] = None)
```

Constructor method. 



**Args:**
 
 - <b>`path`</b>:  The path which should be created. 
 - <b>`host`</b>:  The host where the path should be created. 







---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
