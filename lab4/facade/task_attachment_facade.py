from dataclasses import dataclass

from lab4.composite.task_attachment_tree import TaskAttachmentTree
from src.adapters.storage_adapter import IStorageAdapter
from src.models.task import Task


@dataclass(frozen=True)
class AttachmentUploadResult:
    task_id: str
    file_name: str
    saved_path: str
    file_size: int
    total_task_size: int


class InMemoryTaskRepository:
    """Small repository used to demonstrate the facade without MongoDB."""

    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.update_count = 0

    def add(self, task: Task) -> None:
        if task.id is None:
            raise ValueError("Task id is required")
        self.tasks[task.id] = task

    def get_by_id(self, task_id: str) -> Task | None:
        return self.tasks.get(task_id)

    def update(self, task: Task) -> None:
        if task.id is None:
            raise ValueError("Task id is required")
        self.tasks[task.id] = task
        self.update_count += 1


class MemoryStorageAdapter(IStorageAdapter):
    """Storage adapter for tests and local demos."""

    def __init__(self):
        self.files: dict[str, bytes] = {}

    def save_file(self, file_name: str, content: bytes) -> str:
        path = f"memory://task-attachments/{file_name}"
        self.files[path] = content
        return path

    def delete_file(self, file_path: str) -> bool:
        return self.files.pop(file_path, None) is not None


class TaskAttachmentUploadFacade:
    """Simple bot API for upload, storage and task attachment tree updates."""

    def __init__(
        self,
        task_repository: InMemoryTaskRepository,
        storage_adapter: IStorageAdapter,
    ):
        self.task_repository = task_repository
        self.storage_adapter = storage_adapter

    def upload(
        self,
        task_id: str,
        file_name: str,
        content: bytes,
        folder_path: str = "",
    ) -> AttachmentUploadResult:
        task = self.task_repository.get_by_id(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} was not found")

        saved_path = self.storage_adapter.save_file(file_name, content)
        attachment_tree = TaskAttachmentTree(task)
        file_item = attachment_tree.add_file(folder_path, file_name, content)
        self.task_repository.update(task)

        return AttachmentUploadResult(
            task_id=task_id,
            file_name=file_item.get_name(),
            saved_path=saved_path,
            file_size=file_item.get_size(),
            total_task_size=attachment_tree.total_size(),
        )
