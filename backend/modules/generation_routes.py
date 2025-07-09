from fastapi import APIRouter, Depends
from models.generation_models import TextGenerationRequest, ImageGenerationRequest, VideoGenerationRequest
from services.text_generation_service import TextGenerationService
from services.image_generation_service import ImageGenerationService
from services.video_generation_service import VideoGenerationService
from utils.auth_utils import get_current_user

generation_router = APIRouter(prefix="/api", tags=["Generation"])

# Text Generation
@generation_router.post("/generate/text")
async def generate_text(request: TextGenerationRequest, current_user: str = Depends(get_current_user)):
    """Generate text using various providers"""
    return await TextGenerationService.generate_text(request, current_user)

@generation_router.get("/conversations/{session_id}")
async def get_conversation(session_id: str, current_user: str = Depends(get_current_user)):
    """Get conversation by session ID"""
    return await TextGenerationService.get_conversation(session_id, current_user)

@generation_router.get("/conversations")
async def get_user_conversations(current_user: str = Depends(get_current_user)):
    """Get all user conversations"""
    return await TextGenerationService.get_user_conversations(current_user)

@generation_router.get("/generations")
async def get_user_generations(current_user: str = Depends(get_current_user)):
    """Get user text generations"""
    return await TextGenerationService.get_user_generations(current_user)

# Image Generation
@generation_router.post("/generate/image")
async def generate_image(request: ImageGenerationRequest, current_user: str = Depends(get_current_user)):
    """Generate image using various providers"""
    return await ImageGenerationService.generate_image(request, current_user)

@generation_router.get("/generations/images")
async def get_user_image_generations(current_user: str = Depends(get_current_user)):
    """Get user image generations"""
    return await ImageGenerationService.get_user_image_generations(current_user)

# Video Generation
@generation_router.post("/generate/video")
async def generate_video(request: VideoGenerationRequest, current_user: str = Depends(get_current_user)):
    """Generate video using various providers"""
    return await VideoGenerationService.generate_video(request, current_user)

@generation_router.get("/generations/videos")
async def get_user_video_generations(current_user: str = Depends(get_current_user)):
    """Get user video generations"""
    return await VideoGenerationService.get_user_video_generations(current_user)