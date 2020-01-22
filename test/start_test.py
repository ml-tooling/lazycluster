import docker
import subprocess
import time
import sys

client = docker.from_env()

# pip install layclusterAT<commitid>
subprocess.call(["docker-compose","up" ,"-d"])#, shell=True)

manager_running = True
MANAGER_CONTAINER_NAME = "lazycluster-test-manager"

while manager_running:
  time.sleep(5)
  # TODO: change to correct name
  manager_container = client.containers.get(MANAGER_CONTAINER_NAME)
  if manager_container.status != "running":
      manager_running = False

manager_container = client.containers.get(MANAGER_CONTAINER_NAME)
exit_code = manager_container.attrs["State"]["ExitCode"]

print(exit_code)
# TODO: print test results
print(manager_container.logs())

subprocess.call("docker-compose down", shell=True)

sys.exit(exit_code)
