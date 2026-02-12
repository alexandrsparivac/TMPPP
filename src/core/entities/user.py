"""
User Entity - Core business entity following SOLID principles
"""
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class UserRole(Enum):
    """User role enumeration"""
    STUDENT = "student"
    ADMIN = "admin"

class NotificationPreference(Enum):
    """Notification preference enumeration"""
    ENABLED = "enabled"
    DISABLED = "disabled"

@dataclass
class UserPreferences:
    """User preferences following Single Responsibility Principle"""
    notifications: NotificationPreference = NotificationPreference.ENABLED
    timezone: str = "Europe/Bucharest"
    language: str = "ro"
    theme: str = "light"
    reminder_advance_hours: int = 24
    daily_summary_enabled: bool = True
    weekend_notifications: bool = True

@dataclass
class GoogleTokens:
    """Google tokens for API integration"""
    access_token: str = ""
    refresh_token: str = ""
    expires_at: Optional[datetime] = None
    token_type: str = "Bearer"

@dataclass
class User:
    """
    Core User Entity following SOLID principles:
    - Single Responsibility: Represents only user data and basic behavior
    - Open/Closed: Open for extension through inheritance
    - Liskov Substitution: Subusers can replace base users
    - Interface Segregation: Focused on user-specific methods
    - Dependency Inversion: Depends on abstractions
    """
    id: Optional[str] = None
    telegram_id: int = 0
    username: str = ""
    full_name: str = ""
    email: str = ""
    role: UserRole = UserRole.STUDENT
    preferences: UserPreferences = field(default_factory=UserPreferences)
    google_tokens: Optional[GoogleTokens] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Post-initialization validation"""
        if self.telegram_id <= 0:
            raise ValueError("Telegram ID must be positive")
        
        if self.email and "@" not in self.email:
            raise ValueError("Invalid email format")
    
    def update_last_active(self) -> None:
        """Update last active timestamp"""
        self.last_active = datetime.utcnow()
    
    def update_preferences(self, **kwargs) -> None:
        """Update user preferences"""
        for key, value in kwargs.items():
            if hasattr(self.preferences, key):
                setattr(self.preferences, key, value)
        self.last_active = datetime.utcnow()
    
    def set_google_tokens(self, access_token: str, refresh_token: str, expires_at: datetime) -> None:
        """Set Google API tokens"""
        self.google_tokens = GoogleTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        self.last_active = datetime.utcnow()
    
    def clear_google_tokens(self) -> None:
        """Clear Google tokens"""
        self.google_tokens = None
        self.last_active = datetime.utcnow()
    
    def has_google_integration(self) -> bool:
        """Check if user has Google integration"""
        return self.google_tokens is not None and bool(self.google_tokens.access_token)
    
    def is_google_token_expired(self) -> bool:
        """Check if Google token is expired"""
        if not self.google_tokens or not self.google_tokens.expires_at:
            return True
        return datetime.utcnow() >= self.google_tokens.expires_at
    
    def enable_notifications(self) -> None:
        """Enable notifications"""
        self.preferences.notifications = NotificationPreference.ENABLED
        self.last_active = datetime.utcnow()
    
    def disable_notifications(self) -> None:
        """Disable notifications"""
        self.preferences.notifications = NotificationPreference.DISABLED
        self.last_active = datetime.utcnow()
    
    def notifications_enabled(self) -> bool:
        """Check if notifications are enabled"""
        return self.preferences.notifications == NotificationPreference.ENABLED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for database storage"""
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
            "google_tokens": {
                "access_token": self.google_tokens.access_token,
                "refresh_token": self.google_tokens.refresh_token,
                "expires_at": self.google_tokens.expires_at,
                "token_type": self.google_tokens.token_type
            } if self.google_tokens else None,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_active": self.last_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create user from dictionary"""
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
        
        google_tokens_data = data.get("google_tokens")
        google_tokens = None
        if google_tokens_data:
            google_tokens = GoogleTokens(
                access_token=google_tokens_data.get("access_token", ""),
                refresh_token=google_tokens_data.get("refresh_token", ""),
                expires_at=google_tokens_data.get("expires_at"),
                token_type=google_tokens_data.get("token_type", "Bearer")
            )
        
        return cls(
            id=data.get("id"),
            telegram_id=data.get("telegram_id", 0),
            username=data.get("username", ""),
            full_name=data.get("full_name", ""),
            email=data.get("email", ""),
            role=UserRole(data.get("role", "student")),
            preferences=preferences,
            google_tokens=google_tokens,
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", datetime.utcnow()),
            last_active=data.get("last_active", datetime.utcnow())
        )
    
    def __str__(self) -> str:
        """String representation of user"""
        name = self.full_name or self.username or f"User_{self.telegram_id}"
        return f"👤 {name} ({self.role.value})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return f"User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}', role={self.role.value})"
