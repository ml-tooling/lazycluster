from lazycluster import about

__version__ = about.__version__

from lazycluster.exceptions import *
from lazycluster.runtime_mgmt import *
from lazycluster.runtimes import *

# from .settings import BRANCH, GITHUB_URL, PIP_PROJECT_NAME
from .utils import Environment

Environment.set_third_party_log_level(Environment.third_party_log_level)
