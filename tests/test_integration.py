import os
import re
import sys
import time
from subprocess import PIPE, run
from types import ModuleType
from typing import Union

import docker
import requests
import storm.__main__ as storm

from lazycluster import Runtime, RuntimeGroup, RuntimeManager, RuntimeTask

from .config import RUNTIME_DOCKER_IMAGE, RUNTIME_NAMES, WORKSPACE_PORT


def setup_module(module: ModuleType) -> None:
    """ setup any state specific to the execution of the given module."""
    docker_client = docker.from_env()

    for runtime_name in RUNTIME_NAMES:
        _start_runtime_container(runtime_name, docker_client)

    # Sleep a moment to give all processes time to start within the Workspace containers
    time.sleep(15)

    for runtime_name in RUNTIME_NAMES:
        _setup_ssh_connection_to_runtime(runtime_name)


def teardown_module(module: ModuleType) -> None:
    """teardown any state that was previously setup with a setup_module
    method.
    """
    _remove_runtimes()


class TestRuntime:
    def test_setup(self) -> None:
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

        if not RUNTIME_NAMES:
            raise RuntimeError("No runtime names in integration/config.py configured")

        Runtime(RUNTIME_NAMES[0])

    def test_echo(self) -> None:
        runtime_name = RUNTIME_NAMES[len(RUNTIME_NAMES) - 1]
        rt = Runtime(runtime_name)
        msg = f"Hello Runtime {runtime_name}"
        assert rt.echo(msg).rstrip("\n") == msg

    def test_working(self) -> None:
        runtime_name = RUNTIME_NAMES[0]
        exp_working_dir = "/etc"
        rt = Runtime(runtime_name, working_dir=exp_working_dir)
        act_working_dir = rt.echo("${PWD}").rstrip("\n")
        assert exp_working_dir == act_working_dir

        task = RuntimeTask("get-working-dir").run_command("echo ${PWD}")
        rt.execute_task(task, execute_async=False)
        assert exp_working_dir == rt.execution_log(task.name)[0].rstrip("\n").rstrip(
            "\r"
        )


class TestRuntimeGroup:
    def test_creation(self) -> None:
        runtime_group = RuntimeGroup(hosts=RUNTIME_NAMES)
        for runtime_name in RUNTIME_NAMES:
            assert runtime_name in runtime_group._runtimes
            assert isinstance(runtime_group._runtimes[runtime_name], Runtime)


class TestRuntimeManager:
    def test_create_group(self) -> None:
        runtime_group = RuntimeManager().create_group()
        for runtime_name in RUNTIME_NAMES:
            assert runtime_name in runtime_group._runtimes
            assert isinstance(runtime_group._runtimes[runtime_name], Runtime)


# -------------------------------------------------------------------------


def _remove_runtimes() -> None:
    docker_client = docker.from_env()
    for runtime_name in RUNTIME_NAMES:
        try:
            runtime_container = docker_client.containers.get(runtime_name)
            runtime_container.remove(force=True)
        except docker.errors.NotFound:
            # TODO: handle create a docker container if not running as containerized test
            print(f"Conatiner {runtime_name} not found")
        # Delete ssh config as well, because the ssh setup fails
        # when testing against multiple python versions
        storm.delete(runtime_name)


def _get_current_container_id() -> str:
    return run(
        "awk -F/ '{ print $NF }' /proc/1/cpuset",
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
        encoding="UTF-8",
    ).stdout.rstrip("\n")


def _start_runtime_container(name: str, client: docker.DockerClient) -> None:
    try:
        container = client.containers.run(
            RUNTIME_DOCKER_IMAGE,
            name=name,
            environment={"WORKSPACE_NAME": name},
            detach=True,
        )
    except docker.errors.APIError:
        _remove_runtimes()
        raise

    container.reload()
    ip_address = container.attrs["NetworkSettings"]["Networks"]["bridge"]["IPAddress"]
    os.environ[name] = ip_address
    _wait_until_started(ip_address, WORKSPACE_PORT)


def _setup_ssh_connection_to_runtime(runtime_name: str) -> None:

    runtime_host = os.getenv(runtime_name, "localhost")

    response = requests.get(
        f"http://{runtime_host}:{WORKSPACE_PORT}/tooling/ssh/setup-command?origin=http://{runtime_host}:{WORKSPACE_PORT}"
    )

    ssh_script_runner_regex = rf'^\/bin\/bash <\(curl -s --insecure "(http:\/\/{runtime_host}:{WORKSPACE_PORT}\/shared\/ssh\/setup\?token=[a-z0-9]+&host={runtime_host}&port={WORKSPACE_PORT})"\)$'
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

    completed_process = run(
        [f'/bin/bash -c "{setup_script_path}"'],
        input=runtime_name,
        encoding="ascii",
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
    )

    # child = pexpect.spawn(f"/bin/bash {setup_script_path}", encoding="UTF-8")
    # child.expect("Provide a name .*")
    # child.sendline(runtime_name)
    # child.expect("remote_ikernel was detected .*")
    # child.sendline("no")
    # child.expect("Do you want to add this connection as mountable SFTP storage .*")
    # child.sendline("no")
    # child.close()

    _remove_file_if_exists(setup_script_path)

    assert completed_process.stderr == ""
    assert "Connection successful!" in completed_process.stdout


def _wait_until_started(ip_address: str, workspace_port: Union[str, int]) -> None:
    index = 0
    health_url = f"http://{ip_address}:{str(workspace_port)}/healthy"
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


def _remove_file_if_exists(path: str) -> None:
    try:
        os.remove(path)
    except OSError:
        pass
