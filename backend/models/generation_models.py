from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TextGenerationRequest(BaseModel):
    provider_name: str
    model: str
    prompt: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    session_id: Optional[str] = None

class ImageGenerationRequest(BaseModel):
    provider_name: str
    model: str
    prompt: str
    number_of_images: Optional[int] = 1
    session_id: Optional[str] = None

class VideoGenerationRequest(BaseModel):
    provider_name: str
    model: str
    prompt: str
    duration: Optional[int] = 5  # seconds
    aspect_ratio: Optional[str] = "16:9"
    resolution: Optional[str] = "720p"
    session_id: Optional[str] = None

class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime

class GenerationResponse(BaseModel):
    generation_id: str
    session_id: str
    provider: str
    model: str
    prompt: str
    content: str
    created_at: datetime