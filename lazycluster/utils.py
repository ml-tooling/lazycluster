import os
import time
import logging


class FileLogger(object):
    """Generic class used to write log files.
    """

    def __init__(self, runtime_host, taskname):
        """Initialization method.

        Args:
            runtime_host: The host of the `Runtime`, where the execution takes place.
            taskname: The name of the `RuntimeTask` to be executed.
        """
        self.runtime_host = runtime_host
        self.taskname = taskname
        self.file_extension = 'log'
        self.log = logging.getLogger(__name__)

    @property
    def file_path(self) -> str:
        """Get the full path to the log file.

        Note:
            Although, you can access the path, it does not necessary mean that it already exists. The file eventually
            gets written when the execution of the `RuntimeTask` is started.

        """
        return os.path.join(Environment.main_directory, f'{self.runtime_host}/{self.taskname}_{get_current_timestamp()}'
                                                        f'.{self.file_extension}')

    @property
    def directory_path(self) -> str:
        """Get the full path to the directory where this logfile gets written to.
        """
        return os.path.join(Environment.main_directory, f'{self.runtime_host}')

    def append_message(self, message: str):
        """Add a message at the end of the log file.

        Args:
            message: The message to be appended.
        """
        if not os.path.exists(self.directory_path):
            os.makedirs(self.directory_path)

        mode = self._get_write_mode()
        path = self.file_path

        self.log.debug(f'Add log message to file {path} with file mode {mode}')

        with open(path, mode) as file:
            file.write(message)

    def _get_write_mode(self) -> str:
        # Append if file exists otherwise create the file
        return 'a' if os.path.exists(self.file_path) else 'w+'


class Environment(object):
    """This class contains environment variables.
    """

    main_directory = os.path.abspath('./lazycluster')

    @classmethod
    def set_main_directory(cls, dir: str):
        """Setter for the library's main directory on the manager.

        Note:
            A relative path ist also accepted and translated to an absolute path.

        Args:
            dir: Relative or absolute path.
        """
        cls.main_directory = os.path.abspath(dir)


def get_current_timestamp() -> str:
    """Get the current timestamp."""
    # Get the seconds since epoch
    seconds_since_epoch = time.time()
    # Convert seconds since epoch to struct_time
    time_obj = time.localtime(seconds_since_epoch)
    return f'{time_obj.tm_year}{time_obj.tm_mon}{time_obj.tm_mday}_{time_obj.tm_hour}_{time_obj.tm_min}_' \
           f'{time_obj.tm_sec}'