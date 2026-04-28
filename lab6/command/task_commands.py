from abc import ABC, abstractmethod

from src.models.task import Task, TaskStatus


class InMemoryTaskBoard:
    def __init__(self):
        self.tasks: dict[str, Task] = {}

    def add(self, task: Task) -> None:
        if task.id is None:
            raise ValueError("Task id is required")
        self.tasks[task.id] = task

    def get(self, task_id: str) -> Task | None:
        return self.tasks.get(task_id)

    def delete(self, task_id: str) -> Task | None:
        return self.tasks.pop(task_id, None)


class BotCommand(ABC):
    @abstractmethod
    def execute(self) -> str:
        pass

    @abstractmethod
    def undo(self) -> str:
        pass


class AddTaskCommand(BotCommand):
    def __init__(self, board: InMemoryTaskBoard, task: Task):
        self.board = board
        self.task = task

    def execute(self) -> str:
        self.board.add(self.task)
        return f"added:{self.task.id}"

    def undo(self) -> str:
        self.board.delete(self.task.id or "")
        return f"removed:{self.task.id}"


class CompleteTaskCommand(BotCommand):
    def __init__(self, board: InMemoryTaskBoard, task_id: str):
        self.board = board
        self.task_id = task_id
        self._previous_status: TaskStatus | None = None

    def execute(self) -> str:
        task = self._get_task()
        self._previous_status = task.status
        task.update_status(TaskStatus.COMPLETED)
        return f"completed:{task.id}"

    def undo(self) -> str:
        task = self._get_task()
        if self._previous_status is not None:
            task.update_status(self._previous_status)
        return f"restored:{task.id}"

    def _get_task(self) -> Task:
        task = self.board.get(self.task_id)
        if task is None:
            raise ValueError(f"Task {self.task_id} was not found")
        return task


class DeleteTaskCommand(BotCommand):
    def __init__(self, board: InMemoryTaskBoard, task_id: str):
        self.board = board
        self.task_id = task_id
        self._deleted_task: Task | None = None

    def execute(self) -> str:
        self._deleted_task = self.board.delete(self.task_id)
        if self._deleted_task is None:
            raise ValueError(f"Task {self.task_id} was not found")
        return f"deleted:{self.task_id}"

    def undo(self) -> str:
        if self._deleted_task is None:
            return "nothing-to-restore"
        self.board.add(self._deleted_task)
        return f"restored:{self.task_id}"


class BotCommandInvoker:
    def __init__(self):
        self.history: list[BotCommand] = []

    def run(self, command: BotCommand) -> str:
        result = command.execute()
        self.history.append(command)
        return result

    def undo_last(self) -> str:
        if not self.history:
            return "nothing-to-undo"
        command = self.history.pop()
        return command.undo()
