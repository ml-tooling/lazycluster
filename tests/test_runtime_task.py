import pytest

from lazycluster import RuntimeTask

TASK_NAME = "test-task"


class TestRuntimeTask:
    def test_task_creation(self):
        task = RuntimeTask(TASK_NAME)
        assert task.name == TASK_NAME
        assert task._execution_log_file_path is None
        assert task._task_steps == []
        assert task._execution_log == []
        assert len(task._task_steps) == 0

    def test_task_creation_wo_name(self):
        task = RuntimeTask()
        assert isinstance(task.name, str)
        assert task.name != ""

    def test_run_command(self):
        COMMAND = "echo 'Test Execution'"
        task = RuntimeTask("run-command-task")
        task.run_command(COMMAND)
        assert len(task._task_steps) == 1
        assert task._task_steps[0].type == RuntimeTask._TaskStep.TYPE_RUN_COMMAND

    def test_bad_call_send_file(self):
        COMMAND = ""
        task = RuntimeTask("bad-call-run-command-task")
        with pytest.raises(ValueError):
            task.run_command(COMMAND)

        COMMAND = "echo 'Hello World'"
        task = RuntimeTask("run-command-task")
        task.run_command(COMMAND)
        assert len(task._task_steps) == 1
        assert task._task_steps[0].type == RuntimeTask._TaskStep.TYPE_RUN_COMMAND

    def test_send_file(self):
        task = RuntimeTask("send-file-task")
        task.send_file("./test.txt")
        assert len(task._task_steps) == 1
        assert task._task_steps[0].type == RuntimeTask._TaskStep.TYPE_SEND_FILE

    def test_get_file(self):
        task = RuntimeTask("send-file-task")
        task.get_file("./test.txt")
        assert len(task._task_steps) == 1
        assert task._task_steps[0].type == RuntimeTask._TaskStep.TYPE_GET_FILE
