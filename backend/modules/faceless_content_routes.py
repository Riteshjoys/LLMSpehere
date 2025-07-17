from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from typing import List, Optional
import json

from models.faceless_content_models import (
    FacelessContentRequest,
    FacelessContentResponse,
    FacelessContent,
    TTSRequest,
    TTSResponse,
    ScreenRecordingRequest,
    ScreenRecordingResponse,
    AnimatedCharacter,
    BackgroundMusic,
    FacelessContentTemplate,
    FacelessContentStats,
    Voice,
    VoiceCloneRequest,
    VoiceCloneResponse
)
from services.faceless_content_service import FacelessContentService
from utils.auth_utils import get_current_user
from models.user_models import User

router = APIRouter(prefix="/api/faceless-content", tags=["faceless-content"])

# Initialize service
faceless_service = FacelessContentService()

@router.post("/generate", response_model=FacelessContentResponse)
async def generate_faceless_content(
    request: FacelessContentRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate faceless video content"""
    try:
        return await faceless_service.compose_faceless_video(request, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts/generate", response_model=TTSResponse)
async def generate_tts_audio(
    request: TTSRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate text-to-speech audio"""
    try:
        return await faceless_service.generate_tts_audio(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/screen-recording/simulate", response_model=ScreenRecordingResponse)
async def simulate_screen_recording(
    request: ScreenRecordingRequest,
    current_user: User = Depends(get_current_user)
):
    """Simulate screen recording (placeholder)"""
    try:
        return await faceless_service.simulate_screen_recording(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices", response_model=List[Voice])
async def get_available_voices(current_user: User = Depends(get_current_user)):
    """Get all available voices"""
    try:
        return await faceless_service.get_available_voices()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/characters", response_model=List[AnimatedCharacter])
async def get_animated_characters(current_user: User = Depends(get_current_user)):
    """Get all available animated characters"""
    try:
        return await faceless_service.get_animated_characters()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/background-music", response_model=List[BackgroundMusic])
async def get_background_music(current_user: User = Depends(get_current_user)):
    """Get all available background music"""
    try:
        return await faceless_service.get_background_music()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates", response_model=List[FacelessContentTemplate])
async def get_content_templates(current_user: User = Depends(get_current_user)):
    """Get all available content templates"""
    try:
        return await faceless_service.get_content_templates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[FacelessContent])
async def get_user_content(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get user's faceless content history"""
    try:
        return await faceless_service.get_user_content(current_user.user_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{content_id}", response_model=FacelessContent)
async def get_content_by_id(
    content_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific content by ID"""
    try:
        content = await faceless_service.get_content_by_id(content_id, current_user.user_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        return content
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete user's content"""
    try:
        success = await faceless_service.delete_content(content_id, current_user.user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Content not found")
        return {"message": "Content deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/overview", response_model=FacelessContentStats)
async def get_content_stats(current_user: User = Depends(get_current_user)):
    """Get user's content statistics"""
    try:
        return await faceless_service.get_content_stats(current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voices/clone", response_model=VoiceCloneResponse)
async def clone_voice(
    voice_name: str = Form(...),
    description: str = Form(None),
    labels: str = Form(None),
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Clone a voice from audio samples"""
    try:
        # Parse labels if provided
        labels_dict = json.loads(labels) if labels else None
        
        # Create voice clone request
        clone_request = VoiceCloneRequest(
            voice_name=voice_name,
            description=description,
            labels=labels_dict
        )
        
        # For now, return a placeholder response
        # In a real implementation, you would use the ElevenLabs voice cloning API
        return VoiceCloneResponse(
            voice_id=f"cloned_{voice_name.lower().replace(' ', '_')}",
            name=voice_name,
            status="processing",
            message="Voice cloning started. This may take a few minutes."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoints for real-time features
@router.websocket("/tts/stream")
async def tts_stream_websocket(websocket):
    """Real-time TTS streaming (placeholder)"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process TTS request
            await websocket.send_text(json.dumps({
                "type": "tts_chunk",
                "data": "audio_chunk_data",
                "timestamp": "2024-01-01T00:00:00Z"
            }))
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
    finally:
        await websocket.close()

@router.websocket("/recording/stream")
async def recording_stream_websocket(websocket):
    """Real-time recording stream (placeholder)"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process recording stream
            await websocket.send_text(json.dumps({
                "type": "recording_chunk",
                "data": "video_chunk_data",
                "timestamp": "2024-01-01T00:00:00Z"
            }))
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
    finally:
        await websocket.close()

# Additional utility endpoints
@router.get("/voices/{voice_id}/preview")
async def get_voice_preview(
    voice_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get voice preview URL"""
    try:
        voices = await faceless_service.get_available_voices()
        voice = next((v for v in voices if v.voice_id == voice_id), None)
        if not voice:
            raise HTTPException(status_code=404, detail="Voice not found")
        return {"preview_url": voice.preview_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/characters/{character_id}/animations")
async def get_character_animations(
    character_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get available animations for a character"""
    try:
        characters = await faceless_service.get_animated_characters()
        character = next((c for c in characters if c.character_id == character_id), None)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        return {"animations": character.animations}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}")
async def get_template_by_id(
    template_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific template by ID"""
    try:
        templates = await faceless_service.get_content_templates()
        template = next((t for t in templates if t.template_id == template_id), None)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates/{template_id}/generate", response_model=FacelessContentResponse)
async def generate_content_from_template(
    template_id: str,
    custom_text: str,
    current_user: User = Depends(get_current_user)
):
    """Generate content using a template"""
    try:
        # Get template
        templates = await faceless_service.get_content_templates()
        template = next((t for t in templates if t.template_id == template_id), None)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Create content request from template
        content_request = FacelessContentRequest(
            title=f"Content from {template.name}",
            description=template.description,
            tts_text=custom_text,
            voice_id=template.default_voice_id,
            video_duration=template.video_duration,
            video_format=template.video_format,
            video_quality=template.video_quality,
            video_resolution=template.video_resolution
        )
        
        # Add default character if specified
        if template.default_character:
            from models.faceless_content_models import AnimatedCharacterRequest
            content_request.animated_character = AnimatedCharacterRequest(
                character_id=template.default_character,
                animation="talking",
                duration=template.video_duration,
                position={"x": 0.8, "y": 0.7},
                scale=1.0,
                text=custom_text
            )
        
        # Add default background music if specified
        if template.default_music:
            from models.faceless_content_models import BackgroundMusicRequest
            content_request.background_music = BackgroundMusicRequest(
                track_id=template.default_music,
                volume=0.3,
                loop=True
            )
        
        return await faceless_service.compose_faceless_video(content_request, current_user.user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))