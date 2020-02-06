
**Source:** [/lazycluster/utils.py#L0](/lazycluster/utils.py#L0)


-------------------
<span style="float:right;">[[source]](/lazycluster/utils.py#L6)</span>

## ExecutionFileLogUtil class

Generic class used to write log files.

  


#### ExecutionFileLogUtil.directory_path
 
Get the full path to the directory where this logfile gets written to.

  


#### ExecutionFileLogUtil.file_path
 
Get the full path to the log file.



**Note:**


  Although, you can access the path, it does not necessary mean that it already exists. The file eventually

  gets written when the execution of the `RuntimeTask` is started.


-------------------
<span style="float:right;">[[source]](/lazycluster/utils.py#L10)</span>

### ExecutionFileLogUtil.`__init__`

```python
__init__(self, runtime_host, taskname)
```

Initialization method.



**Note:**


  The log file file be placed in directory named `runtime_host` within the `Environment.main_directory`.



**Args:**


 - `runtime_host`:  The host of the `Runtime`, where the execution takes place.

 - `taskname`:  The name of the `RuntimeTask` to be executed.



-------------------
<span style="float:right;">[[source]](/lazycluster/utils.py#L50)</span>

### ExecutionFileLogUtil.get_write_mode

```python
get_write_mode(self) → str
```




-------------------
<span style="float:right;">[[source]](/lazycluster/utils.py#L55)</span>

## Environment class

This class contains environment variables.

  





-------------------
<span style="float:right;">[[source]](/lazycluster/utils.py#L96)</span>

## Timestamp class

Custom Timestamp class with convenient methods.

  


-------------------
<span style="float:right;">[[source]](/lazycluster/utils.py#L100)</span>

### Timestamp.`__init__`

```python
__init__(self)
```

Initializes the object with the current date/time.

  



-------------------
<span style="float:right;">[[source]](/lazycluster/utils.py#L122)</span>

### Timestamp.get_formatted

```python
get_formatted(self) → str
```

Formatted fixed length representation with delimiters in format: yyyy-mm-dd hh:mm:ss.

  

-------------------
<span style="float:right;">[[source]](/lazycluster/utils.py#L117)</span>

### Timestamp.get_unformatted

```python
get_unformatted(self) → str
```

Fixed length representation w/o delimiters in format: yyyymmddhhmmss.

  



