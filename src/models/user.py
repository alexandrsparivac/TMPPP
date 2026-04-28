from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class UserRole(Enum):
    STUDENT = "student"
    ADMIN = "admin"

class NotificationPreference(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"

@dataclass
class UserPreferences:
    notifications: NotificationPreference = NotificationPreference.ENABLED
    timezone: str = "Europe/Bucharest"
    language: str = "ro"
    theme: str = "light"
    reminder_advance_hours: int = 24
    daily_summary_enabled: bool = True
    weekend_notifications: bool = True

@dataclass
class User:
    id: Optional[str] = None
    telegram_id: int = 0
    username: str = ""
    full_name: str = ""
    email: str = ""
    role: UserRole = UserRole.STUDENT
    preferences: UserPreferences = field(default_factory=UserPreferences)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.telegram_id <= 0:
            raise ValueError("Telegram ID must be positive")
        if self.email and "@" not in self.email:
            raise ValueError("Invalid email format")

    def update_last_active(self) -> None:
        self.last_active = datetime.utcnow()

    def update_preferences(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self.preferences, key):
                setattr(self.preferences, key, value)
        self.last_active = datetime.utcnow()

    def enable_notifications(self) -> None:
        self.preferences.notifications = NotificationPreference.ENABLED
        self.last_active = datetime.utcnow()

    def disable_notifications(self) -> None:
        self.preferences.notifications = NotificationPreference.DISABLED
        self.last_active = datetime.utcnow()

    def notifications_enabled(self) -> bool:
        return self.preferences.notifications == NotificationPreference.ENABLED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role.value,
            "preferences": {
                "notifications": self.preferences.notifications.value,
                "timezone": self.preferences.timezone,
                "language": self.preferences.language,
                "theme": self.preferences.theme,
                "reminder_advance_hours": self.preferences.reminder_advance_hours,
                "daily_summary_enabled": self.preferences.daily_summary_enabled,
                "weekend_notifications": self.preferences.weekend_notifications
            },
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_active": self.last_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        preferences_data = data.get("preferences", {})
        preferences = UserPreferences(
            notifications=NotificationPreference(preferences_data.get("notifications", "enabled")),
            timezone=preferences_data.get("timezone", "Europe/Bucharest"),
            language=preferences_data.get("language", "ro"),
            theme=preferences_data.get("theme", "light"),
            reminder_advance_hours=preferences_data.get("reminder_advance_hours", 24),
            daily_summary_enabled=preferences_data.get("daily_summary_enabled", True),
            weekend_notifications=preferences_data.get("weekend_notifications", True)
        )

        return cls(
            id=data.get("id"),
            telegram_id=data.get("telegram_id", 0),
            username=data.get("username", ""),
            full_name=data.get("full_name", ""),
            email=data.get("email", ""),
            role=UserRole(data.get("role", "student")),
            preferences=preferences,
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", datetime.utcnow()),
            last_active=data.get("last_active", datetime.utcnow())
        )

    def __str__(self) -> str:
        name = self.full_name or self.username or f"User_{self.telegram_id}"
        return f"👤 {name} ({self.role.value})"

    def __repr__(self) -> str:
        return f"User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}', role={self.role.value})"
