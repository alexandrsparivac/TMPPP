from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class _ConfigValues:
    bot_token: str | None
    mongo_uri: str
    mongo_database: str
    mongo_collection: str
    default_task_strategy: str


class AppConfig:
    """Singleton: one configuration object shared by the application."""

    _instance: "AppConfig | None" = None

    def __new__(cls, values: _ConfigValues) -> "AppConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._values = values
        return cls._instance

    @classmethod
    def load(cls) -> "AppConfig":
        if cls._instance is None:
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                pass
            values = _ConfigValues(
                bot_token=os.getenv("BOT_TOKEN"),
                mongo_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
                mongo_database=os.getenv("MONGODB_DATABASE", "student_life_helper"),
                mongo_collection=os.getenv("MONGODB_COLLECTION", "users"),
                default_task_strategy=os.getenv("TASK_STRATEGY", "deadline"),
            )
            cls(values)
        return cls._instance

    @property
    def bot_token(self) -> str | None:
        return self._values.bot_token

    @property
    def mongo_uri(self) -> str:
        return self._values.mongo_uri

    @property
    def mongo_database(self) -> str:
        return self._values.mongo_database

    @property
    def mongo_collection(self) -> str:
        return self._values.mongo_collection

    @property
    def default_task_strategy(self) -> str:
        return self._values.default_task_strategy
