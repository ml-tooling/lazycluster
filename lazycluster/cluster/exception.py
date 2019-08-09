"""Exception module of the cluster classes based on ml-runtimes lib.

Note: The lazycluster.exception.MlRuntimeError will be the parent class of all defined exception classes here.
"""

from lazycluster.exceptions import MlRuntimeError


class MasterStartError(MlRuntimeError):
    """Error indicating that the cluster master instance could not be started successfully. """

    def __init__(self, host: str, port: int):
        """Constructor method.

        Args:
            host (str): The host where the cluster master instance should be started.
            port (int): The port of the cluster master instance.
        """
        self.port = port
        super().__init__('The cluster master instance could not be started successfully on host `' + host + '` on port '
                         + str(port))
