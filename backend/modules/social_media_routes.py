from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from models.social_media_models import (
    SocialMediaGenerationRequest, 
    HashtagGenerationRequest,
    SocialMediaTemplateRequest
)
from services.social_media_service import SocialMediaService
from utils.auth_utils import get_current_user

social_media_router = APIRouter(prefix="/api/social-media", tags=["Social Media"])

@social_media_router.post("/generate")
async def generate_social_media_content(
    request: SocialMediaGenerationRequest, 
    current_user: str = Depends(get_current_user)
):
    """Generate social media content"""
    try:
        result = await SocialMediaService.generate_social_media_content(request, current_user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_media_router.post("/generate/hashtags")
async def generate_hashtags(
    request: HashtagGenerationRequest,
    current_user: str = Depends(get_current_user)
):
    """Generate hashtags for a topic and platform"""
    try:
        result = await SocialMediaService.generate_hashtags(request, current_user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_media_router.get("/generations")
async def get_social_media_generations(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    current_user: str = Depends(get_current_user)
):
    """Get user's social media generations"""
    try:
        result = await SocialMediaService.get_user_social_media_generations(current_user, platform)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_media_router.get("/templates")
async def get_social_media_templates(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    content_type: Optional[str] = Query(None, description="Filter by content type")
):
    """Get social media content templates"""
    try:
        result = await SocialMediaService.get_social_media_templates(platform, content_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_media_router.get("/platforms")
async def get_platform_configs():
    """Get all platform configurations and supported features"""
    try:
        result = await SocialMediaService.get_platform_configs()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_media_router.get("/analytics")
async def get_social_media_analytics(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    current_user: str = Depends(get_current_user)
):
    """Get social media content analytics"""
    try:
        result = await SocialMediaService.get_social_media_analytics(current_user, platform)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_media_router.get("/generation/{generation_id}")
async def get_social_media_generation(
    generation_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get specific social media generation by ID"""
    try:
        from utils.database import social_media_generations_collection
        
        generation = social_media_generations_collection.find_one(
            {"generation_id": generation_id, "user_id": current_user},
            {"_id": 0}
        )
        
        if not generation:
            raise HTTPException(status_code=404, detail="Generation not found")
        
        return generation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_media_router.delete("/generation/{generation_id}")
async def delete_social_media_generation(
    generation_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete a social media generation"""
    try:
        from utils.database import social_media_generations_collection
        
        result = social_media_generations_collection.delete_one(
            {"generation_id": generation_id, "user_id": current_user}
        )
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Generation not found")
        
        return {"message": "Generation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_media_router.get("/content-types/{platform}")
async def get_content_types_for_platform(platform: str):
    """Get supported content types for a specific platform"""
    try:
        from services.social_media_service import SocialMediaService
        
        platform_config = SocialMediaService.PLATFORM_CONFIGS.get(platform)
        if not platform_config:
            raise HTTPException(status_code=404, detail="Platform not found")
        
        return {
            "platform": platform,
            "content_types": platform_config.content_types,
            "max_length": platform_config.max_length,
            "supports_hashtags": platform_config.supports_hashtags,
            "supports_emojis": platform_config.supports_emojis,
            "supports_mentions": platform_config.supports_mentions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_media_router.post("/optimize")
async def optimize_content_for_platform(
    content: str,
    platform: str,
    content_type: str,
    current_user: str = Depends(get_current_user)
):
    """Optimize existing content for a specific platform"""
    try:
        from services.social_media_service import SocialMediaService
        
        platform_config = SocialMediaService.PLATFORM_CONFIGS.get(platform)
        if not platform_config:
            raise HTTPException(status_code=404, detail="Platform not found")
        
        # Create optimization request
        optimization_request = SocialMediaGenerationRequest(
            provider_name="openai",  # Default provider
            model="gpt-4o-mini",
            platform=platform,
            content_type=content_type,
            prompt=f"Optimize this content for {platform}: {content}",
            tone="professional",
            include_hashtags=True,
            include_emojis=True,
            include_call_to_action=True
        )
        
        result = await SocialMediaService.generate_social_media_content(optimization_request, current_user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))