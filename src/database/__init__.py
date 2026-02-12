"""
Database configuration and connections for Student Life Helper Bot
"""

from .config import (
    get_database,
    get_sync_database,
    connect_to_mongo,
    disconnect_from_mongo,
    init_indexes,
    USERS_COLLECTION,
    TASKS_COLLECTION,
    PROJECTS_COLLECTION,
    GOOGLE_SYNC_COLLECTION,
    NOTIFICATIONS_COLLECTION
)

__all__ = [
    "get_database",
    "get_sync_database", 
    "connect_to_mongo",
    "disconnect_from_mongo",
    "init_indexes",
    "USERS_COLLECTION",
    "TASKS_COLLECTION",
    "PROJECTS_COLLECTION",
    "GOOGLE_SYNC_COLLECTION",
    "NOTIFICATIONS_COLLECTION"
]
