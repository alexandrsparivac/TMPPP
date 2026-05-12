from __future__ import annotations

from .config import AppConfig
from .conversations import ConversationManager
from .events import build_default_event_bus
from .facade import StudentLifeFacade
from .factories import StudentCommandFactory
from .router import BotRouter
from .storage import MongoStorage, StudentStorage


def build_router(storage: StudentStorage | None = None) -> BotRouter:
    if storage is None:
        config = AppConfig.load()
        storage = MongoStorage(
            mongo_uri=config.mongo_uri,
            database=config.mongo_database,
            collection=config.mongo_collection,
            default_strategy=config.default_task_strategy,
        )
    event_bus = build_default_event_bus(storage)
    facade = StudentLifeFacade(storage, event_bus)
    factory = StudentCommandFactory(facade)
    conversations = ConversationManager(facade)
    return BotRouter(factory, conversations, facade=facade)
