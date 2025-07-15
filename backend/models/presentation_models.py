from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class PresentationFormat(str, Enum):
    POWERPOINT = "powerpoint"
    GOOGLE_SLIDES = "google_slides"
    PDF = "pdf"
    HTML = "html"

class SlideType(str, Enum):
    TITLE = "title"
    CONTENT = "content"
    IMAGE = "image"
    CHART = "chart"
    COMPARISON = "comparison"
    CONCLUSION = "conclusion"
    SECTION_HEADER = "section_header"

class ChartType(str, Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    COLUMN = "column"

class PresentationTheme(str, Enum):
    BUSINESS = "business"
    CREATIVE = "creative"
    MINIMAL = "minimal"
    MODERN = "modern"
    ACADEMIC = "academic"
    MARKETING = "marketing"

class SlideLayout(BaseModel):
    layout_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: SlideType
    template: str
    placeholders: List[Dict[str, Any]]
    thumbnail_url: Optional[str] = None

class SlideContent(BaseModel):
    slide_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: SlideType
    layout_id: str
    title: Optional[str] = None
    content: Optional[str] = None
    bullet_points: Optional[List[str]] = None
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    chart_data: Optional[Dict[str, Any]] = None
    chart_type: Optional[ChartType] = None
    speaker_notes: Optional[str] = None
    animation_settings: Optional[Dict[str, Any]] = None
    position: int = 0

class PresentationTemplate(BaseModel):
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    theme: PresentationTheme
    category: str
    slides: List[SlideContent]
    color_scheme: Dict[str, str]
    font_settings: Dict[str, Any]
    thumbnail_url: Optional[str] = None
    is_premium: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PresentationRequest(BaseModel):
    title: str
    topic: str
    num_slides: int = Field(default=10, ge=3, le=50)
    audience: str = "general"
    tone: str = "professional"
    format: PresentationFormat = PresentationFormat.POWERPOINT
    theme: PresentationTheme = PresentationTheme.BUSINESS
    template_id: Optional[str] = None
    include_charts: bool = True
    include_images: bool = True
    outline: Optional[List[str]] = None
    provider_name: Optional[str] = None
    model: Optional[str] = None

class PresentationResponse(BaseModel):
    presentation_id: str
    title: str
    topic: str
    slides: List[SlideContent]
    theme: PresentationTheme
    format: PresentationFormat
    total_slides: int
    file_url: Optional[str] = None
    file_base64: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime
    user_id: str
    provider: Optional[str] = None
    model: Optional[str] = None

class PresentationUpdate(BaseModel):
    title: Optional[str] = None
    slides: Optional[List[SlideContent]] = None
    theme: Optional[PresentationTheme] = None
    format: Optional[PresentationFormat] = None

class PresentationGeneration(BaseModel):
    generation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    presentation_id: str
    user_id: str
    title: str
    topic: str
    slides: List[SlideContent]
    theme: PresentationTheme
    format: PresentationFormat
    total_slides: int
    file_url: Optional[str] = None
    file_base64: Optional[str] = None
    thumbnail_url: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    generation_time: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SlideGenerationRequest(BaseModel):
    slide_type: SlideType
    title: str
    content_prompt: str
    layout_id: Optional[str] = None
    include_image: bool = False
    include_chart: bool = False
    chart_type: Optional[ChartType] = None
    provider_name: Optional[str] = None
    model: Optional[str] = None

class ChartData(BaseModel):
    chart_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    chart_type: ChartType
    data: Dict[str, Any]
    labels: List[str]
    datasets: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None
    color_scheme: Optional[List[str]] = None

class PresentationAnalytics(BaseModel):
    total_presentations: int
    presentations_this_month: int
    most_used_themes: List[Dict[str, Any]]
    most_used_formats: List[Dict[str, Any]]
    avg_slides_per_presentation: float
    total_slides_generated: int
    recent_presentations: List[Dict[str, Any]]
    user_id: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class PresentationExportRequest(BaseModel):
    presentation_id: str
    format: PresentationFormat
    include_speaker_notes: bool = True
    include_animations: bool = True
    quality: str = "high"  # high, medium, low