"""
MongoDB Models and Schemas for Student Life Helper Bot
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class UserPreferences(BaseModel):
    notifications: bool = True
    timezone: str = "Europe/Bucharest"
    language: str = "ro"
    theme: str = "light"

class GoogleTokens(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime
    token_type: str = "Bearer"

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    telegram_id: int
    name: str
    email: Optional[str] = None
    preferences: UserPreferences = UserPreferences()
    google_tokens: Optional[GoogleTokens] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class TaskMetadata(BaseModel):
    subject: Optional[str] = None
    estimated_duration: Optional[int] = None  # in minutes
    attachments: List[str] = []
    location: Optional[str] = None
    recurrence: Optional[Dict[str, Any]] = None
    priority_score: Optional[float] = None
    urgency_score: Optional[float] = None
    complexity_score: Optional[float] = None

class Task(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    title: str
    description: Optional[str] = None
    type: str  # assignment, meeting, reminder, project
    status: str = "todo"  # todo, in_progress, completed, cancelled
    priority: str = "medium"  # low, medium, high, urgent
    deadline: Optional[datetime] = None
    tags: List[str] = []
    metadata: TaskMetadata = TaskMetadata()
    dependencies: List[PyObjectId] = []
    subtasks: List[PyObjectId] = []
    calendar_event_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class Project(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    name: str
    description: Optional[str] = None
    status: str = "active"  # active, completed, on_hold, archived
    tasks: List[PyObjectId] = []
    milestones: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class GoogleSync(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    service: str  # calendar, gmail, drive
    external_id: str  # Google's ID
    local_id: PyObjectId  # Our document ID
    sync_status: str = "pending"  # pending, synced, error
    last_sync: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = {}
    error_message: Optional[str] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class Notification(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    type: str  # deadline, reminder, update, system
    title: str
    message: str
    status: str = "pending"  # pending, sent, failed, read
    priority: str = "medium"  # low, medium, high, urgent
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
