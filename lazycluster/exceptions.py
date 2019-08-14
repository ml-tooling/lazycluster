"""Exception module."""

from typing import Optional


class LazyclusterError(Exception):
    """Basic exception class for `lazycluster` library errors. """

    def __init__(self, msg: str, predecessor_excp: Optional[Exception] = None):
        """Constructor method.

         Args:
             msg (str): The error message.
         """
        self.msg = msg
        self.predecessor_excp = predecessor_excp

        super().__init__(str(self))

    def __str__(self):
        if self.predecessor_excp:
            return self.msg + ' Predecessor Exception: ' + str(self.predecessor_excp)
        return self.msg


class InvalidRuntimeError(LazyclusterError):
    """Error indicating that a `Runtime` can not be instantiated properly. """

    def __init__(self, host: str):
        """Constructor method.

        Args:
            host (str): The host which cannot be instantiated as `Runtime`.
        """
        self.host = host

        super().__init__('No runtime could be instantiated for host :' + self.host)


class NoRuntimesDetectedError(LazyclusterError):
    """Error indicating that no `Runtime` could be detcted automatically by a `RuntimeManager` for example. """
    def __init__(self, predecessor_excp: Optional[Exception] = None):
        super().__init__('No Runtimes automatically detected.', predecessor_excp)


class PortInUseError(LazyclusterError):
    """Error indicating that a port is already in use in a `RuntimeGroup` or on the local machine. """

    def __init__(self, port: int, group: Optional['RuntimeGroup'] = None, runtime: Optional['Runtime'] = None):
        """Constructor method.

        Args:
            port (int): The port in use.
            group (Optional[RuntimeGroup]): The group object where the port is in use.
            runtime (Optional[Runtime]: The runtime object where the port is in use.
        """
        self.port = port
        self.group = group
        self.runtime = runtime

        if group:
            msg = 'Port ' + str(port) + ' is already in use in at least one `Runtime` in the group or on the local ' \
                  'machine. Group: ' + str(group)
        elif runtime:
            msg = 'Port ' + str(port) + ' is already in use in ' + runtime.type_str + ' ' + runtime.host + \
                  '. Runtime: ' + str(runtime)
        else:
            msg = 'Port ' + str(port) + ' is already in use.'

        super().__init__(msg)


class NoPortsLeftError(LazyclusterError):
    """Error indicating that there are no more ports left from the given port list. """

    def __init__(self):
        """Constructor method."""
        msg = 'No free port could be determined. No more ports left in port list.'
        super().__init__(msg)
