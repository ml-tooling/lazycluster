
**Source:** [/lazycluster/exceptions.py#L0](/lazycluster/exceptions.py#L0)


-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L6)</span>

## LazyclusterError class

Basic exception class for `lazycluster` library errors. 

-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L9)</span>

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

 - `msg` (str):  The error message.



-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L26)</span>

## InvalidRuntimeError class

Error indicating that a `Runtime` can not be instantiated properly. 

-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L29)</span>

### InvalidRuntimeError.`__init__`

```python
__init__(self, host:  str)
```

Constructor method.

**Args:**

 - `host` (str):  The host which cannot be instantiated as `Runtime`.



-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L40)</span>

## NoRuntimesDetectedError class

Error indicating that no `Runtime` could be detcted automatically by a `RuntimeManager` for example. 

-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L42)</span>

### NoRuntimesDetectedError.`__init__`

```python
__init__(self, predecessor_excp:  Union[Exception, NoneType]  =  None)
```

Constructor method.

**Args:**

 - `msg` (str):  The error message.



-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L46)</span>

## PortInUseError class

Error indicating that a port is already in use in a `RuntimeGroup` or on the local machine. 

-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L49)</span>

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
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L73)</span>

## NoPortsLeftError class

Error indicating that there are no more ports left from the given port list. 

-------------------
<span style="float:right;">[[source]](/lazycluster/exceptions.py#L76)</span>

### NoPortsLeftError.`__init__`

```python
__init__(self)
```

Constructor method.




