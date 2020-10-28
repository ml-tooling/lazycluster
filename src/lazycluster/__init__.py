from lazycluster import about

__version__ = about.__version__

from lazycluster.exceptions import *
from lazycluster.runtime_mgmt import RuntimeGroup, RuntimeManager
from lazycluster.runtimes import Runtime, RuntimeTask

# from .settings import BRANCH, GITHUB_URL, PIP_PROJECT_NAME
from lazycluster.utils import Environment

Environment.set_third_party_log_level(Environment.third_party_log_level)
