from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime
import uuid

from utils.auth_utils import get_current_user
from models.generation_models import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowExecutionRequest,
    WorkflowExecution, WorkflowTemplate, WorkflowStepExecution, WorkflowStatus
)
from services.workflow_service import WorkflowService
from services.workflow_execution_service import WorkflowExecutionService

router = APIRouter(prefix="/api/workflows", tags=["workflows"])

# Initialize services
workflow_service = WorkflowService()
execution_service = WorkflowExecutionService()

@router.get("/templates", response_model=List[WorkflowTemplate])
async def get_workflow_templates():
    """Get all available workflow templates"""
    return await workflow_service.get_templates()

@router.get("/templates/{template_id}", response_model=WorkflowTemplate)
async def get_workflow_template(template_id: str):
    """Get a specific workflow template"""
    template = await workflow_service.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )
    return template

@router.post("/from-template/{template_id}", response_model=WorkflowResponse)
async def create_workflow_from_template(
    template_id: str,
    variables: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """Create a new workflow from a template"""
    workflow = await workflow_service.create_from_template(
        template_id=template_id,
        user_id=current_user,
        variables=variables
    )
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )
    return workflow

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow: WorkflowCreate,
    current_user: str = Depends(get_current_user)
):
    """Create a new workflow"""
    return await workflow_service.create_workflow(
        workflow=workflow,
        user_id=current_user
    )

@router.get("/", response_model=List[WorkflowResponse])
async def get_user_workflows(
    current_user: dict = Depends(get_current_user),
    category: str = None,
    tag: str = None,
    status: WorkflowStatus = None
):
    """Get all workflows for the current user"""
    return await workflow_service.get_user_workflows(
        user_id=current_user["user_id"],
        category=category,
        tag=tag,
        status=status
    )

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific workflow"""
    workflow = await workflow_service.get_workflow(
        workflow_id=workflow_id,
        user_id=current_user["user_id"]
    )
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return workflow

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow_update: WorkflowUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a workflow"""
    workflow = await workflow_service.update_workflow(
        workflow_id=workflow_id,
        workflow_update=workflow_update,
        user_id=current_user["user_id"]
    )
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return workflow

@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a workflow"""
    success = await workflow_service.delete_workflow(
        workflow_id=workflow_id,
        user_id=current_user["user_id"]
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return {"message": "Workflow deleted successfully"}

@router.post("/{workflow_id}/duplicate", response_model=WorkflowResponse)
async def duplicate_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Duplicate a workflow"""
    workflow = await workflow_service.duplicate_workflow(
        workflow_id=workflow_id,
        user_id=current_user["user_id"]
    )
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return workflow

# Workflow Execution Endpoints
@router.post("/{workflow_id}/execute", response_model=WorkflowExecution)
async def execute_workflow(
    workflow_id: str,
    execution_request: WorkflowExecutionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Execute a workflow"""
    execution = await execution_service.execute_workflow(
        workflow_id=workflow_id,
        user_id=current_user["user_id"],
        input_variables=execution_request.input_variables,
        run_name=execution_request.run_name
    )
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return execution

@router.get("/{workflow_id}/executions", response_model=List[WorkflowExecution])
async def get_workflow_executions(
    workflow_id: str,
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """Get execution history for a workflow"""
    return await execution_service.get_workflow_executions(
        workflow_id=workflow_id,
        user_id=current_user["user_id"],
        limit=limit,
        offset=offset
    )

@router.get("/{workflow_id}/executions/{execution_id}", response_model=WorkflowExecution)
async def get_workflow_execution(
    workflow_id: str,
    execution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific workflow execution"""
    execution = await execution_service.get_execution(
        execution_id=execution_id,
        user_id=current_user["user_id"]
    )
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow execution not found"
        )
    return execution

@router.post("/{workflow_id}/executions/{execution_id}/stop")
async def stop_workflow_execution(
    workflow_id: str,
    execution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Stop a running workflow execution"""
    success = await execution_service.stop_execution(
        execution_id=execution_id,
        user_id=current_user["user_id"]
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow execution not found or not running"
        )
    return {"message": "Workflow execution stopped"}

@router.get("/executions/", response_model=List[WorkflowExecution])
async def get_user_workflow_executions(
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """Get all workflow executions for the current user"""
    return await execution_service.get_user_executions(
        user_id=current_user["user_id"],
        limit=limit,
        offset=offset
    )

# Analytics Endpoints
@router.get("/{workflow_id}/analytics")
async def get_workflow_analytics(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get analytics for a workflow"""
    analytics = await execution_service.get_workflow_analytics(
        workflow_id=workflow_id,
        user_id=current_user["user_id"]
    )
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return analytics

@router.get("/analytics/dashboard")
async def get_workflow_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get workflow dashboard analytics for the current user"""
    return await execution_service.get_user_dashboard(
        user_id=current_user["user_id"]
    )