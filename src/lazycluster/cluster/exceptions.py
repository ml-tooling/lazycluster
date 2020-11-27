"""Exception module for cluster classes.

Note:
    It is intended that the lazycluster.exception.LazyclusterError should be the parent class of all defined exception
    classes here.
"""

from lazycluster.exceptions import LazyclusterError


class MasterStartError(LazyclusterError):
    """Error indicating that the cluster master instance could not be started successfully."""

    def __init__(self, host: str, port: int, cause: str):
        """Initialization method.

        Args:
            host: The host where the cluster master instance should be started.
            port: The port of the cluster master instance.
            cause: More detailed information of the actual root
        """
        self.host = host
        self.port = port
        self.cause = cause
        super().__init__(
            f"The cluster master instance could not be started successfully on host `{host}` on port "
            f"{str(port)}. Cause: {cause}"
        )
