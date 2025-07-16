from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any, List, Optional
from models.user_models import (
    UserUpdateProfile, UserUpdatePreferences, UserUpdatePassword, 
    UserUpdateEmail, UserUsageStats, ActivityLog, UserResponse
)
from services.user_service import UserService
from services.auth_service import AuthService
from utils.auth_utils import get_current_user

router = APIRouter(prefix="/api/user", tags=["User Management"])

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: str = Depends(get_current_user)):
    """Get current user's complete profile"""
    return await AuthService.get_current_user_info(current_user)

@router.put("/profile")
async def update_user_profile(
    profile_data: UserUpdateProfile,
    current_user: str = Depends(get_current_user)
):
    """Update user profile information"""
    # Get user ID from username
    user_info = await AuthService.get_current_user_info(current_user)
    
    # Log activity
    await UserService.log_user_activity(
        user_info.user_id,
        "profile_update",
        "Updated profile information"
    )
    
    return await UserService.update_user_profile(user_info.user_id, profile_data)

@router.put("/preferences")
async def update_user_preferences(
    preferences_data: UserUpdatePreferences,
    current_user: str = Depends(get_current_user)
):
    """Update user preferences"""
    # Get user ID from username
    user_info = await AuthService.get_current_user_info(current_user)
    
    # Log activity
    await UserService.log_user_activity(
        user_info.user_id,
        "preferences_update",
        "Updated user preferences"
    )
    
    return await UserService.update_user_preferences(user_info.user_id, preferences_data)

@router.put("/password")
async def update_user_password(
    password_data: UserUpdatePassword,
    current_user: str = Depends(get_current_user)
):
    """Update user password"""
    # Get user ID from username
    user_info = await AuthService.get_current_user_info(current_user)
    
    # Log activity
    await UserService.log_user_activity(
        user_info.user_id,
        "password_update",
        "Updated password"
    )
    
    return await UserService.update_user_password(user_info.user_id, password_data)

@router.put("/email")
async def update_user_email(
    email_data: UserUpdateEmail,
    current_user: str = Depends(get_current_user)
):
    """Update user email"""
    # Get user ID from username
    user_info = await AuthService.get_current_user_info(current_user)
    
    # Log activity
    await UserService.log_user_activity(
        user_info.user_id,
        "email_update",
        f"Updated email to {email_data.new_email}"
    )
    
    return await UserService.update_user_email(user_info.user_id, email_data)

@router.get("/usage-stats", response_model=UserUsageStats)
async def get_user_usage_stats(current_user: str = Depends(get_current_user)):
    """Get comprehensive user usage statistics"""
    # Get user ID from username
    user_info = await AuthService.get_current_user_info(current_user)
    
    return await UserService.get_user_usage_stats(user_info.user_id)

@router.get("/activity-logs")
async def get_user_activity_logs(
    limit: int = 50,
    skip: int = 0,
    current_user: str = Depends(get_current_user)
):
    """Get user activity logs"""
    # Get user ID from username
    user_info = await AuthService.get_current_user_info(current_user)
    
    return await UserService.get_user_activity_logs(user_info.user_id, limit, skip)

@router.get("/analytics")
async def get_user_analytics(
    days: int = 30,
    current_user: str = Depends(get_current_user)
):
    """Get user analytics for the specified number of days"""
    # Get user ID from username
    user_info = await AuthService.get_current_user_info(current_user)
    
    return await UserService.get_user_analytics(user_info.user_id, days)

@router.post("/activity/log")
async def log_activity(
    activity_type: str,
    description: str,
    metadata: Optional[Dict[str, Any]] = None,
    request: Request = None,
    current_user: str = Depends(get_current_user)
):
    """Log user activity (for client-side tracking)"""
    # Get user ID from username
    user_info = await AuthService.get_current_user_info(current_user)
    
    # Extract IP and User-Agent from request
    ip_address = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None
    
    await UserService.log_user_activity(
        user_info.user_id,
        activity_type,
        description,
        metadata,
        ip_address,
        user_agent
    )
    
    return {"message": "Activity logged successfully"}

@router.delete("/account")
async def delete_user_account(
    password: str,
    current_user: str = Depends(get_current_user)
):
    """Delete user account (requires password confirmation)"""
    # Get user info
    user_info = await AuthService.get_current_user_info(current_user)
    
    # TODO: Implement account deletion logic
    # This is a placeholder - in production, you'd want to:
    # 1. Verify password
    # 2. Delete user data from all collections
    # 3. Handle data retention policies
    # 4. Send confirmation email
    
    return {"message": "Account deletion requested - feature coming soon"}