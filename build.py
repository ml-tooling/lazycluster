import os
import sys
from shutil import rmtree
from typing import Dict, Union

import pytest
from universal_build import build_utils

DOCKER_NETWORK_NAME = "lazy-test-net"
TEST_DIRECTORY_PATH = "./tests"

PIP_INSTALL_LIB_CMD = "pip install --upgrade ."


def main(args: Dict[str, Union[bool, str]]):

    if args[build_utils.FLAG_TEST]:
        exit_code = _test()
        if exit_code != 0:
            build_utils.exit_process(exit_code)

    if args[build_utils.FLAG_MAKE]:
        exit_code = _make()
        if exit_code != 0:
            build_utils.exit_process(exit_code)

    if args[build_utils.FLAG_RELEASE]:
        exit_code = _release()
        if exit_code != 0:
            build_utils.exit_process(exit_code)


def _test() -> int:
    exit_code = build_utils.run(PIP_INSTALL_LIB_CMD).returncode
    return (
        exit_code if exit_code != 0 else int(pytest.main(["-x", TEST_DIRECTORY_PATH]))
    )


def _make() -> int:
    # Ensure there are no old builds
    try:
        rmtree(os.path.join(os.path.abspath(os.path.dirname(__file__)), "dist"))
    except OSError:
        pass
    pass
    return build_utils.run(
        f"{sys.executable} setup.py sdist bdist_wheel clean --all"
    ).returncode


def _release() -> int:
    pass


if __name__ == "__main__":
    args = build_utils.get_sanitized_arguments()

    if args[build_utils.FLAG_DOCKER]:
        # Set the containerized flag to False because the container
        # uses the same build.py as the entry point and would otherwise launch another builder container etc.
        args[build_utils.FLAG_DOCKER] = False
        container_build_name = "lazycluster-container-build"
        build_utils.run(f"docker build -t {container_build_name} ./build")
        build_utils.run("docker network create lab-core")
        build_utils.run(
            f"docker run \
            -v {os.getcwd()}:/resources:cached \
            -v /var/run/docker.sock:/var/run/docker.sock \
            --network {DOCKER_NETWORK_NAME} \
            {container_build_name}"
            + build_utils.concat_command_line_arguments(args)
        )
    else:
        if args[build_utils.FLAG_RELEASE]:
            # Run main without release to see whether everthing can be built and all tests run through
            arguments = dict(args)
            arguments[build_utils.FLAG_RELEASE] = False
            main(arguments)
            # Run main again without building and testing the components again
            arguments = {**arguments, "make": False, "test": False, "force": True}
            main(arguments)
        else:
            main(args)
