from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

class LLMProvider(BaseModel):
    name: str
    description: str
    base_url: str
    headers: Dict[str, str]
    request_body_template: Dict[str, Any]
    response_parser: Dict[str, str]  # JSONPath expressions to extract response
    models: List[str]
    provider_type: str = "text"  # "text", "image", or "video"
    is_active: bool = True

class CurlProvider(BaseModel):
    name: str
    description: str
    curl_command: str
    models: List[str]
    provider_type: str = "text"  # "text", "image", or "video"
    is_active: bool = True

class ProviderResponse(BaseModel):
    provider_id: str
    name: str
    description: str
    models: List[str]
    provider_type: str
    is_active: bool
    created_at: datetime
    created_by: str