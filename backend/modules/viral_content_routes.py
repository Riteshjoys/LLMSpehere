from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import json

from utils.auth_utils import get_current_user
from services.viral_content_service import ViralContentService
from models.viral_content_models import (
    TrendAnalysisRequest, TrendAnalysisResponse, ViralContentRequest, 
    ViralContentResponse, CrossPlatformAdaptation, HashtagAnalysis,
    ViralContentStats, SocialPlatform, ContentType, ViralContentTemplate
)

router = APIRouter(prefix="/api/viral", tags=["viral"])

# Initialize viral content service
viral_service = ViralContentService()

@router.post("/analyze-trends")
async def analyze_trends(
    request: TrendAnalysisRequest,
    current_user: str = Depends(get_current_user)
):
    """Analyze current social media trends"""
    try:
        result = await viral_service.analyze_trends(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_viral_content(
    request: ViralContentRequest,
    current_user: str = Depends(get_current_user)
):
    """Generate viral content based on trends and preferences"""
    try:
        result = await viral_service.generate_viral_content(request, current_user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adapt-cross-platform")
async def adapt_content_cross_platform(
    request: dict,
    current_user: str = Depends(get_current_user)
):
    """Adapt content for different social media platforms"""
    try:
        content = request.get("content")
        original_platform = SocialPlatform(request.get("original_platform"))
        target_platforms = [SocialPlatform(p) for p in request.get("target_platforms", [])]
        
        if not content or not original_platform or not target_platforms:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        result = await viral_service.adapt_content_cross_platform(
            content, original_platform, target_platforms
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-hashtags")
async def analyze_hashtags(
    request: dict,
    current_user: str = Depends(get_current_user)
):
    """Analyze hashtag performance and potential"""
    try:
        hashtags = request.get("hashtags", [])
        platform = SocialPlatform(request.get("platform"))
        
        if not hashtags or not platform:
            raise HTTPException(status_code=400, detail="Missing hashtags or platform")
        
        result = await viral_service.analyze_hashtags(hashtags, platform)
        return {"analyses": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_viral_templates(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    current_user: str = Depends(get_current_user)
):
    """Get available viral content templates"""
    try:
        platform_enum = SocialPlatform(platform) if platform else None
        content_type_enum = ContentType(content_type) if content_type else None
        
        templates = await viral_service.get_viral_templates(platform_enum, content_type_enum)
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content")
async def get_user_viral_content(
    limit: int = Query(50, description="Number of content items to return"),
    current_user: str = Depends(get_current_user)
):
    """Get user's viral content generation history"""
    try:
        content = await viral_service.get_user_viral_content(current_user, limit)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_viral_content_stats(
    current_user: str = Depends(get_current_user)
):
    """Get viral content statistics for user"""
    try:
        stats = await viral_service.get_viral_content_stats(current_user)
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms")
async def get_supported_platforms(
    current_user: str = Depends(get_current_user)
):
    """Get list of supported social media platforms"""
    try:
        platforms = [
            {
                "name": platform.value,
                "display_name": platform.value.replace("_", " ").title(),
                "max_length": viral_service.platform_configs[platform]["max_length"],
                "optimal_hashtags": viral_service.platform_configs[platform]["optimal_hashtags"],
                "best_times": viral_service.platform_configs[platform]["best_times"],
                "viral_elements": viral_service.platform_configs[platform]["viral_elements"]
            }
            for platform in SocialPlatform
        ]
        return {"platforms": platforms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content-types")
async def get_content_types(
    current_user: str = Depends(get_current_user)
):
    """Get list of supported content types"""
    try:
        content_types = [
            {
                "name": content_type.value,
                "display_name": content_type.value.replace("_", " ").title()
            }
            for content_type in ContentType
        ]
        return {"content_types": content_types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending-hashtags")
async def get_trending_hashtags(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    limit: int = Query(20, description="Number of hashtags to return"),
    current_user: str = Depends(get_current_user)
):
    """Get currently trending hashtags"""
    try:
        # For now, return platform-specific trending hashtags
        trending_hashtags = await viral_service._get_trending_hashtags()
        
        if platform:
            platform_enum = SocialPlatform(platform)
            # Add platform-specific hashtags
            platform_hashtags = {
                SocialPlatform.TIKTOK: ["#fyp", "#viral", "#trending", "#tiktok"],
                SocialPlatform.INSTAGRAM: ["#reels", "#explore", "#viral", "#instagram"],
                SocialPlatform.YOUTUBE: ["#shorts", "#viral", "#trending", "#youtube"],
                SocialPlatform.TWITTER: ["#trending", "#viral", "#news", "#twitter"]
            }
            trending_hashtags = platform_hashtags.get(platform_enum, trending_hashtags)
        
        return {"hashtags": trending_hashtags[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint for viral content service"""
    return {"status": "healthy", "service": "viral_content", "timestamp": datetime.utcnow()}