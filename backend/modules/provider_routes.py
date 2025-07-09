from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from models.provider_models import LLMProvider, CurlProvider
from services.provider_service import ProviderService
from services.auth_service import AuthService
from utils.auth_utils import get_current_user

provider_router = APIRouter(prefix="/api", tags=["Providers"])

# Admin routes
@provider_router.post("/admin/providers")
async def add_provider(provider: LLMProvider, current_user: str = Depends(get_current_user)):
    """Add a new provider (Admin only)"""
    if not AuthService.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return await ProviderService.add_provider(provider, current_user)

@provider_router.post("/admin/providers/curl")
async def add_provider_from_curl(provider: CurlProvider, current_user: str = Depends(get_current_user)):
    """Add a provider from curl command (Admin only)"""
    if not AuthService.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return await ProviderService.add_provider_from_curl(provider, current_user)

@provider_router.get("/admin/providers")
async def get_all_providers(current_user: str = Depends(get_current_user)):
    """Get all providers (Admin only)"""
    if not AuthService.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    providers = await ProviderService.get_all_providers()
    return {"providers": providers}

@provider_router.put("/admin/providers/{provider_id}")
async def update_provider(provider_id: str, provider: LLMProvider, current_user: str = Depends(get_current_user)):
    """Update provider (Admin only)"""
    if not AuthService.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return await ProviderService.update_provider(provider_id, provider)

@provider_router.delete("/admin/providers/{provider_id}")
async def delete_provider(provider_id: str, current_user: str = Depends(get_current_user)):
    """Delete provider (Admin only)"""
    if not AuthService.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return await ProviderService.delete_provider(provider_id)

# Public routes
@provider_router.get("/providers")
async def get_active_providers(current_user: str = Depends(get_current_user)):
    """Get active providers"""
    providers = await ProviderService.get_active_providers()
    return {"providers": providers}

@provider_router.get("/providers/text")
async def get_text_providers(current_user: str = Depends(get_current_user)):
    """Get text providers"""
    providers = await ProviderService.get_providers_by_type("text")
    return {"providers": providers}

@provider_router.get("/providers/image")
async def get_image_providers(current_user: str = Depends(get_current_user)):
    """Get image providers"""
    providers = await ProviderService.get_providers_by_type("image")
    return {"providers": providers}

@provider_router.get("/providers/video")
async def get_video_providers(current_user: str = Depends(get_current_user)):
    """Get video providers"""
    providers = await ProviderService.get_providers_by_type("video")
    return {"providers": providers}