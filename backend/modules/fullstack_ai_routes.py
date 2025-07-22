"""
Full Stack AI Assistant API Routes
Premium feature for advanced users
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from utils.auth_utils import get_current_user
from services.auth_service import AuthService
from services.fullstack_ai_assistant import FullStackAIAssistant
from models.fullstack_ai_models import (
    FullStackProjectRequest, TaskExecutionRequest, CodeGenerationRequest,
    DatabaseOptimizationRequest, DeploymentRequest, ProjectStatus,
    AIAssistantResponse, DeploymentConfiguration, ProjectAnalytics
)

router = APIRouter(prefix="/api/fullstack-ai", tags=["fullstack_ai_assistant"])

# Initialize AI Assistant service
ai_assistant = FullStackAIAssistant()
auth_service = AuthService()

async def verify_premium_access(current_user: str = Depends(get_current_user)):
    """Verify user has premium access to AI Assistant"""
    try:
        user_info = await auth_service.get_current_user_info(current_user)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user has premium access
        user_plan = user_info.get("plan", "free")
        if user_plan not in ["premium", "pro", "enterprise"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Premium subscription required to access Full Stack AI Assistant"
            )
        
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying user access: {str(e)}"
        )

@router.post("/project/initialize", response_model=AIAssistantResponse)
async def initialize_fullstack_project(
    request: FullStackProjectRequest,
    background_tasks: BackgroundTasks,
    user_info: dict = Depends(verify_premium_access)
):
    """
    Initialize a new full-stack project with comprehensive AI analysis
    """
    try:
        # Convert request to dict for processing
        project_data = request.dict()
        user_id = user_info["user_id"]
        
        # Initialize project in background for better UX
        project_id = await ai_assistant.initialize_project(project_data, user_id)
        
        return AIAssistantResponse(
            success=True,
            message="Full-stack project initialized successfully",
            project_id=project_id,
            data={"project_name": request.name},
            next_recommended_action="review_project_plan",
            estimated_completion_time=5  # Initial analysis takes ~5 minutes
        )
        
    except Exception as e:
        return AIAssistantResponse(
            success=False,
            message=f"Failed to initialize project: {str(e)}",
            warnings=["Check your project requirements and try again"]
        )

@router.get("/project/{project_id}/status", response_model=ProjectStatus)
async def get_project_status(
    project_id: str,
    user_info: dict = Depends(verify_premium_access)
):
    """
    Get comprehensive project status and progress
    """
    try:
        status = await ai_assistant.get_project_status(project_id, user_info["user_id"])
        return status
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving project status: {str(e)}"
        )

@router.post("/project/{project_id}/execute-task", response_model=AIAssistantResponse)
async def execute_project_task(
    project_id: str,
    request: TaskExecutionRequest,
    background_tasks: BackgroundTasks,
    user_info: dict = Depends(verify_premium_access)
):
    """
    Execute a specific project task or the next available task
    """
    try:
        # Validate project ownership
        await ai_assistant.validate_project_access(project_id, user_info["user_id"])
        
        # Execute task in background
        execution_id = await ai_assistant.execute_task(
            project_id,
            request.task_id,
            user_info["user_id"],
            request.execution_mode,
            request.force_execution
        )
        
        return AIAssistantResponse(
            success=True,
            message="Task execution started successfully",
            project_id=project_id,
            execution_id=execution_id,
            next_recommended_action="monitor_task_progress",
            estimated_completion_time=30  # Average task execution time
        )
        
    except Exception as e:
        return AIAssistantResponse(
            success=False,
            message=f"Failed to execute task: {str(e)}"
        )

@router.post("/project/{project_id}/generate-code", response_model=AIAssistantResponse)
async def generate_project_code(
    project_id: str,
    request: CodeGenerationRequest,
    user_info: dict = Depends(verify_premium_access)
):
    """
    Generate code for a specific file or component
    """
    try:
        await ai_assistant.validate_project_access(project_id, user_info["user_id"])
        
        result = await ai_assistant.generate_code(
            project_id,
            request.task_id,
            request.file_path,
            request.generation_type,
            request.additional_context
        )
        
        return AIAssistantResponse(
            success=True,
            message="Code generated successfully",
            project_id=project_id,
            data=result,
            next_recommended_action="review_generated_code"
        )
        
    except Exception as e:
        return AIAssistantResponse(
            success=False,
            message=f"Code generation failed: {str(e)}"
        )

@router.post("/project/{project_id}/optimize-database", response_model=AIAssistantResponse)
async def optimize_project_database(
    project_id: str,
    request: DatabaseOptimizationRequest,
    user_info: dict = Depends(verify_premium_access)
):
    """
    Optimize database schema and queries for high performance
    """
    try:
        await ai_assistant.validate_project_access(project_id, user_info["user_id"])
        
        optimization_result = await ai_assistant.optimize_database(
            project_id,
            request.database_type,
            request.table_schemas,
            request.query_patterns,
            request.performance_requirements,
            request.expected_scale
        )
        
        return AIAssistantResponse(
            success=True,
            message="Database optimization completed",
            project_id=project_id,
            data=optimization_result,
            next_recommended_action="implement_optimization_recommendations"
        )
        
    except Exception as e:
        return AIAssistantResponse(
            success=False,
            message=f"Database optimization failed: {str(e)}"
        )

@router.post("/project/{project_id}/deploy", response_model=AIAssistantResponse)
async def deploy_project(
    project_id: str,
    request: DeploymentRequest,
    background_tasks: BackgroundTasks,
    user_info: dict = Depends(verify_premium_access)
):
    """
    Deploy project to specified platform
    """
    try:
        await ai_assistant.validate_project_access(project_id, user_info["user_id"])
        
        deployment_id = await ai_assistant.deploy_project(
            project_id,
            request.target_platform,
            request.environment,
            request.custom_config
        )
        
        return AIAssistantResponse(
            success=True,
            message=f"Deployment to {request.target_platform} initiated",
            project_id=project_id,
            execution_id=deployment_id,
            next_recommended_action="monitor_deployment_progress",
            estimated_completion_time=15  # Deployment typically takes 10-20 minutes
        )
        
    except Exception as e:
        return AIAssistantResponse(
            success=False,
            message=f"Deployment failed: {str(e)}"
        )

@router.get("/project/{project_id}/analytics", response_model=ProjectAnalytics)
async def get_project_analytics(
    project_id: str,
    user_info: dict = Depends(verify_premium_access)
):
    """
    Get comprehensive project analytics and metrics
    """
    try:
        await ai_assistant.validate_project_access(project_id, user_info["user_id"])
        
        analytics = await ai_assistant.get_project_analytics(project_id)
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving project analytics: {str(e)}"
        )

@router.get("/project/{project_id}/deployment-config", response_model=DeploymentConfiguration)
async def get_deployment_configuration(
    project_id: str,
    target_platform: str,
    user_info: dict = Depends(verify_premium_access)
):
    """
    Generate deployment configuration for specified platform
    """
    try:
        await ai_assistant.validate_project_access(project_id, user_info["user_id"])
        
        config = await ai_assistant.generate_deployment_config(project_id, target_platform)
        return config
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating deployment configuration: {str(e)}"
        )

@router.get("/projects", response_model=List[ProjectStatus])
async def list_user_projects(
    user_info: dict = Depends(verify_premium_access)
):
    """
    List all projects for the current user
    """
    try:
        projects = await ai_assistant.get_user_projects(user_info["user_id"])
        return projects
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user projects: {str(e)}"
        )

@router.delete("/project/{project_id}")
async def delete_project(
    project_id: str,
    user_info: dict = Depends(verify_premium_access)
):
    """
    Delete a project and all associated data
    """
    try:
        await ai_assistant.validate_project_access(project_id, user_info["user_id"])
        await ai_assistant.delete_project(project_id)
        
        return {"message": "Project deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting project: {str(e)}"
        )

@router.post("/project/{project_id}/pause")
async def pause_project(
    project_id: str,
    user_info: dict = Depends(verify_premium_access)
):
    """
    Pause project execution
    """
    try:
        await ai_assistant.validate_project_access(project_id, user_info["user_id"])
        await ai_assistant.pause_project(project_id)
        
        return {"message": "Project paused successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error pausing project: {str(e)}"
        )

@router.post("/project/{project_id}/resume")
async def resume_project(
    project_id: str,
    user_info: dict = Depends(verify_premium_access)
):
    """
    Resume paused project execution
    """
    try:
        await ai_assistant.validate_project_access(project_id, user_info["user_id"])
        await ai_assistant.resume_project(project_id)
        
        return {"message": "Project resumed successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resuming project: {str(e)}"
        )

@router.get("/capabilities")
async def get_ai_assistant_capabilities(
    user_info: dict = Depends(verify_premium_access)
):
    """
    Get comprehensive list of AI Assistant capabilities
    """
    return {
        "project_management": [
            "Comprehensive requirement analysis",
            "Automated task decomposition", 
            "Dependency tracking and resolution",
            "Progress monitoring and reporting"
        ],
        "development": [
            "Full-stack code generation",
            "Advanced debugging and optimization",
            "Test generation and execution", 
            "Code quality analysis"
        ],
        "database": [
            "High-performance schema design",
            "Query optimization for 1000M+ records",
            "Sharding and partitioning strategies",
            "Performance benchmarking"
        ],
        "deployment": [
            "Docker containerization",
            "Kubernetes orchestration", 
            "Serverless platform deployment",
            "CI/CD pipeline automation"
        ],
        "supported_technologies": {
            "frontend": ["React", "Vue", "Angular", "Svelte", "Next.js"],
            "backend": ["FastAPI", "Node.js", "Django", "Spring Boot", "Go"],
            "databases": ["PostgreSQL", "MongoDB", "Redis", "Cassandra", "Elasticsearch"],
            "deployment": ["Docker", "Kubernetes", "Vercel", "Netlify", "AWS Lambda"]
        }
    }