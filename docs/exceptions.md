
<a href="/lazycluster/exceptions.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `lazycluster.exceptions`
Exception module.



-------------------
<a href="/lazycluster/exceptions.py#L6"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LazyclusterError`
Basic exception class for `lazycluster` library errors.
 


-------------------
<a href="/lazycluster/exceptions.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `LazyclusterError.__init__`

```python
__init__(msg: str, predecessor_excp: Optional[Exception] = None)
```
Constructor method.


**Args:**


 - <b>`msg`</b>:  The error message.

 - <b>`predecessor_excp`</b>:  Optionally, a predecessor exception can be passed on.




-------------------
<a href="/lazycluster/exceptions.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TaskExecutionError`
This error relates to exceptions occured during RuntimeTask execution.
 


-------------------
<a href="/lazycluster/exceptions.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `TaskExecutionError.__init__`

```python
__init__(
    task_step_index: int,
    task: 'RuntimeTask',
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




-------------------
<a href="/lazycluster/exceptions.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `InvalidRuntimeError`
Error indicating that a `Runtime` can not be instantiated properly.
 


-------------------
<a href="/lazycluster/exceptions.py#L56"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `InvalidRuntimeError.__init__`

```python
__init__(host: str)
```
Constructor method.


**Args:**


 - <b>`host`</b>:  The host which cannot be instantiated as `Runtime`.




-------------------
<a href="/lazycluster/exceptions.py#L67"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `NoRuntimesDetectedError`
Error indicating that no `Runtime` could be detcted automatically by a `RuntimeManager` for example.
 


-------------------
<a href="/lazycluster/exceptions.py#L70"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `NoRuntimesDetectedError.__init__`

```python
__init__(predecessor_excp: Optional[Exception] = None)
```





-------------------
<a href="/lazycluster/exceptions.py#L74"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PortInUseError`
Error indicating that a port is already in use in a `RuntimeGroup` or on the local machine.
 


-------------------
<a href="/lazycluster/exceptions.py#L78"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PortInUseError.__init__`

```python
__init__(
    port: int,
    group: Optional[ForwardRef('RuntimeGroup')] = None,
    runtime: Optional[ForwardRef('Runtime')] = None
)
```
Constructor method.


**Args:**


 - <b>`port`</b> (int):  The port in use.

 - <b>`group`</b> (Optional[RuntimeGroup]):  The group object where the port is in use.

 - <b>`runtime (Optional[Runtime]`</b>:  The runtime object where the port is in use.




-------------------
<a href="/lazycluster/exceptions.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `NoPortsLeftError`
Error indicating that there are no more ports left from the given port list.
 


-------------------
<a href="/lazycluster/exceptions.py#L106"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `NoPortsLeftError.__init__`

```python
__init__()
```
Constructor method.
 




-------------------
<a href="/lazycluster/exceptions.py#L113"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PathCreationError`
Error indicating that a given path could not be created.
 


-------------------
<a href="/lazycluster/exceptions.py#L117"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PathCreationError.__init__`

```python
__init__(path: str, host: Optional[str] = None)
```
Constructor method.


**Args:**


 - <b>`path`</b>:  The path which should be created.

 - <b>`host`</b>:  The host where the path should be created.





