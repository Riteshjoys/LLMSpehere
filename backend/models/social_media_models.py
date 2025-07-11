from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class SocialMediaGenerationRequest(BaseModel):
    provider_name: str
    model: str
    platform: str  # twitter, instagram, linkedin, facebook, tiktok, youtube
    content_type: str  # post, caption, story, thread, bio, hashtags
    prompt: str
    tone: Optional[str] = "professional"  # professional, casual, friendly, formal, humorous
    target_audience: Optional[str] = "general"
    include_hashtags: Optional[bool] = True
    hashtag_count: Optional[int] = 5
    max_length: Optional[int] = None  # Auto-determined by platform if not specified
    include_emojis: Optional[bool] = True
    include_call_to_action: Optional[bool] = True
    session_id: Optional[str] = None

class SocialMediaGenerationResponse(BaseModel):
    id: str
    session_id: str
    provider: str
    model: str
    platform: str
    content_type: str
    prompt: str
    content: str
    hashtags: List[str]
    user_id: str
    created_at: datetime
    status: str = "completed"
    metadata: Dict[str, Any] = {}

class SocialMediaTemplateRequest(BaseModel):
    platform: str
    content_type: str
    industry: Optional[str] = None
    tone: Optional[str] = "professional"

class PlatformConfig(BaseModel):
    platform: str
    max_length: int
    supports_hashtags: bool
    supports_emojis: bool
    supports_mentions: bool
    content_types: List[str]

class HashtagGenerationRequest(BaseModel):
    topic: str
    platform: str
    count: Optional[int] = 10
    trending: Optional[bool] = False
    niche: Optional[str] = None

class SocialMediaScheduleRequest(BaseModel):
    content_id: str
    platform: str
    scheduled_time: datetime
    recurring: Optional[bool] = False
    frequency: Optional[str] = None  # daily, weekly, monthly

class SocialMediaAnalyticsRequest(BaseModel):
    platform: str
    date_range: Optional[str] = "30d"  # 7d, 30d, 90d
    content_type: Optional[str] = None