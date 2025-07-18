from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class UserPlan(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class User(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    plan: UserPlan = UserPlan.FREE
    is_admin: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None
    profile: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    usage_stats: Optional[Dict[str, Any]] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    is_admin: bool
    created_at: datetime
    profile: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    plan: Optional[str] = "free"
    role: Optional[str] = "user"
    last_login: Optional[datetime] = None
    usage_stats: Optional[Dict[str, Any]] = None

class UserUpdateProfile(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None

class UserUpdatePreferences(BaseModel):
    theme: Optional[str] = "light"
    language: Optional[str] = "en"
    notifications: Optional[Dict[str, bool]] = None
    default_providers: Optional[Dict[str, str]] = None
    auto_save: Optional[bool] = True
    show_tutorials: Optional[bool] = True

class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str

class UserUpdateEmail(BaseModel):
    new_email: str
    password: str

class UserUsageStats(BaseModel):
    total_generations: int
    text_generations: int
    image_generations: int
    video_generations: int
    code_generations: int
    social_media_generations: int
    workflows_created: int
    workflows_executed: int
    api_calls_today: int
    api_calls_this_month: int
    tokens_used: int
    credits_used: int
    credits_remaining: int

class ActivityLog(BaseModel):
    activity_id: str
    user_id: str
    activity_type: str
    activity_description: str
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime

class UserAnalytics(BaseModel):
    user_id: str
    date: datetime
    daily_stats: Dict[str, Any]
    weekly_stats: Dict[str, Any]
    monthly_stats: Dict[str, Any]
    provider_usage: Dict[str, int]
    feature_usage: Dict[str, int]
    performance_metrics: Dict[str, float]