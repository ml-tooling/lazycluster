import argparse
import os
import sys
from shutil import rmtree
from typing import Dict, Tuple, Union

import docker
import pytest
from universal_build import build_utils

TEST_DIRECTORY_PATH = "tests"
ABOUT_FILE_PATH = "src/lazycluster/about.py"


def main(args: Dict[str, Union[bool, str]]):

    version = args[build_utils.FLAG_VERSION]

    if args[build_utils.FLAG_VERSION]:
        assert isinstance(version, str)
        _update_library_version(version)

    if args[build_utils.FLAG_MAKE]:
        exit_code = _make()
        if exit_code != 0:
            build_utils.exit_process(exit_code)

    if args[build_utils.FLAG_CHECK]:
        exit_code = _check()
        if exit_code != 0:
            build_utils.exit_process(exit_code)

    if args[build_utils.FLAG_TEST]:
        exit_code = _test()
        if exit_code != 0:
            build_utils.exit_process(exit_code)

    if args[build_utils.FLAG_RELEASE]:
        assert isinstance(version, str)
        exit_code = _release(
            version, str(args["pypi_token"]), str(args["pypi_repository"])
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

    # When running locally wihtout container
    if not container_mount:
        return (os.getcwd(), "/workspace/github")

    # When running in act
    if container_mount.startswith("/"):
        return (container_mount, "/github/workspace")

    # When running in a container using a named volume which contains
    # the git repo (e.g. on Github Actions)
    else:
        return (container_mount, "/github")


def _make() -> int:
    # Todo: Generate documentation
    distribution_path_dir = "dist"
    # Ensure there are no old builds
    try:
        rmtree(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)), distribution_path_dir
            )
        )
    except OSError:
        pass

    # Build the distribution archives
    exit_code = build_utils.run(
        f"{sys.executable} setup.py sdist bdist_wheel clean --all"
    ).returncode
    if exit_code != 0:
        return exit_code

    # Check the archives with twine
    exit_code = build_utils.run(f"twine check {distribution_path_dir}/*").returncode
    return exit_code


def _check() -> int:
    # Todo: Implement
    return 0


def _release(
    version: str,
    pypi_token: str,
    pypi_repository: str = "testpypi",
) -> int:
    if not pypi_token:
        build_utils.log(
            "Release not possible - neither --pypi-token nor --pypi-test-token provied"
        )
        return 1
    pypi_token = "" if not pypi_token else f"-u __token__ -p {pypi_token}"
    upload_cmd = f"twine upload --repository {pypi_repository} dist/* {pypi_token}"

    exit_code = build_utils.run(upload_cmd).returncode
    return exit_code


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

    if __name__ == "__main__":
        # Check for valid arguments
        args = build_utils.get_sanitized_arguments()

        if args[build_utils.FLAG_RELEASE] and not args[build_utils.FLAG_FORCE]:
            # Run main without release to see whether everthing can be built and all tests run through
            main({**args, "release": False})
            # Run main again with only executing release with force flag
            main({**args, "make": False, "test": False, "check": False, "force": True})
        else:
            main(args)
