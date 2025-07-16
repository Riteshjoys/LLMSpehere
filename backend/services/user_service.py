import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from models.user_models import (
    UserUpdateProfile, UserUpdatePreferences, UserUpdatePassword, 
    UserUpdateEmail, UserUsageStats, ActivityLog, UserAnalytics
)
from utils.auth_utils import verify_password, get_password_hash
from utils.database import (
    users_collection, 
    generations_collection,
    image_generations_collection,
    video_generations_collection,
    code_generations_collection,
    social_media_generations_collection,
    workflows_collection,
    workflow_executions_collection,
    db
)

class UserService:
    @staticmethod
    async def update_user_profile(user_id: str, profile_data: UserUpdateProfile) -> Dict[str, Any]:
        """Update user profile information"""
        try:
            update_data = {
                "profile": profile_data.dict(exclude_none=True),
                "updated_at": datetime.utcnow()
            }
            
            result = users_collection.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return {"message": "Profile updated successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update profile: {str(e)}"
            )
    
    @staticmethod
    async def update_user_preferences(user_id: str, preferences_data: UserUpdatePreferences) -> Dict[str, Any]:
        """Update user preferences"""
        try:
            update_data = {
                "preferences": preferences_data.dict(exclude_none=True),
                "updated_at": datetime.utcnow()
            }
            
            result = users_collection.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return {"message": "Preferences updated successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update preferences: {str(e)}"
            )
    
    @staticmethod
    async def update_user_password(user_id: str, password_data: UserUpdatePassword) -> Dict[str, Any]:
        """Update user password"""
        try:
            user_doc = users_collection.find_one({"user_id": user_id})
            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            if not verify_password(password_data.current_password, user_doc["hashed_password"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
            
            new_hashed_password = get_password_hash(password_data.new_password)
            
            result = users_collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "hashed_password": new_hashed_password,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return {"message": "Password updated successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update password: {str(e)}"
            )
    
    @staticmethod
    async def update_user_email(user_id: str, email_data: UserUpdateEmail) -> Dict[str, Any]:
        """Update user email"""
        try:
            user_doc = users_collection.find_one({"user_id": user_id})
            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            if not verify_password(email_data.password, user_doc["hashed_password"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password is incorrect"
                )
            
            # Check if email already exists
            if users_collection.find_one({"email": email_data.new_email, "user_id": {"$ne": user_id}}):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            result = users_collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "email": email_data.new_email,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return {"message": "Email updated successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update email: {str(e)}"
            )
    
    @staticmethod
    async def get_user_usage_stats(user_id: str) -> UserUsageStats:
        """Get comprehensive usage statistics for a user"""
        try:
            # Get generation counts
            text_gens = generations_collection.count_documents({"user_id": user_id})
            image_gens = image_generations_collection.count_documents({"user_id": user_id})
            video_gens = video_generations_collection.count_documents({"user_id": user_id})
            code_gens = code_generations_collection.count_documents({"user_id": user_id})
            social_gens = social_media_generations_collection.count_documents({"user_id": user_id})
            
            # Get workflow stats
            workflows_created = workflows_collection.count_documents({"user_id": user_id})
            workflows_executed = workflow_executions_collection.count_documents({"user_id": user_id})
            
            # Get today's activity
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            api_calls_today = (
                generations_collection.count_documents({"user_id": user_id, "created_at": {"$gte": today}}) +
                image_generations_collection.count_documents({"user_id": user_id, "created_at": {"$gte": today}}) +
                video_generations_collection.count_documents({"user_id": user_id, "created_at": {"$gte": today}}) +
                code_generations_collection.count_documents({"user_id": user_id, "created_at": {"$gte": today}}) +
                social_media_generations_collection.count_documents({"user_id": user_id, "created_at": {"$gte": today}})
            )
            
            # Get this month's activity
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            api_calls_this_month = (
                generations_collection.count_documents({"user_id": user_id, "created_at": {"$gte": month_start}}) +
                image_generations_collection.count_documents({"user_id": user_id, "created_at": {"$gte": month_start}}) +
                video_generations_collection.count_documents({"user_id": user_id, "created_at": {"$gte": month_start}}) +
                code_generations_collection.count_documents({"user_id": user_id, "created_at": {"$gte": month_start}}) +
                social_media_generations_collection.count_documents({"user_id": user_id, "created_at": {"$gte": month_start}})
            )
            
            total_generations = text_gens + image_gens + video_gens + code_gens + social_gens
            
            # Calculate tokens and credits (mock values for now)
            tokens_used = total_generations * 100  # Estimate
            credits_used = total_generations * 10   # Estimate
            credits_remaining = 1000 - credits_used  # Default plan limit
            
            return UserUsageStats(
                total_generations=total_generations,
                text_generations=text_gens,
                image_generations=image_gens,
                video_generations=video_gens,
                code_generations=code_gens,
                social_media_generations=social_gens,
                workflows_created=workflows_created,
                workflows_executed=workflows_executed,
                api_calls_today=api_calls_today,
                api_calls_this_month=api_calls_this_month,
                tokens_used=tokens_used,
                credits_used=credits_used,
                credits_remaining=max(0, credits_remaining)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get usage stats: {str(e)}"
            )
    
    @staticmethod
    async def log_user_activity(user_id: str, activity_type: str, description: str, 
                               metadata: Optional[Dict[str, Any]] = None, 
                               ip_address: Optional[str] = None, 
                               user_agent: Optional[str] = None) -> None:
        """Log user activity"""
        try:
            activity = {
                "activity_id": str(uuid.uuid4()),
                "user_id": user_id,
                "activity_type": activity_type,
                "activity_description": description,
                "metadata": metadata or {},
                "ip_address": ip_address,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow()
            }
            
            db.activity_logs.insert_one(activity)
        except Exception as e:
            # Log error but don't fail the main operation
            print(f"Failed to log activity: {str(e)}")
    
    @staticmethod
    async def get_user_activity_logs(user_id: str, limit: int = 50, skip: int = 0) -> List[ActivityLog]:
        """Get user activity logs"""
        try:
            logs = list(db.activity_logs.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit).skip(skip))
            
            return [ActivityLog(**log) for log in logs]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get activity logs: {str(e)}"
            )
    
    @staticmethod
    async def get_user_analytics(user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user analytics for the specified number of days"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Aggregate data from all generation collections
            pipeline = [
                {"$match": {"user_id": user_id, "created_at": {"$gte": start_date, "$lte": end_date}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            # Get daily activity from all collections
            text_daily = list(generations_collection.aggregate(pipeline))
            image_daily = list(image_generations_collection.aggregate(pipeline))
            video_daily = list(video_generations_collection.aggregate(pipeline))
            code_daily = list(code_generations_collection.aggregate(pipeline))
            social_daily = list(social_media_generations_collection.aggregate(pipeline))
            
            # Combine all daily data
            daily_data = {}
            for data in [text_daily, image_daily, video_daily, code_daily, social_daily]:
                for item in data:
                    date = item["_id"]
                    if date not in daily_data:
                        daily_data[date] = 0
                    daily_data[date] += item["count"]
            
            # Get provider usage
            provider_pipeline = [
                {"$match": {"user_id": user_id, "created_at": {"$gte": start_date, "$lte": end_date}}},
                {"$group": {
                    "_id": "$provider_name",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
            
            provider_usage = {}
            for collection in [generations_collection, image_generations_collection, video_generations_collection]:
                for item in collection.aggregate(provider_pipeline):
                    provider = item["_id"] or "Unknown"
                    if provider not in provider_usage:
                        provider_usage[provider] = 0
                    provider_usage[provider] += item["count"]
            
            return {
                "daily_activity": daily_data,
                "provider_usage": provider_usage,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user analytics: {str(e)}"
            )
    
    @staticmethod
    async def update_last_login(user_id: str) -> None:
        """Update user's last login timestamp"""
        try:
            users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"last_login": datetime.utcnow()}}
            )
        except Exception as e:
            print(f"Failed to update last login: {str(e)}")