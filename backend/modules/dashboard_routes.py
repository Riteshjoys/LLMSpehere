from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime, timedelta
from utils.auth_utils import get_current_user
from utils.database import (
    providers_collection, 
    generations_collection,
    image_generations_collection,
    video_generations_collection,
    workflows_collection,
    workflow_executions_collection
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/statistics", response_model=Dict[str, Any])
async def get_dashboard_statistics(current_user: str = Depends(get_current_user)):
    """Get comprehensive dashboard statistics for the current user"""
    try:
        # Get current date for filtering
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Count active providers
        active_providers = providers_collection.count_documents({"is_active": True})
        
        # Count user's generations
        text_generations = list(generations_collection.find(
            {"user_id": current_user}
        ).sort("created_at", -1).limit(10))
        
        image_generations = list(image_generations_collection.find(
            {"user_id": current_user}
        ).sort("created_at", -1).limit(10))
        
        video_generations = list(video_generations_collection.find(
            {"user_id": current_user}
        ).sort("created_at", -1).limit(10))
        
        # Count user's workflows
        user_workflows = list(workflows_collection.find({"user_id": current_user}))
        
        # Count workflow executions
        workflow_executions = list(workflow_executions_collection.find(
            {"user_id": current_user}
        ).sort("started_at", -1).limit(10))
        
        # Calculate totals
        total_generations = len(text_generations) + len(image_generations) + len(video_generations)
        total_workflows = len(user_workflows)
        total_executions = len(workflow_executions)
        
        # Calculate success rate (assuming all completed generations are successful)
        completed_executions = len([e for e in workflow_executions if e.get("status") == "completed"])
        success_rate = round((completed_executions / total_executions) * 100) if total_executions > 0 else 100
        
        # Prepare recent activity (combine all generation types)
        recent_activity = []
        
        # Add text generations
        for gen in text_generations[:5]:
            recent_activity.append({
                "id": str(gen["_id"]),
                "type": "text",
                "title": "Text Generation",
                "description": gen.get("prompt", "Generated text content")[:100] + "...",
                "provider": gen.get("provider_name", "Unknown"),
                "created_at": gen.get("created_at", now).isoformat(),
                "status": "completed"
            })
        
        # Add image generations
        for gen in image_generations[:3]:
            recent_activity.append({
                "id": str(gen["_id"]),
                "type": "image",
                "title": "Image Generation",
                "description": gen.get("prompt", "Generated image content")[:100] + "...",
                "provider": gen.get("provider_name", "Unknown"),
                "created_at": gen.get("created_at", now).isoformat(),
                "status": "completed"
            })
        
        # Add workflow executions
        for exec in workflow_executions[:3]:
            recent_activity.append({
                "id": str(exec["_id"]),
                "type": "workflow",
                "title": "Workflow Execution",
                "description": exec.get("run_name", "Workflow run")[:100] + "...",
                "provider": "Workflow Engine",
                "created_at": exec.get("started_at", now).isoformat(),
                "status": exec.get("status", "unknown")
            })
        
        # Sort by date and take top 10
        recent_activity.sort(key=lambda x: x["created_at"], reverse=True)
        recent_activity = recent_activity[:10]
        
        return {
            "statistics": {
                "total_generations": total_generations,
                "active_workflows": total_workflows,
                "providers_available": active_providers,
                "success_rate": success_rate
            },
            "recent_activity": recent_activity,
            "generation_breakdown": {
                "text": len(text_generations),
                "image": len(image_generations),
                "video": len(video_generations)
            },
            "workflow_stats": {
                "total_workflows": total_workflows,
                "total_executions": total_executions,
                "completed_executions": completed_executions
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard statistics: {str(e)}"
        )