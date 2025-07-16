from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class SocialPlatform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"

class ContentType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"

class ViralityScore(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VIRAL = "viral"

class TrendAnalysisRequest(BaseModel):
    platforms: List[SocialPlatform] = Field(default=[SocialPlatform.TIKTOK, SocialPlatform.INSTAGRAM])
    categories: Optional[List[str]] = None
    region: str = "global"
    timeframe: str = "24h"  # 24h, 7d, 30d
    include_hashtags: bool = True
    include_sounds: bool = True
    include_effects: bool = True

class TrendItem(BaseModel):
    trend_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    platform: SocialPlatform
    category: str
    hashtags: List[str]
    engagement_rate: float
    growth_rate: float
    popularity_score: float
    viral_potential: ViralityScore
    duration_estimate: str
    related_sounds: Optional[List[str]] = None
    related_effects: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TrendAnalysisResponse(BaseModel):
    trends: List[TrendItem]
    total_trends: int
    analysis_date: datetime
    platforms_analyzed: List[SocialPlatform]
    region: str
    timeframe: str
    next_update: datetime

class ViralContentTemplate(BaseModel):
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    platform: SocialPlatform
    content_type: ContentType
    category: str
    structure: Dict[str, Any]
    suggested_hashtags: List[str]
    optimal_timing: Dict[str, Any]
    engagement_hooks: List[str]
    call_to_action: List[str]
    viral_elements: List[str]
    success_rate: float
    template_content: str
    placeholder_fields: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ViralContentRequest(BaseModel):
    topic: str
    platform: SocialPlatform
    content_type: ContentType
    target_audience: str = "general"
    tone: str = "engaging"
    template_id: Optional[str] = None
    include_hashtags: bool = True
    include_trending_elements: bool = True
    max_length: Optional[int] = None
    custom_requirements: Optional[Dict[str, Any]] = None

class EngagementPrediction(BaseModel):
    predicted_views: int
    predicted_likes: int
    predicted_comments: int
    predicted_shares: int
    virality_score: float
    engagement_rate: float
    reach_estimate: int
    confidence_level: float
    factors: List[str]
    recommendations: List[str]

class ViralContentResponse(BaseModel):
    content_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    platform: SocialPlatform
    content_type: ContentType
    hashtags: List[str]
    suggested_caption: str
    optimal_post_time: datetime
    engagement_prediction: EngagementPrediction
    viral_elements_used: List[str]
    trending_hooks: List[str]
    call_to_action: str
    platform_specific_tips: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: str
    topic: str
    template_used: Optional[str] = None

class CrossPlatformAdaptation(BaseModel):
    original_content: str
    original_platform: SocialPlatform
    adaptations: Dict[SocialPlatform, Dict[str, Any]]
    adaptation_notes: Dict[SocialPlatform, List[str]]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ViralContentGeneration(BaseModel):
    generation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    topic: str
    platform: SocialPlatform
    content_type: ContentType
    content: str
    hashtags: List[str]
    engagement_prediction: EngagementPrediction
    viral_score: float
    trend_alignment: float
    cross_platform_versions: Optional[CrossPlatformAdaptation] = None
    performance_tracking: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class HashtagAnalysis(BaseModel):
    hashtag: str
    platform: SocialPlatform
    usage_count: int
    engagement_rate: float
    growth_rate: float
    difficulty_score: float
    viral_potential: ViralityScore
    related_hashtags: List[str]
    optimal_usage_time: List[str]
    audience_demographics: Dict[str, Any]
    content_types: List[ContentType]

class ViralContentStats(BaseModel):
    total_generated: int
    by_platform: Dict[SocialPlatform, int]
    by_content_type: Dict[ContentType, int]
    average_viral_score: float
    top_performing_topics: List[str]
    success_rate: float
    trending_hashtags: List[str]
    recent_generations: List[ViralContentGeneration]