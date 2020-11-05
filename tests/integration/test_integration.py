import os
import re
import sys
import time
from subprocess import PIPE, run

import docker
import pexpect
import requests
from docker.client import DockerClient

from .config import (
    DOCKER_NETWORK_NAME,
    RUNTIME_DOCKER_IMAGE,
    RUNTIME_NAMES,
    WORKSPACE_PORT,
)


def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    docker_client = docker.from_env()

    try:
        docker_network = docker_client.networks.get(DOCKER_NETWORK_NAME)
        print(f"Docker network {docker_network.name} already exists")
    except docker.errors.NotFound:
        docker_network = docker_client.networks.create(
            DOCKER_NETWORK_NAME, driver="bridge"
        )
        print(f"Docker network {DOCKER_NETWORK_NAME} created")

    manager_container_id = _get_current_container_id()
    print(f"Manager Container ID: {manager_container_id}")

    docker_network.connect(manager_container_id)
    print(f"Container {manager_container_id} added to network {DOCKER_NETWORK_NAME}")

    for runtime_name in RUNTIME_NAMES:
        _start_runtime_container(runtime_name, docker_network.name, docker_client)

    # Sleep a moment to give all processes time to start within the Workspace containers
    time.sleep(15)

    for runtime_name in RUNTIME_NAMES:
        _setup_ssh_connection_to_runtime(runtime_name)


def teardown_module(module):
    """teardown any state that was previously setup with a setup_module
    method.
    """
    docker_client = docker.from_env()

    try:
        docker_network = docker_client.networks.get(DOCKER_NETWORK_NAME)
        print(f"Docker network {DOCKER_NETWORK_NAME} removed")
    except docker.errors.NotFound:
        print(f"Network {DOCKER_NETWORK_NAME} does NOT exist")
        return

    for runtime_name in RUNTIME_NAMES:
        try:
            runtime_container = docker_client.containers.get(runtime_name)
            docker_network.disconnect(runtime_container.name)
            runtime_container.remove(force=True)
        except docker.errors.NotFound:
            # TODO: handle create a docker container if not running as containerized test
            print(f"Conatiner {runtime_name} not found")

    manager_container_id = _get_current_container_id()
    docker_network.disconnect(manager_container_id)
    docker_network.remove()


def _get_current_container_id() -> str:
    return run(
        "awk -F/ '{ print $NF }' /proc/1/cpuset",
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
        encoding="UTF-8",
    ).stdout.rstrip("\n")


def _start_runtime_container(name: str, network_name: str, client: DockerClient):
    try:
        client.containers.run(
            RUNTIME_DOCKER_IMAGE,
            network=network_name,
            name=name,
            environment={"WORKSPACE_NAME": name},
            detach=True,
        )
    except docker.errors.APIError:
        pass

    _wait_until_started(name, WORKSPACE_PORT)


def _setup_ssh_connection_to_runtime(runtime_name: str):

    response = requests.get(
        f"http://{runtime_name}:{WORKSPACE_PORT}/tooling/ssh/setup-command?origin=http://{runtime_name}:{WORKSPACE_PORT}"
    )
    ssh_script_runner_regex = rf'^\/bin\/bash <\(curl -s --insecure "(http:\/\/{runtime_name}:{WORKSPACE_PORT}\/shared\/ssh\/setup\?token=[a-z0-9]+&host={runtime_name}&port={WORKSPACE_PORT})"\)$'
    pattern = re.compile(ssh_script_runner_regex)
    match = pattern.match(response.text)

    assert match, "SSH setup script url not found"

    # Execute the ssh setup script and automatically pass an ssh connection name to the script
    script_url = match.groups()[0]

    r = requests.get(script_url)

    setup_script_path = "./setup-ssh.sh"
    _remove_file_if_exists(setup_script_path)

    with open(setup_script_path, "w") as file:
        file.write(r.text)

    # make the file executable for the user
    os.chmod(setup_script_path, 0o744)

    child = pexpect.spawn(f"/bin/bash {setup_script_path}", encoding="UTF-8")
    child.expect("Provide a name .*")
    child.sendline(runtime_name)
    child.expect("remote_ikernel was detected .*")
    child.sendline("no")
    child.expect("Do you want to add this connection as mountable SFTP storage .*")
    child.sendline("no")
    child.close()
    _remove_file_if_exists(setup_script_path)


def _wait_until_started(workspace_name, workspace_port):
    index = 0
    health_url = f"http://{workspace_name}:{workspace_port}/healthy"
    response = None
    while response is None or (response.status_code != 200 and index < 15):
        index += 1
        time.sleep(1)
        try:
            response = requests.get(health_url, allow_redirects=False, timeout=2)
        except requests.ConnectionError:
            # Catch error that is raised when the workspace container is not reachable yet
            pass

    if index == 15:
        print("The workspace did not start")
        sys.exit(-1)


def _remove_file_if_exists(path: str):
    try:
        os.remove(path)
    except OSError:
        pass


class TestRuntime:
    def test_setup(self):
        for runtime_name in RUNTIME_NAMES:
            completed_process = run(
                f"ssh {runtime_name} 'echo $WORKSPACE_NAME'",
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
            )
            assert completed_process.stderr == b"", "The stderr is not emtpy"
            stdout = completed_process.stdout.decode("UTF-8").replace("\n", "")
            assert stdout == runtime_name, "Stdout is not equal to the runtime_name"
