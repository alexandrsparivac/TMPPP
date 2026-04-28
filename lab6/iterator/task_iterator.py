from datetime import datetime
from typing import Callable, Iterator

from src.models.task import Task, TaskStatus


class TaskIterator(Iterator[Task]):
    def __init__(self, tasks: tuple[Task, ...]):
        self._tasks = tasks
        self._index = 0

    def __iter__(self) -> "TaskIterator":
        return self

    def __next__(self) -> Task:
        if self._index >= len(self._tasks):
            raise StopIteration
        task = self._tasks[self._index]
        self._index += 1
        return task


class TaskCollection:
    """Collection used by bot handlers without exposing internal storage."""

    def __init__(self):
        self._tasks: list[Task] = []

    def add(self, task: Task) -> None:
        self._tasks.append(task)

    def __iter__(self) -> TaskIterator:
        return TaskIterator(tuple(self._tasks))

    def matching(self, predicate: Callable[[Task], bool]) -> TaskIterator:
        return TaskIterator(tuple(task for task in self._tasks if predicate(task)))

    def upcoming(self, now: datetime) -> TaskIterator:
        return self.matching(
            lambda task: task.deadline is not None
            and task.deadline >= now
            and task.status != TaskStatus.COMPLETED
        )
