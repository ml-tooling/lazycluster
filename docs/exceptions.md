
**Source:** [/lazycluster/exceptions.py#L0](/lazycluster/exceptions.py#L0)


-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L6)</span>

## LazyclusterError class

Basic exception class for `lazycluster` library errors.
  

-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L10)</span>

### LazyclusterError.`__init__`

```python
__init__(
    self,
    msg:  str,
    predecessor_excp:  Union[Exception,
    NoneType]  =  None
)
```

Constructor method.

**Args:**

 - `msg`:  The error message.
 - `predecessor_excp`:  Optionally, a predecessor exception can be passed on.



-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L28)</span>

## TaskExecutionError class

This error relates to exceptions occured during RuntimeTask execution.
  

-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L32)</span>

### TaskExecutionError.`__init__`

```python
__init__(
    self,
    task_step_index:  int,
    task:  'RuntimeTask',
    host:  str,
    predecessor_excp:  Union[Exception,
    NoneType]  =  None
)
```

Initialization method.

**Args:**

 - `task_step_index`:  The index of the task step, where an error occured.
 - `task`:  The `RuntimeTask` during which execution the error occured.
 - `host`:  The host where the execution failed.
 - `predecessor_excp`:  Optionally, a predecessor exception can be passed on.



-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L48)</span>

## InvalidRuntimeError class

Error indicating that a `Runtime` can not be instantiated properly.
  

-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L52)</span>

### InvalidRuntimeError.`__init__`

```python
__init__(self, host:  str)
```

Constructor method.

**Args:**

 - `host`:  The host which cannot be instantiated as `Runtime`.



-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L63)</span>

## NoRuntimesDetectedError class

Error indicating that no `Runtime` could be detcted automatically by a `RuntimeManager` for example.
  

-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L66)</span>

### NoRuntimesDetectedError.`__init__`

```python
__init__(self, predecessor_excp:  Union[Exception, NoneType]  =  None)
```

Constructor method.

**Args:**

 - `msg`:  The error message.
 - `predecessor_excp`:  Optionally, a predecessor exception can be passed on.



-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L70)</span>

## PortInUseError class

Error indicating that a port is already in use in a `RuntimeGroup` or on the local machine.
  

-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L74)</span>

### PortInUseError.`__init__`

```python
__init__(
    self,
    port:  int,
    group:  Union[ForwardRef('RuntimeGroup'
), NoneType]  =  None, runtime:  Union[ForwardRef('Runtime'), NoneType]  =  None)
```

Constructor method.

**Args:**

 - `port` (int):  The port in use.
 - `group` (Optional[RuntimeGroup]):  The group object where the port is in use.
runtime (Optional[Runtime]: The runtime object where the port is in use.



-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L98)</span>

## NoPortsLeftError class

Error indicating that there are no more ports left from the given port list.
  

-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L102)</span>

### NoPortsLeftError.`__init__`

```python
__init__(self)
```

Constructor method.
  



-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L109)</span>

## PathCreationError class

Error indicating that a given path could not be created.
  

-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L113)</span>

### PathCreationError.`__init__`

```python
__init__(self, path:  str, host:  Union[str, NoneType]  =  None)
```

Constructor method.

**Args:**

 - `path`:  The path which should be created.
 - `host`:  The host where the path should be created.




