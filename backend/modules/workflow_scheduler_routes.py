from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime

from utils.auth_utils import get_current_user
from models.generation_models import (
    WorkflowSchedule, WorkflowScheduleCreate, WorkflowScheduleUpdate,
    ScheduleStatus
)
from services.workflow_scheduler_service import WorkflowSchedulerService

router = APIRouter(prefix="/api/workflow-schedules", tags=["workflow-schedules"])

# Initialize service
scheduler_service = WorkflowSchedulerService()

@router.post("/", response_model=WorkflowSchedule)
async def create_workflow_schedule(
    schedule_data: WorkflowScheduleCreate,
    current_user: str = Depends(get_current_user)
):
    """Create a new workflow schedule"""
    schedule = await scheduler_service.create_schedule(
        workflow_id=schedule_data.workflow_id,
        user_id=current_user,
        schedule_data=schedule_data.dict()
    )
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create workflow schedule"
        )
    return schedule

@router.get("/", response_model=List[WorkflowSchedule])
async def get_user_schedules(
    current_user: str = Depends(get_current_user)
):
    """Get all workflow schedules for the current user"""
    return await scheduler_service.get_user_schedules(current_user)

@router.get("/{schedule_id}", response_model=WorkflowSchedule)
async def get_workflow_schedule(
    schedule_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get a specific workflow schedule"""
    schedule = await scheduler_service.get_schedule(schedule_id, current_user)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow schedule not found"
        )
    return schedule

@router.put("/{schedule_id}", response_model=WorkflowSchedule)
async def update_workflow_schedule(
    schedule_id: str,
    schedule_update: WorkflowScheduleUpdate,
    current_user: str = Depends(get_current_user)
):
    """Update a workflow schedule"""
    schedule = await scheduler_service.update_schedule(
        schedule_id=schedule_id,
        user_id=current_user,
        update_data=schedule_update.dict(exclude_unset=True)
    )
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow schedule not found"
        )
    return schedule

@router.delete("/{schedule_id}")
async def delete_workflow_schedule(
    schedule_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete a workflow schedule"""
    success = await scheduler_service.delete_schedule(schedule_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow schedule not found"
        )
    return {"message": "Workflow schedule deleted successfully"}

@router.post("/{schedule_id}/pause")
async def pause_workflow_schedule(
    schedule_id: str,
    current_user: str = Depends(get_current_user)
):
    """Pause a workflow schedule"""
    success = await scheduler_service.pause_schedule(schedule_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow schedule not found"
        )
    return {"message": "Workflow schedule paused successfully"}

@router.post("/{schedule_id}/resume")
async def resume_workflow_schedule(
    schedule_id: str,
    current_user: str = Depends(get_current_user)
):
    """Resume a workflow schedule"""
    success = await scheduler_service.resume_schedule(schedule_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow schedule not found"
        )
    return {"message": "Workflow schedule resumed successfully"}

@router.get("/{schedule_id}/analytics")
async def get_schedule_analytics(
    schedule_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get analytics for a workflow schedule"""
    analytics = await scheduler_service.get_schedule_analytics(schedule_id, current_user)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow schedule not found"
        )
    return analytics

@router.get("/validate/cron")
async def validate_cron_expression(
    expression: str,
    current_user: str = Depends(get_current_user)
):
    """Validate a cron expression"""
    is_valid = scheduler_service._validate_cron_expression(expression)
    next_runs = []
    
    if is_valid:
        try:
            # Calculate next 5 run times
            from croniter import croniter
            cron = croniter(expression, datetime.now())
            next_runs = [cron.get_next(datetime).isoformat() for _ in range(5)]
        except Exception:
            pass
    
    return {
        "valid": is_valid,
        "next_runs": next_runs,
        "expression": expression
    }