
<a href="/lazycluster/utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `lazycluster.utils`




-------------------
<a href="/lazycluster/utils.py#L6"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ExecutionFileLogUtil`
Generic class used to write log files.
 


#### <kbd>property</kbd> ExecutionFileLogUtil.directory_path
 Get the full path to the directory where this logfile gets written to.
 


#### <kbd>property</kbd> ExecutionFileLogUtil.file_path
 Get the full path to the log file.


**Note:**

 Although, you can access the path, it does not necessary mean that it already exists. The file eventually
 gets written when the execution of the `RuntimeTask` is started.


-------------------
<a href="/lazycluster/utils.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ExecutionFileLogUtil.__init__`

```python
__init__(runtime_host, taskname)
```
Initialization method.


**Note:**

 The log file file be placed in directory named `runtime_host` within the `Environment.main_directory`.


**Args:**


 - <b>`runtime_host`</b>:  The host of the `Runtime`, where the execution takes place.

 - <b>`taskname`</b>:  The name of the `RuntimeTask` to be executed.



-------------------
<a href="/lazycluster/utils.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ExecutionFileLogUtil.get_write_mode`

```python
get_write_mode() → str
```



-------------------
<a href="/lazycluster/utils.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Environment`
This class contains environment variables.
 




-------------------
<a href="/lazycluster/utils.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `Environment.set_main_directory`

```python
set_main_directory(dir: str)
```
Setter for the library's main directory on the manager.


**Note:**

 A relative path ist also accepted and translated to an absolute path.


**Args:**


 - <b>`dir`</b>:  Relative or absolute path.

-------------------
<a href="/lazycluster/utils.py#L77"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `Environment.set_third_party_log_level`

```python
set_third_party_log_level(log_level: int)
```
Setter for `third_party_log_level` to control the standard python logging behavior of used libraries.

Affected libraries: paramiko


**Note:**

 The class variable `third_party_log_level` defaults to `logging.Error`, e.g. only paramiko errors
 will be shown.


**Args:**


 - <b>`log_level`</b>:  Standard python log level values as defined in `logging` like `logging.ERROR`.

-------------------
<a href="/lazycluster/utils.py#L99"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `Environment.use_lazycluster_dev_version`

```python
use_lazycluster_dev_version()
```
This methods makes sure that the latest lazycluster developement version will be installed on the Runtimes. 
This means the latest commit in the develop branch will be installed on the Runtimes. 


**Note:**

 Please make sure that you install the same version on the manager as well. 


-------------------
<a href="/lazycluster/utils.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Timestamp`
Custom Timestamp class with convenient methods.
 


-------------------
<a href="/lazycluster/utils.py#L114"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Timestamp.__init__`

```python
__init__()
```
Initializes the object with the current date/time.
 



-------------------
<a href="/lazycluster/utils.py#L136"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Timestamp.get_formatted`

```python
get_formatted() → str
```
Formatted fixed length representation with delimiters in format: yyyy-mm-dd hh:mm:ss.
 

-------------------
<a href="/lazycluster/utils.py#L131"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Timestamp.get_unformatted`

```python
get_unformatted() → str
```
Fixed length representation w/o delimiters in format: yyyymmddhhmmss.
 



