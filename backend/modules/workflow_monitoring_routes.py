from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime

from utils.auth_utils import get_current_user
from services.workflow_monitoring_service import WorkflowMonitoringService

router = APIRouter(prefix="/api/workflow-monitoring", tags=["workflow-monitoring"])

# Initialize service
monitoring_service = WorkflowMonitoringService()

@router.get("/dashboard")
async def get_dashboard_metrics(
    current_user: str = Depends(get_current_user)
):
    """Get comprehensive dashboard metrics for the current user"""
    metrics = await monitoring_service.get_user_dashboard_metrics(current_user)
    return metrics

@router.get("/workflows/{workflow_id}/analytics")
async def get_workflow_analytics(
    workflow_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get detailed analytics for a specific workflow"""
    analytics = await monitoring_service.get_workflow_analytics(workflow_id, current_user)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return analytics

@router.get("/real-time-status")
async def get_real_time_status(
    current_user: str = Depends(get_current_user)
):
    """Get real-time system status"""
    return await monitoring_service.get_real_time_status(current_user)

@router.get("/health-check")
async def get_system_health(
    current_user: str = Depends(get_current_user)
):
    """Get system health status"""
    metrics = await monitoring_service.get_user_dashboard_metrics(current_user)
    return metrics.get("system_health", {})