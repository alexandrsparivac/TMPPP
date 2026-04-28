from src.models.task import Task
from src.models.user import User, UserRole


class InMemoryTaskStore:
    """Real object that simulates a MongoDB-backed task repository."""

    def __init__(self, tasks: dict[str, Task]):
        self.tasks = tasks
        self.load_count = 0
        self.update_count = 0

    def get_by_id(self, task_id: str) -> Task | None:
        self.load_count += 1
        return self.tasks.get(task_id)

    def update(self, task: Task) -> bool:
        if task.id is None:
            return False
        self.tasks[task.id] = task
        self.update_count += 1
        return True


class AuthorizedTaskRepositoryProxy:
    """Protection and virtual proxy for task access inside the bot."""

    def __init__(self, store: InMemoryTaskStore):
        self.store = store
        self._cache: dict[str, Task | None] = {}

    def get_task(self, task_id: str, user: User) -> Task | None:
        task = self._load_cached(task_id)
        if task is None:
            return None
        self._ensure_access(task, user)
        return task

    def update_task(self, task: Task, user: User) -> bool:
        self._ensure_access(task, user)
        self._cache[task.id or ""] = task
        return self.store.update(task)

    def _load_cached(self, task_id: str) -> Task | None:
        if task_id not in self._cache:
            self._cache[task_id] = self.store.get_by_id(task_id)
        return self._cache[task_id]

    def _ensure_access(self, task: Task, user: User) -> None:
        if user.role == UserRole.ADMIN:
            return
        if task.user_id != user.id:
            raise PermissionError(f"User {user.id} cannot access task {task.id}")
