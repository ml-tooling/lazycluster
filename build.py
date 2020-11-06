import argparse
import os
import sys
from shutil import rmtree
from typing import Dict, Optional, Tuple, Union

import docker
import pytest
from universal_build import build_utils

TEST_DIRECTORY_PATH = "tests"
DISTRIBUTION_DIRECTORY_PATH = "dist"
ABOUT_FILE_PATH = "src/lazycluster/about.py"

PYPI_USERNAME = "__token__"
BUILD_DIST_ARCHIVES_CMD = f"{sys.executable} setup.py sdist bdist_wheel clean --all"
UPLOAD_TO_TEST_PYPI_CMD = "twine upload --repository testpypi dist/*"
UPLOAD_TO_PYPI_CMD = "twine upload dist/*"

FLAG_PYPI_TEST_TOKEN = "pypi_test_token"
FLAG_PYPI_TOKEN = "pypi_token"


def main(args: Dict[str, Union[bool, str]]):

    version = args[build_utils.FLAG_VERSION]

    if args[build_utils.FLAG_VERSION]:
        assert isinstance(version, str)
        _update_library_version(version)

    if args[build_utils.FLAG_MAKE]:
        exit_code = _make()
        if exit_code != 0:
            build_utils.exit_process(exit_code)

    if args[build_utils.FLAG_TEST]:
        exit_code = _test()
        if exit_code != 0:
            build_utils.exit_process(exit_code)

    if args[build_utils.FLAG_RELEASE]:
        assert isinstance(version, str)
        exit_code = _release(
            version, str(args[FLAG_PYPI_TOKEN]), str(args[FLAG_PYPI_TEST_TOKEN])
        )
        if exit_code != 0:
            build_utils.exit_process(exit_code)


def _update_library_version(version: str):
    # Read lines of file
    f = open(ABOUT_FILE_PATH, "r")
    lines = f.readlines()
    f.close()

    # Update the version by overwriting the existing content
    f = open("__version__.py", "w+")
    for line in lines:
        line = line if "__version__" not in line else f"__version__ = {version}"
        f.write(line + "\n")
    f.close()


def _test() -> int:
    # Execute all unit tests
    unit_test_exit_code = int(
        pytest.main(["-x", os.path.join(TEST_DIRECTORY_PATH, "unit")])
    )
    return unit_test_exit_code if unit_test_exit_code != 0 else _integration_test()


def _integration_test() -> int:
    docker_client = docker.from_env()

    source_path, dest_path = _get_repo_mount_paths()

    container = docker_client.containers.run(
        "mltooling/ml-workspace-minimal:0.9.1",
        name="lazy-runtime-manager",
        volumes={
            source_path: {"bind": dest_path, "mode": "rw"},
            "/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"},
        },
        entrypoint=[
            "/bin/bash",
            os.path.join(
                "/github/workspace", TEST_DIRECTORY_PATH, "integration/entrypoint.sh"
            ),
        ],
        detach=True,
    )
    for output in container.logs(stream=True):
        build_utils.log(str(output))

    result = container.wait()
    container.remove()
    return result["StatusCode"]


def _get_repo_mount_paths() -> Tuple[str, str]:
    """Get the src (mount path or docker volume name) and the destination path
    dependent on the actual execution environment (e.g. Act, Github Actions, local).

    Returns:
        Tuple[str, str]: Source /  Destination
    """
    # Try to get the docker container id of the current host
    container_mount = os.getenv("INPUT_CONTAINER_MOUNT")
    return (
        (os.getcwd(), "/github/workspace")
        if not container_mount
        else (container_mount, "/github")
    )


def _make() -> int:
    # Todo: Generate documentation
    # Ensure there are no old builds
    try:
        rmtree(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)), DISTRIBUTION_DIRECTORY_PATH
            )
        )
    except OSError:
        pass

    # Build the distribution archives
    exit_code = build_utils.run(BUILD_DIST_ARCHIVES_CMD).returncode
    if exit_code != 0:
        return exit_code

    # Check the archives with twine
    exit_code = build_utils.run(
        f"twine check {DISTRIBUTION_DIRECTORY_PATH}/*"
    ).returncode
    return exit_code


def _release(
    version: str, pypi_token: Optional[str] = None, testpypi_token: Optional[str] = None
) -> int:
    if testpypi_token:
        # Publish on Test-PyPi
        upload_cmd = f"{UPLOAD_TO_TEST_PYPI_CMD} -u {PYPI_USERNAME} -p {testpypi_token}"
        exit_code = build_utils.run(upload_cmd).returncode
        if exit_code != 0:
            return exit_code

        # Check if installation from testpypi is succesful
        exit_code = build_utils.run(_get_test_pypi_install_cmd(version)).returncode
        if exit_code != 0:
            return exit_code

        if not pypi_token:
            return 0

    if pypi_token:
        # Finally publish on pypi
        exit_code = build_utils.run("twine upload dist/* ").returncode
        return exit_code

    build_utils.log(
        "Release not possible - neither --pypi-token nor --pypi-test-token provied"
    )
    return 1


def _get_test_pypi_install_cmd(version: str):
    return f"pip install  --index-url https://test.pypi.org/simple/ lazycluster={version} --force-reinstall"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pypi-token", help="Personal access token for PyPI account.", required=False
    )
    parser.add_argument(
        "--pypi-test-token",
        help="Personal access token for TestPyPI account.",
        required=False,
    )

    args = build_utils.get_sanitized_arguments(argument_parser=parser)

    if args[build_utils.FLAG_RELEASE]:
        # Run main without release to see whether everthing can be built and all tests run through
        arguments = dict(args)
        arguments[build_utils.FLAG_RELEASE] = False
        main(arguments)
        # Run main with release again without building and testing the components again
        arguments[build_utils.FLAG_RELEASE] = True
        arguments = {
            **arguments,
            build_utils.FLAG_MAKE: False,
            build_utils.FLAG_TEST: False,
            build_utils.FLAG_FORCE: True,
        }
        main(arguments)
    else:
        main(args)
