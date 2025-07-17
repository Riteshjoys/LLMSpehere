from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from uuid import uuid4

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    voice_id: str = Field(..., description="ElevenLabs voice ID")
    stability: float = Field(0.5, ge=0, le=1, description="Voice stability")
    similarity_boost: float = Field(0.5, ge=0, le=1, description="Voice similarity boost")
    model_id: str = Field("eleven_monolingual_v1", description="ElevenLabs model ID")
    format: str = Field("mp3", description="Audio format")

class TTSResponse(BaseModel):
    audio_url: str = Field(..., description="Generated audio file URL")
    duration: float = Field(..., description="Audio duration in seconds")
    voice_id: str = Field(..., description="Voice ID used")
    format: str = Field(..., description="Audio format")
    file_size: int = Field(..., description="File size in bytes")

class ScreenRecordingRequest(BaseModel):
    duration: int = Field(..., ge=1, le=300, description="Recording duration in seconds")
    fps: int = Field(30, ge=15, le=60, description="Frames per second")
    quality: str = Field("high", description="Recording quality")
    capture_audio: bool = Field(True, description="Whether to capture system audio")
    region: Optional[Dict[str, int]] = Field(None, description="Screen region to capture")

class ScreenRecordingResponse(BaseModel):
    video_url: str = Field(..., description="Generated video file URL")
    duration: float = Field(..., description="Video duration in seconds")
    fps: int = Field(..., description="Frames per second")
    resolution: str = Field(..., description="Video resolution")
    file_size: int = Field(..., description="File size in bytes")

class AnimatedCharacter(BaseModel):
    character_id: str = Field(..., description="Character identifier")
    name: str = Field(..., description="Character name")
    animation_type: str = Field(..., description="Animation type")
    position: Dict[str, float] = Field(..., description="Character position")
    scale: float = Field(1.0, description="Character scale")
    animations: List[str] = Field([], description="Available animations")

class AnimatedCharacterRequest(BaseModel):
    character_id: str = Field(..., description="Character to use")
    animation: str = Field(..., description="Animation to play")
    duration: float = Field(..., description="Animation duration")
    position: Dict[str, float] = Field(..., description="Character position")
    scale: float = Field(1.0, description="Character scale")
    text: Optional[str] = Field(None, description="Text for character to say")

class BackgroundMusic(BaseModel):
    track_id: str = Field(..., description="Track identifier")
    name: str = Field(..., description="Track name")
    genre: str = Field(..., description="Music genre")
    duration: float = Field(..., description="Track duration")
    tempo: str = Field(..., description="Track tempo")
    mood: str = Field(..., description="Track mood")
    file_url: str = Field(..., description="Audio file URL")

class BackgroundMusicRequest(BaseModel):
    track_id: str = Field(..., description="Background track to use")
    volume: float = Field(0.3, ge=0, le=1, description="Background music volume")
    fade_in: float = Field(0.0, description="Fade in duration")
    fade_out: float = Field(0.0, description="Fade out duration")
    loop: bool = Field(True, description="Whether to loop the music")

class FacelessContentRequest(BaseModel):
    title: str = Field(..., description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    
    # Text-to-Speech settings
    tts_text: str = Field(..., description="Text for narration")
    voice_id: str = Field(..., description="Voice ID for narration")
    
    # Screen recording settings
    screen_recording: Optional[ScreenRecordingRequest] = Field(None, description="Screen recording settings")
    
    # Animated character settings
    animated_character: Optional[AnimatedCharacterRequest] = Field(None, description="Animated character settings")
    
    # Background music settings
    background_music: Optional[BackgroundMusicRequest] = Field(None, description="Background music settings")
    
    # Video composition settings
    video_duration: Optional[float] = Field(None, description="Total video duration")
    video_format: str = Field("mp4", description="Output video format")
    video_quality: str = Field("high", description="Video quality")
    video_resolution: str = Field("1920x1080", description="Video resolution")

class FacelessContentResponse(BaseModel):
    content_id: str = Field(..., description="Generated content ID")
    title: str = Field(..., description="Content title")
    status: str = Field(..., description="Generation status")
    video_url: Optional[str] = Field(None, description="Generated video URL")
    audio_url: Optional[str] = Field(None, description="Generated audio URL")
    duration: Optional[float] = Field(None, description="Content duration")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class FacelessContent(BaseModel):
    content_id: str = Field(default_factory=lambda: str(uuid4()), description="Content ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    
    # Generation settings
    tts_settings: Dict[str, Any] = Field(..., description="TTS settings used")
    screen_recording_settings: Optional[Dict[str, Any]] = Field(None, description="Screen recording settings")
    character_settings: Optional[Dict[str, Any]] = Field(None, description="Character settings")
    music_settings: Optional[Dict[str, Any]] = Field(None, description="Music settings")
    video_settings: Dict[str, Any] = Field(..., description="Video settings")
    
    # Generated content
    audio_file: Optional[str] = Field(None, description="Generated audio file path")
    video_file: Optional[str] = Field(None, description="Generated video file path")
    thumbnail: Optional[str] = Field(None, description="Video thumbnail")
    
    # Metadata
    status: str = Field("pending", description="Content status")
    duration: Optional[float] = Field(None, description="Content duration")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    processing_time: Optional[float] = Field(None, description="Processing time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

class Voice(BaseModel):
    voice_id: str = Field(..., description="Voice ID")
    name: str = Field(..., description="Voice name")
    category: str = Field(..., description="Voice category")
    gender: str = Field(..., description="Voice gender")
    age: str = Field(..., description="Voice age")
    accent: str = Field(..., description="Voice accent")
    language: str = Field(..., description="Voice language")
    preview_url: Optional[str] = Field(None, description="Voice preview URL")
    
class VoiceCloneRequest(BaseModel):
    voice_name: str = Field(..., description="Name for the cloned voice")
    description: Optional[str] = Field(None, description="Voice description")
    labels: Optional[Dict[str, str]] = Field(None, description="Voice labels")

class VoiceCloneResponse(BaseModel):
    voice_id: str = Field(..., description="Generated voice ID")
    name: str = Field(..., description="Voice name")
    status: str = Field(..., description="Cloning status")
    message: str = Field(..., description="Status message")

class FacelessContentTemplate(BaseModel):
    template_id: str = Field(default_factory=lambda: str(uuid4()), description="Template ID")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Template category")
    
    # Template settings
    default_voice_id: str = Field(..., description="Default voice ID")
    default_character: Optional[str] = Field(None, description="Default character")
    default_music: Optional[str] = Field(None, description="Default background music")
    
    # Video settings
    video_duration: float = Field(..., description="Video duration")
    video_format: str = Field("mp4", description="Video format")
    video_quality: str = Field("high", description="Video quality")
    video_resolution: str = Field("1920x1080", description="Video resolution")
    
    # Content structure
    content_structure: List[Dict[str, Any]] = Field(..., description="Content structure")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    is_active: bool = Field(True, description="Whether template is active")

class FacelessContentStats(BaseModel):
    total_content: int = Field(..., description="Total content created")
    total_duration: float = Field(..., description="Total content duration")
    success_rate: float = Field(..., description="Success rate percentage")
    avg_processing_time: float = Field(..., description="Average processing time")
    popular_voices: List[Dict[str, Any]] = Field(..., description="Popular voices")
    popular_characters: List[Dict[str, Any]] = Field(..., description="Popular characters")
    content_by_category: Dict[str, int] = Field(..., description="Content by category")
    recent_content: List[Dict[str, Any]] = Field(..., description="Recent content")