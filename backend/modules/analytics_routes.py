from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from utils.auth_utils import get_current_user
from services.auth_service import AuthService
from utils.database import (
    providers_collection,
    generations_collection,
    image_generations_collection,
    video_generations_collection,
    code_generations_collection,
    social_media_generations_collection,
    workflows_collection,
    workflow_executions_collection,
    users_collection,
    db
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/dashboard/enhanced")
async def get_enhanced_dashboard_analytics(
    days: int = Query(default=30, description="Number of days to analyze"),
    current_user: str = Depends(get_current_user)
):
    """Get enhanced dashboard analytics with charts and detailed metrics"""
    try:
        # Get user info
        user_info = await AuthService.get_current_user_info(current_user)
        user_id = user_info.user_id
        
        # Date range setup
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Basic stats
        total_text = generations_collection.count_documents({"user_id": user_id})
        total_image = image_generations_collection.count_documents({"user_id": user_id})
        total_video = video_generations_collection.count_documents({"user_id": user_id})
        total_code = code_generations_collection.count_documents({"user_id": user_id})
        total_social = social_media_generations_collection.count_documents({"user_id": user_id})
        
        total_generations = total_text + total_image + total_video + total_code + total_social
        
        # Daily activity data for charts
        daily_pipeline = [
            {"$match": {"user_id": user_id, "created_at": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        # Get daily data from all collections
        text_daily = list(generations_collection.aggregate(daily_pipeline))
        image_daily = list(image_generations_collection.aggregate(daily_pipeline))
        video_daily = list(video_generations_collection.aggregate(daily_pipeline))
        code_daily = list(code_generations_collection.aggregate(daily_pipeline))
        social_daily = list(social_media_generations_collection.aggregate(daily_pipeline))
        
        # Combine daily data
        daily_activity = {}
        all_dates = set()
        
        for data_list in [text_daily, image_daily, video_daily, code_daily, social_daily]:
            for item in data_list:
                date = item["_id"]
                all_dates.add(date)
                if date not in daily_activity:
                    daily_activity[date] = {"total": 0, "text": 0, "image": 0, "video": 0, "code": 0, "social": 0}
                
                # Determine the type based on which collection this came from
                if data_list == text_daily:
                    daily_activity[date]["text"] += item["count"]
                elif data_list == image_daily:
                    daily_activity[date]["image"] += item["count"]
                elif data_list == video_daily:
                    daily_activity[date]["video"] += item["count"]
                elif data_list == code_daily:
                    daily_activity[date]["code"] += item["count"]
                elif data_list == social_daily:
                    daily_activity[date]["social"] += item["count"]
                
                daily_activity[date]["total"] += item["count"]
        
        # Fill in missing dates with zero values
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            if date_str not in daily_activity:
                daily_activity[date_str] = {"total": 0, "text": 0, "image": 0, "video": 0, "code": 0, "social": 0}
            current_date += timedelta(days=1)
        
        # Provider usage analytics
        provider_pipeline = [
            {"$match": {"user_id": user_id, "created_at": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {
                "_id": "$provider_name",
                "count": {"$sum": 1},
                "avg_response_time": {"$avg": "$response_time"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        provider_usage = {}
        for collection in [generations_collection, image_generations_collection, video_generations_collection]:
            for item in collection.aggregate(provider_pipeline):
                provider = item["_id"] or "Unknown"
                if provider not in provider_usage:
                    provider_usage[provider] = {"count": 0, "avg_response_time": 0}
                provider_usage[provider]["count"] += item["count"]
                provider_usage[provider]["avg_response_time"] = item.get("avg_response_time", 0)
        
        # Performance metrics
        avg_response_times = []
        for collection in [generations_collection, image_generations_collection, video_generations_collection]:
            pipeline = [
                {"$match": {"user_id": user_id, "created_at": {"$gte": start_date, "$lte": end_date}}},
                {"$group": {"_id": None, "avg_time": {"$avg": "$response_time"}}}
            ]
            result = list(collection.aggregate(pipeline))
            if result:
                avg_response_times.append(result[0]["avg_time"])
        
        avg_response_time = sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0
        
        # Success rate calculation
        success_count = 0
        total_count = 0
        for collection in [generations_collection, image_generations_collection, video_generations_collection]:
            pipeline = [
                {"$match": {"user_id": user_id, "created_at": {"$gte": start_date, "$lte": end_date}}},
                {"$group": {
                    "_id": None,
                    "success_count": {"$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}},
                    "total_count": {"$sum": 1}
                }}
            ]
            result = list(collection.aggregate(pipeline))
            if result:
                success_count += result[0]["success_count"]
                total_count += result[0]["total_count"]
        
        success_rate = (success_count / total_count * 100) if total_count > 0 else 100
        
        # Cost analysis (mock data for now)
        estimated_cost = total_generations * 0.01  # $0.01 per generation
        
        # Popular features
        feature_usage = {
            "text_generation": total_text,
            "image_generation": total_image,
            "video_generation": total_video,
            "code_generation": total_code,
            "social_media": total_social,
            "workflows": workflows_collection.count_documents({"user_id": user_id})
        }
        
        return {
            "summary": {
                "total_generations": total_generations,
                "success_rate": round(success_rate, 2),
                "avg_response_time": round(avg_response_time, 2),
                "estimated_cost": round(estimated_cost, 2),
                "active_days": len([d for d in daily_activity.values() if d["total"] > 0])
            },
            "daily_activity": daily_activity,
            "generation_breakdown": {
                "text": total_text,
                "image": total_image,
                "video": total_video,
                "code": total_code,
                "social": total_social
            },
            "provider_usage": provider_usage,
            "feature_usage": feature_usage,
            "performance_metrics": {
                "avg_response_time": round(avg_response_time, 2),
                "success_rate": round(success_rate, 2),
                "total_requests": total_count,
                "successful_requests": success_count
            },
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get enhanced analytics: {str(e)}"
        )

@router.get("/usage-trends")
async def get_usage_trends(
    period: str = Query(default="week", description="Period: day, week, month"),
    current_user: str = Depends(get_current_user)
):
    """Get usage trends over different time periods"""
    try:
        # Get user info
        user_info = await AuthService.get_current_user_info(current_user)
        user_id = user_info.user_id
        
        # Calculate date range based on period
        end_date = datetime.utcnow()
        if period == "day":
            start_date = end_date - timedelta(hours=24)
            date_format = "%Y-%m-%d %H:00"
        elif period == "week":
            start_date = end_date - timedelta(days=7)
            date_format = "%Y-%m-%d"
        elif period == "month":
            start_date = end_date - timedelta(days=30)
            date_format = "%Y-%m-%d"
        else:
            raise HTTPException(status_code=400, detail="Invalid period")
        
        # Aggregate pipeline for trends
        pipeline = [
            {"$match": {"user_id": user_id, "created_at": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {
                "_id": {"$dateToString": {"format": date_format, "date": "$created_at"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        trends = {}
        for collection_name, collection in [
            ("text", generations_collection),
            ("image", image_generations_collection),
            ("video", video_generations_collection),
            ("code", code_generations_collection),
            ("social", social_media_generations_collection)
        ]:
            result = list(collection.aggregate(pipeline))
            trends[collection_name] = result
        
        return {
            "period": period,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "trends": trends
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage trends: {str(e)}"
        )

@router.get("/export")
async def export_analytics(
    format: str = Query(default="json", description="Export format: json, csv"),
    days: int = Query(default=30, description="Number of days to export"),
    current_user: str = Depends(get_current_user)
):
    """Export analytics data"""
    try:
        # Get user info
        user_info = await AuthService.get_current_user_info(current_user)
        user_id = user_info.user_id
        
        # Get comprehensive analytics data
        analytics_data = await get_enhanced_dashboard_analytics(days, current_user)
        
        if format == "json":
            return {
                "export_format": "json",
                "generated_at": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "data": analytics_data
            }
        elif format == "csv":
            # TODO: Implement CSV export
            return {"message": "CSV export coming soon"}
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export analytics: {str(e)}"
        )

@router.get("/insights")
async def get_analytics_insights(
    current_user: str = Depends(get_current_user)
):
    """Get AI-powered insights about user's usage patterns"""
    try:
        # Get user info
        user_info = await AuthService.get_current_user_info(current_user)
        user_id = user_info.user_id
        
        # Get data for the last 30 days
        analytics_data = await get_enhanced_dashboard_analytics(30, current_user)
        
        # Generate insights based on data
        insights = []
        
        # Most productive day
        daily_data = analytics_data["daily_activity"]
        if daily_data:
            max_day = max(daily_data.items(), key=lambda x: x[1]["total"])
            insights.append({
                "type": "productivity",
                "title": "Most Productive Day",
                "description": f"You generated {max_day[1]['total']} items on {max_day[0]}",
                "value": max_day[1]["total"],
                "trend": "positive"
            })
        
        # Most used feature
        feature_usage = analytics_data["feature_usage"]
        if feature_usage:
            top_feature = max(feature_usage.items(), key=lambda x: x[1])
            insights.append({
                "type": "feature",
                "title": "Most Used Feature",
                "description": f"You've used {top_feature[0].replace('_', ' ').title()} {top_feature[1]} times",
                "value": top_feature[1],
                "trend": "neutral"
            })
        
        # Performance insight
        performance = analytics_data["performance_metrics"]
        if performance["success_rate"] > 95:
            insights.append({
                "type": "performance",
                "title": "Excellent Success Rate",
                "description": f"Your success rate is {performance['success_rate']}% - keep up the great work!",
                "value": performance["success_rate"],
                "trend": "positive"
            })
        
        # Cost awareness
        if analytics_data["summary"]["estimated_cost"] > 10:
            insights.append({
                "type": "cost",
                "title": "Cost Awareness",
                "description": f"You've spent approximately ${analytics_data['summary']['estimated_cost']} this month",
                "value": analytics_data["summary"]["estimated_cost"],
                "trend": "warning"
            })
        
        return {
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get insights: {str(e)}"
        )