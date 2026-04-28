from src.models.attachment import AttachmentComponent, FileItem, FolderItem
from src.models.task import Task


class TaskAttachmentTree:
    """Composite tree used by the bot to organize files attached to a task."""

    def __init__(self, task: Task):
        self.task = task
        if self.task.attachments_root is None:
            self.task.attachments_root = FolderItem("root")

    def add_file(self, folder_path: str, file_name: str, content: bytes) -> FileItem:
        folder = self._resolve_folder(folder_path)
        file_item = FileItem(file_name, len(content))
        folder.add(file_item)
        return file_item

    def total_size(self) -> int:
        return self.task.attachments_root.get_size()

    def render(self) -> list[str]:
        return self._render_component(self.task.attachments_root)

    def _resolve_folder(self, folder_path: str) -> FolderItem:
        current = self.task.attachments_root
        for part in [part for part in folder_path.strip("/").split("/") if part]:
            child = current.get_child(part)
            if child is None:
                child = FolderItem(part)
                current.add(child)
            if not isinstance(child, FolderItem):
                raise ValueError(f"{part} exists and is not a folder")
            current = child
        return current

    def _render_component(
        self, component: AttachmentComponent, indent: int = 0
    ) -> list[str]:
        prefix = "  " * indent
        if isinstance(component, FolderItem):
            rows = [f"{prefix}+ {component.get_name()} ({component.get_size()} bytes)"]
            for child in component.children:
                rows.extend(self._render_component(child, indent + 1))
            return rows
        return [f"{prefix}- {component.get_name()} ({component.get_size()} bytes)"]
