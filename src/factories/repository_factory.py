from abc import ABC, abstractmethod

from ..models.repositories import ITaskRepository, IUserRepository
from ..repositories.mongodb_task_repository import MongoTaskRepository
from ..repositories.mongodb_user_repository import MongoUserRepository

class IRepositoryFactory(ABC):
    """
    Abstract Factory interface for creating related repository objects.
    """
    @abstractmethod
    def create_task_repository(self) -> ITaskRepository:
        pass

    @abstractmethod
    def create_user_repository(self) -> IUserRepository:
        pass


class MongoRepositoryFactory(IRepositoryFactory):
    """
    Concrete Factory for MongoDB repositories.
    """
    def __init__(self, database):
        self._database = database

    def create_task_repository(self) -> ITaskRepository:
        return MongoTaskRepository(self._database)

    def create_user_repository(self) -> IUserRepository:
        return MongoUserRepository(self._database)
