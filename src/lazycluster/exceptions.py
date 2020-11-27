"""Exception module."""

from typing import Any, Optional


class LazyclusterError(Exception):
    """Basic exception class for `lazycluster` library errors."""

    def __init__(self, msg: str, predecessor_excp: Optional[Exception] = None):
        """Constructor method.

        Args:
            msg: The error message.
            predecessor_excp: Optionally, a predecessor exception can be passed on.
        """
        self.msg = msg
        self.predecessor_excp = predecessor_excp

        super().__init__(str(self))

    def __str__(self) -> str:
        if self.predecessor_excp:
            return self.msg + " Predecessor Exception: " + str(self.predecessor_excp)
        return self.msg


class TaskExecutionError(LazyclusterError):
    """This error relates to exceptions occured during RuntimeTask execution."""

    def __init__(
        self,
        task_step_index: int,
        task: Any,  # Needs to be any due to a circular dependency
        host: str,
        execution_log_file_path: str,
        output: str,
        predecessor_excp: Optional[Exception] = None,
    ):
        """Initialization method.

        Args:
            task_step_index: The index of the task step, where an error occured.
            task: The `RuntimeTask` during which execution the error occured.
            host: The host where the execution failed.
            execution_log_file_path: The path to the execution log file on the manager.
            output: Thr ouput (stdout/stderr) generated on the Runtime during execution.
            predecessor_excp: Optionally, a predecessor exception can be passed on.
        """
        super().__init__(
            f"An error occurred during the execution of RuntimeTask {task.name} on host {host} in "
            f"task step {str(task_step_index)}. Please check the respective execution "
            f"log file `{execution_log_file_path}`. The output on the Runtime was:\n {output}",
            predecessor_excp,
        )
        self.task_step_index = task_step_index
        self.task = task


class InvalidRuntimeError(LazyclusterError):
    """Error indicating that a `Runtime` can not be instantiated properly."""

    def __init__(self, host: str):
        """Constructor method.

        Args:
            host: The host which cannot be instantiated as `Runtime`.
        """
        self.host = host

        super().__init__("No runtime could be instantiated for host: " + self.host)


class NoRuntimesDetectedError(LazyclusterError):
    """Error indicating that no `Runtime` could be detcted automatically by a `RuntimeManager` for example."""

    def __init__(self, predecessor_excp: Optional[Exception] = None):
        super().__init__("No Runtimes automatically detected.", predecessor_excp)


class PortInUseError(LazyclusterError):
    """Error indicating that a port is already in use in a `RuntimeGroup` or on the local machine."""

    def __init__(
        self,
        port: int,
        group: Optional[Any] = None,  # Needs to be any due to a circular dependency
        runtime: Optional[Any] = None,  # Needs to be any due to a circular dependency
    ) -> None:
        """Constructor.

        Args:
            port (int): [description]
            group (Optional[Any], optional): [description]. Defaults to None.
            runtime (Optional[Any], optional): [description]. Defaults to None.
        """
        self.port = port
        self.group = group
        self.runtime = runtime

        if group:
            msg = "Port " + str(
                port
            ) + " is already in use in at least one `Runtime` in the group or on the local " "machine. Group: " + str(
                group
            )
        elif runtime:
            msg = (
                "Port "
                + str(port)
                + " is already in use on Runtime "
                + runtime.host
                + ". Runtime: "
                + str(runtime)
            )
        else:
            msg = "Port " + str(port) + " is already in use."

        super().__init__(msg)


class NoPortsLeftError(LazyclusterError):
    """Error indicating that there are no more ports left from the given port list."""

    def __init__(self) -> None:
        """Constructor method."""
        msg = "No free port could be determined. No more ports left in port list."
        super().__init__(msg)


class PathCreationError(LazyclusterError):
    """Error indicating that a given path could not be created."""

    def __init__(self, path: str, host: Optional[str] = None):
        """Constructor method.

        Args:
            path: The path which should be created.
            host: The host where the path should be created.
        """
        self.path = path
        self.host = host

        if host:
            super().__init__(f"The path {path} could not be created on host {host}")
        else:
            super().__init__(f"The path {path} could not be created")
