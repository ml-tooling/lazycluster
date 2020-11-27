import os
import platform
import socket
import subprocess
import sys
from typing import Dict, List, Union

import lazycluster.settings as settings

from .utils import Environment


def get_remaining_ports(ports: List[int], last_used_port: int) -> List[int]:
    """Get a new list with the remaining ports after cutting out all ports until and incl. the last used port.

    Args:
        ports (List[int]): The port list to be updated.
        last_used_port (int): The last port that was actually used. All ports up this one and including this one will
                              be removed.

    Returns:
        List with remaining ports
    """
    skip = True
    final_port_list = []
    for port in ports:
        if skip:
            if port == last_used_port:
                skip = False
            continue
        final_port_list.append(port)
    return final_port_list


def create_list_from_parameter_value(value: Union[object, List[object], None]) -> list:
    """Encapsulates a given object in a list.

    Many methods can either take a single value, a list or None as input. Usually we want to iterate all given
    values. Therefore, this method ensures that a list is always returned.

    Args:
        value (Union[object, List[object], None])): The value that will be mapped onto a list representation.

    Returns:
        List[object]: Either an empty list or a list with all given objects.

    Examples:
        value = None    => []
        value = []      => []
        value = 5       => [5]
        value = [5,6]   => [5,6]
    """
    if not value:
        # => create empty list
        return []
    if not isinstance(value, list):
        # => create list with single value
        return [value]
    # => value is already a list
    return value


def get_localhost_info() -> dict:
    """Get information about the specifications of localhost.

    Returns:
        dict: Current dict keys: 'os', 'cpu_cores', 'memory', 'python_version', 'workspace_version', 'gpus'.
    """
    info = {
        "os": _get_os_on_localhost(),
        "cpu_cores": _get_cpu_count_on_localhost(),
        "memory": _get_memory_on_localhost(),
        "python_version": _get_python_version_on_localhost(),
        "workspace_version": _get_workspace_version_on_localhost(),
        "gpus": _get_gpu_info_for_localhost(),
    }
    return info


def print_localhost_info() -> None:
    """Prints the dictionary retrieved by `get_localhost_info()`."""
    from json import dumps

    json_str = dumps(get_localhost_info())
    print(json_str)


def command_exists_on_localhost(command: str) -> bool:
    """Check if a command exists on localhost."""
    cmd_ext = "hash " + command + ' 2>/dev/null && echo "True" || echo ""'
    return True if os.popen(cmd_ext).read() else False


def localhost_has_free_port(port: int) -> bool:
    """Checks if the port is free on localhost.

    Args:
        port (int): The port which will be checked.

    Returns:
        bool: True if port is free, else False.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    is_success = sock.connect_ex(("localhost", port))
    return True if is_success else False


def get_pip_install_cmd() -> str:

    if Environment.use_dev_version:
        return (
            "pip install -q --upgrade git+"
            + settings.GITHUB_URL
            + "@"
            + settings.BRANCH
        )
    else:
        return "pip install -q --upgrade " + settings.PIP_PROJECT_NAME


def read_host_info(host: str) -> Dict[str, Union[str, List[str]]]:
    """Read information of a remote host.

    Args:
        host: The host from which the info will be read.
    """
    import json

    from fabric import Connection

    from lazycluster import RuntimeTask

    task = RuntimeTask("get-host-info")
    task.run_command(get_pip_install_cmd())
    task.run_function(print_localhost_info)
    task.execute(Connection(host))
    runtime_info = json.loads(task.execution_log[2])
    runtime_info["host"] = host
    return runtime_info


""" Private module level utils """


def _get_os_on_localhost() -> str:
    return platform.platform()


def _get_cpu_count_on_localhost() -> float:
    """Fail-safe method to get cpu count. Also respects docker/cgroup limitations."""
    try:
        import psutil

        cpu_count = psutil.cpu_count()
    except:  # noqa: E722
        # psutil is probably not installed
        cpu_count = os.cpu_count()

    try:
        import math

        # Try to read out docker cpu quota if it exists
        quota_file = "/sys/fs/cgroup/cpu/cpu.cfs_quota_us"
        if os.path.isfile(quota_file):
            cpu_quota = math.ceil(
                int(os.popen("cat " + quota_file).read().replace("\n", "")) / 100000
            )
            if 0 < cpu_quota < cpu_count:
                cpu_count = cpu_quota
    except:  # noqa: E722
        # Do nothing
        pass

    return cpu_count


def _get_memory_on_localhost() -> int:
    """Fail-safe method to get total memory. Also respects docker/cgroup limitations."""
    import psutil

    memory = psutil.virtual_memory().total
    try:
        if os.path.isfile("/sys/fs/cgroup/memory/memory.limit_in_bytes"):
            with open("/sys/fs/cgroup/memory/memory.limit_in_bytes", "r") as file:
                mem_limit = file.read().replace("\n", "").strip()
                if mem_limit and 0 < int(mem_limit) < int(memory):
                    # if mem limit from cgroup bigger than total memory -> use total memory
                    memory = int(mem_limit)
    except:  # noqa: E722
        # Do nothing
        pass

    return memory


def _get_python_version_on_localhost() -> str:
    return (
        str(sys.version_info.major)
        + "."
        + str(sys.version_info.minor)
        + "."
        + str(sys.version_info.micro)
    )


def _get_workspace_version_on_localhost() -> str:
    return os.environ["WORKSPACE_VERSION"]


def _get_gpu_info_for_localhost() -> list:
    NVIDIA_CMD = "nvidia-smi"

    if not command_exists_on_localhost(NVIDIA_CMD):
        return []

    gpus = []

    try:
        sp = subprocess.Popen(
            ["nvidia-smi", "-q"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out_str = sp.communicate()
        out_list = out_str[0].decode("utf-8").split("\n")

        count_gpu = 0
        for item in out_list:
            try:
                key, val = item.split(":")
                key, val = key.strip(), val.strip()
                if key == "Product Name":
                    count_gpu += 1
                    gpus.append(val)
            except:  # noqa: E722
                continue
    except:  # noqa: E722
        gpus = []

    return gpus
