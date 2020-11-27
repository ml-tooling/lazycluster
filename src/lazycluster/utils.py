import logging
import os
import time


class ExecutionFileLogUtil(object):
    """Generic class used to write log files."""

    def __init__(self, runtime_host: str, taskname: str) -> None:
        """Initialization method.

        Note:
            The log file file be placed in directory named `runtime_host` within the `Environment.main_directory`.

        Args:
            runtime_host: The host of the `Runtime`, where the execution takes place.
            taskname: The name of the `RuntimeTask` to be executed.
        """
        self.runtime_host = runtime_host
        self.taskname = taskname
        self.file_extension = "log"
        self.log = logging.getLogger(__name__)
        self._main_dir = os.path.join(Environment.main_directory, "execution_log")
        self._creation_timestamp = Timestamp()

    @property
    def file_path(self) -> str:
        """Get the full path to the log file.

        Note:
            Although, you can access the path, it does not necessary mean that it already exists. The file eventually
            gets written when the execution of the `RuntimeTask` is started.

        """
        return os.path.join(
            self.directory_path,
            f"{self.taskname}_{self._creation_timestamp.get_unformatted()}"
            f".{self.file_extension}",
        )

    @property
    def directory_path(self) -> str:
        """Get the full path to the directory where this logfile gets written to."""
        path = os.path.join(self._main_dir, f"{self.runtime_host}")

        if not os.path.exists(path):
            os.makedirs(path)

        return path

    def get_write_mode(self) -> str:
        # Append if file exists otherwise create the file
        return "a" if os.path.exists(self.file_path) else "w+"


class Environment(object):
    """This class contains environment variables."""

    main_directory = os.path.abspath("./lazycluster")

    third_party_log_level = logging.CRITICAL

    use_dev_version = False

    @classmethod
    def set_main_directory(cls, dir: str) -> None:
        """Setter for the library's main directory on the manager.

        Note:
            A relative path ist also accepted and translated to an absolute path.

        Args:
            dir: Relative or absolute path.
        """
        cls.main_directory = os.path.abspath(dir)

    @classmethod
    def set_third_party_log_level(cls, log_level: int) -> None:
        """Setter for `third_party_log_level` to control the standard python logging behavior of used libraries.

        Affected libraries: paramiko

        Note:
            The class variable `third_party_log_level` defaults to `logging.Error`, e.g. only paramiko errors
            will be shown.

        Args:
            log_level: Standard python log level values as defined in `logging` like `logging.ERROR`.
        """
        logging.getLogger("paramiko").setLevel(log_level)
        logging.getLogger("invoke").setLevel(log_level)

        if log_level == logging.ERROR or log_level == logging.CRITICAL:
            logging.basicConfig(
                format="[%(levelname)s] %(message)s", level=logging.INFO
            )
        else:
            logging.basicConfig(
                format="[%(levelname)s] %(name)s %(message)s", level=logging.INFO
            )

    @classmethod
    def use_lazycluster_dev_version(cls) -> None:
        """This methods makes sure that the latest lazycluster developement version will be installed on the Runtimes.

        This means the latest commit in the develop branch will be installed on the Runtimes.

        Note:
            Please make sure that you install the same version on the manager as well.
        """
        # Todo: Refactor to a clean solution
        cls.use_dev_version = True


class Timestamp(object):
    """Custom Timestamp class with convenient methods."""

    def __init__(self) -> None:
        """Initializes the object with the current date/time."""
        self._seconds_since_epoch = time.time()

        # Convert seconds since epoch to struct_time
        self._time_obj = time.localtime(self._seconds_since_epoch)

        # Ensure that each field has a fixed number of letters, so needed for representations w/o delimiters
        self.year = str(self._time_obj.tm_year)
        self.month = (
            str(self._time_obj.tm_mon)
            if len(str(self._time_obj.tm_mon)) == 2
            else f"0{str(self._time_obj.tm_mon)}"
        )
        self.day = (
            str(self._time_obj.tm_mday)
            if len(str(self._time_obj.tm_mday)) == 2
            else f"0{str(self._time_obj.tm_mday)}"
        )

        self.hour = (
            str(self._time_obj.tm_hour)
            if len(str(self._time_obj.tm_hour)) == 2
            else f"0{str(self._time_obj.tm_hour)}"
        )
        self.min = (
            str(self._time_obj.tm_min)
            if len(str(self._time_obj.tm_min)) == 2
            else f"0{str(self._time_obj.tm_min)}"
        )
        self.sec = (
            str(self._time_obj.tm_sec)
            if len(str(self._time_obj.tm_sec)) == 2
            else f"0{str(self._time_obj.tm_sec)}"
        )

    def get_unformatted(self) -> str:
        """Fixed length representation w/o delimiters in format: yyyymmddhhmmss."""
        return self.year + self.month + self.day + self.hour + self.min + self.sec

    def get_formatted(self) -> str:
        """Formatted fixed length representation with delimiters in format: yyyy-mm-dd hh:mm:ss."""
        return f"{self.year}-{self.month}-{self.day} {self.hour}:{self.min}:{self.sec}"
