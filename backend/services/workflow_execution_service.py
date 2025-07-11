from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re

from utils.database import get_database
from models.generation_models import (
    WorkflowExecution, WorkflowStepExecution, WorkflowStatus, WorkflowStepStatus
)
from services.workflow_service import WorkflowService
from services.text_generation_service import TextGenerationService
from services.image_generation_service import ImageGenerationService
from services.video_generation_service import VideoGenerationService
from services.code_generation_service import CodeGenerationService
from services.social_media_service import SocialMediaService

class WorkflowExecutionService:
    def __init__(self):
        self.db = get_database()
        self.executions_collection = self.db.workflow_executions
        self.workflow_service = WorkflowService()
        
        # Initialize content generation services
        self.text_service = TextGenerationService()
        self.image_service = ImageGenerationService()
        self.video_service = VideoGenerationService()
        self.code_service = CodeGenerationService()
        self.social_media_service = SocialMediaService()
        
        # Thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    async def execute_workflow(self, workflow_id: str, user_id: str, input_variables: Dict[str, Any] = None, run_name: str = None) -> Optional[WorkflowExecution]:
        """Execute a workflow"""
        try:
            # Get workflow
            workflow = await self.workflow_service.get_workflow(workflow_id, user_id)
            if not workflow:
                return None
            
            # Create execution record
            execution_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            execution_data = {
                "_id": execution_id,
                "workflow_id": workflow_id,
                "run_name": run_name or f"Run {now.strftime('%Y-%m-%d %H:%M:%S')}",
                "status": WorkflowStatus.RUNNING,
                "input_variables": input_variables or {},
                "step_executions": [],
                "started_at": now,
                "completed_at": None,
                "duration_seconds": None,
                "user_id": user_id,
                "error_message": None,
                "final_output": None
            }
            
            await self.executions_collection.insert_one(execution_data)
            
            # Start workflow execution in background
            asyncio.create_task(self._run_workflow_steps(execution_id, workflow, input_variables or {}))
            
            # Return initial execution state
            return WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                run_name=execution_data["run_name"],
                status=execution_data["status"],
                input_variables=execution_data["input_variables"],
                step_executions=[],
                started_at=execution_data["started_at"],
                completed_at=execution_data["completed_at"],
                duration_seconds=execution_data["duration_seconds"],
                user_id=execution_data["user_id"],
                error_message=execution_data["error_message"],
                final_output=execution_data["final_output"]
            )
        except Exception as e:
            print(f"Error executing workflow: {e}")
            return None
    
    async def _run_workflow_steps(self, execution_id: str, workflow, input_variables: Dict[str, Any]):
        """Run workflow steps in the correct order"""
        try:
            # Sort steps by order
            sorted_steps = sorted(workflow.steps, key=lambda x: x.order)
            
            step_outputs = {}
            step_executions = []
            
            for step in sorted_steps:
                try:
                    # Check dependencies
                    if step.depends_on:
                        for dep_step_id in step.depends_on:
                            if dep_step_id not in step_outputs:
                                raise Exception(f"Dependency {dep_step_id} not completed")
                    
                    # Create step execution
                    step_execution = {
                        "step_id": step.step_id,
                        "execution_id": execution_id,
                        "status": WorkflowStepStatus.RUNNING,
                        "input_data": self._prepare_step_input(step, input_variables, step_outputs, workflow.variables),
                        "output_data": None,
                        "error_message": None,
                        "started_at": datetime.now(timezone.utc),
                        "completed_at": None,
                        "duration_seconds": None
                    }
                    
                    step_executions.append(step_execution)
                    
                    # Update execution with current step
                    await self.executions_collection.update_one(
                        {"_id": execution_id},
                        {"$set": {"step_executions": step_executions}}
                    )
                    
                    # Execute step
                    start_time = datetime.now(timezone.utc)
                    output = await self._execute_step(step, step_execution["input_data"])
                    end_time = datetime.now(timezone.utc)
                    
                    # Update step execution
                    step_execution.update({
                        "status": WorkflowStepStatus.COMPLETED,
                        "output_data": output,
                        "completed_at": end_time,
                        "duration_seconds": (end_time - start_time).total_seconds()
                    })
                    
                    step_outputs[step.step_id] = output
                    
                except Exception as e:
                    # Handle step failure
                    step_execution.update({
                        "status": WorkflowStepStatus.FAILED,
                        "error_message": str(e),
                        "completed_at": datetime.now(timezone.utc)
                    })
                    
                    # Update execution with failure
                    await self.executions_collection.update_one(
                        {"_id": execution_id},
                        {"$set": {
                            "status": WorkflowStatus.FAILED,
                            "error_message": f"Step {step.step_id} failed: {str(e)}",
                            "completed_at": datetime.now(timezone.utc),
                            "step_executions": step_executions
                        }}
                    )
                    return
            
            # Workflow completed successfully
            end_time = datetime.now(timezone.utc)
            execution = await self.executions_collection.find_one({"_id": execution_id})
            start_time = execution["started_at"]
            
            final_output = {
                "step_outputs": step_outputs,
                "summary": "Workflow completed successfully",
                "total_steps": len(sorted_steps),
                "completed_steps": len([s for s in step_executions if s["status"] == WorkflowStepStatus.COMPLETED])
            }
            
            await self.executions_collection.update_one(
                {"_id": execution_id},
                {"$set": {
                    "status": WorkflowStatus.COMPLETED,
                    "completed_at": end_time,
                    "duration_seconds": (end_time - start_time).total_seconds(),
                    "step_executions": step_executions,
                    "final_output": final_output
                }}
            )
            
            # Update workflow execution count
            await self.workflow_service.workflows_collection.update_one(
                {"_id": workflow.workflow_id},
                {"$inc": {"executions_count": 1}, "$set": {"last_execution_at": end_time}}
            )
            
        except Exception as e:
            print(f"Error running workflow steps: {e}")
            await self.executions_collection.update_one(
                {"_id": execution_id},
                {"$set": {
                    "status": WorkflowStatus.FAILED,
                    "error_message": str(e),
                    "completed_at": datetime.now(timezone.utc)
                }}
            )
    
    def _prepare_step_input(self, step, input_variables: Dict[str, Any], step_outputs: Dict[str, Any], workflow_variables: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input data for a step"""
        try:
            # Start with workflow variables
            context = {**workflow_variables, **input_variables}
            
            # Add step outputs
            for step_id, output in step_outputs.items():
                context[f"step_{step_id}"] = output
                # Also add as previous_output if this step depends on it
                if step.depends_on and step_id in step.depends_on:
                    context["previous_output"] = output
            
            # Process prompt template
            prompt = step.prompt_template
            for key, value in context.items():
                placeholder = "{" + key + "}"
                if placeholder in prompt:
                    prompt = prompt.replace(placeholder, str(value))
            
            return {
                "prompt": prompt,
                "provider": step.provider,
                "model": step.model,
                "settings": step.settings,
                "step_type": step.step_type,
                "context": context
            }
        except Exception as e:
            print(f"Error preparing step input: {e}")
            return {}
    
    async def _execute_step(self, step, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        try:
            step_type = step.step_type
            prompt = input_data.get("prompt", "")
            provider = input_data.get("provider", "")
            model = input_data.get("model", "")
            settings = input_data.get("settings", {})
            
            if step_type == "text_generation":
                response = await self.text_service.generate_text(
                    provider=provider,
                    model=model,
                    prompt=prompt,
                    max_tokens=settings.get("max_tokens", 1000),
                    temperature=settings.get("temperature", 0.7),
                    session_id=str(uuid.uuid4())
                )
                return {
                    "type": "text",
                    "content": response.get("content", ""),
                    "provider": provider,
                    "model": model
                }
            
            elif step_type == "image_generation":
                response = await self.image_service.generate_image(
                    provider=provider,
                    model=model,
                    prompt=prompt,
                    number_of_images=settings.get("number_of_images", 1),
                    session_id=str(uuid.uuid4())
                )
                return {
                    "type": "image",
                    "content": response.get("content", ""),
                    "images": response.get("images", []),
                    "provider": provider,
                    "model": model
                }
            
            elif step_type == "video_generation":
                response = await self.video_service.generate_video(
                    provider=provider,
                    model=model,
                    prompt=prompt,
                    duration=settings.get("duration", 5),
                    aspect_ratio=settings.get("aspect_ratio", "16:9"),
                    resolution=settings.get("resolution", "720p"),
                    session_id=str(uuid.uuid4())
                )
                return {
                    "type": "video",
                    "content": response.get("content", ""),
                    "video_url": response.get("video_url", ""),
                    "provider": provider,
                    "model": model
                }
            
            elif step_type == "code_generation":
                response = await self.code_service.generate_code(
                    provider=provider,
                    model=model,
                    request_type=settings.get("request_type", "generate"),
                    language=settings.get("language", "python"),
                    prompt=prompt,
                    session_id=str(uuid.uuid4())
                )
                return {
                    "type": "code",
                    "content": response.get("content", ""),
                    "language": settings.get("language", "python"),
                    "request_type": settings.get("request_type", "generate"),
                    "provider": provider,
                    "model": model
                }
            
            elif step_type == "social_media_generation":
                response = await self.social_media_service.generate_content(
                    provider=provider,
                    model=model,
                    platform=settings.get("platform", "twitter"),
                    content_type=settings.get("content_type", "post"),
                    prompt=prompt,
                    tone=settings.get("tone", "professional"),
                    session_id=str(uuid.uuid4())
                )
                return {
                    "type": "social_media",
                    "content": response.get("content", ""),
                    "platform": settings.get("platform", "twitter"),
                    "content_type": settings.get("content_type", "post"),
                    "provider": provider,
                    "model": model
                }
            
            else:
                raise Exception(f"Unknown step type: {step_type}")
        
        except Exception as e:
            print(f"Error executing step: {e}")
            raise
    
    async def get_workflow_executions(self, workflow_id: str, user_id: str, limit: int = 50, offset: int = 0) -> List[WorkflowExecution]:
        """Get execution history for a workflow"""
        try:
            executions = []
            async for execution in self.executions_collection.find(
                {"workflow_id": workflow_id, "user_id": user_id}
            ).sort("started_at", -1).skip(offset).limit(limit):
                execution["execution_id"] = str(execution.pop("_id"))
                execution["step_executions"] = [
                    WorkflowStepExecution(**step) for step in execution.get("step_executions", [])
                ]
                executions.append(WorkflowExecution(**execution))
            return executions
        except Exception as e:
            print(f"Error getting workflow executions: {e}")
            return []
    
    async def get_execution(self, execution_id: str, user_id: str) -> Optional[WorkflowExecution]:
        """Get a specific workflow execution"""
        try:
            execution = await self.executions_collection.find_one({"_id": execution_id, "user_id": user_id})
            if execution:
                execution["execution_id"] = str(execution.pop("_id"))
                execution["step_executions"] = [
                    WorkflowStepExecution(**step) for step in execution.get("step_executions", [])
                ]
                return WorkflowExecution(**execution)
            return None
        except Exception as e:
            print(f"Error getting execution: {e}")
            return None
    
    async def stop_execution(self, execution_id: str, user_id: str) -> bool:
        """Stop a running workflow execution"""
        try:
            result = await self.executions_collection.update_one(
                {"_id": execution_id, "user_id": user_id, "status": WorkflowStatus.RUNNING},
                {"$set": {
                    "status": WorkflowStatus.PAUSED,
                    "completed_at": datetime.now(timezone.utc)
                }}
            )
            return result.matched_count > 0
        except Exception as e:
            print(f"Error stopping execution: {e}")
            return False
    
    async def get_user_executions(self, user_id: str, limit: int = 50, offset: int = 0) -> List[WorkflowExecution]:
        """Get all workflow executions for a user"""
        try:
            executions = []
            async for execution in self.executions_collection.find(
                {"user_id": user_id}
            ).sort("started_at", -1).skip(offset).limit(limit):
                execution["execution_id"] = str(execution.pop("_id"))
                execution["step_executions"] = [
                    WorkflowStepExecution(**step) for step in execution.get("step_executions", [])
                ]
                executions.append(WorkflowExecution(**execution))
            return executions
        except Exception as e:
            print(f"Error getting user executions: {e}")
            return []
    
    async def get_workflow_analytics(self, workflow_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get analytics for a workflow"""
        try:
            # Get workflow
            workflow = await self.workflow_service.get_workflow(workflow_id, user_id)
            if not workflow:
                return None
            
            # Get executions
            executions = await self.get_workflow_executions(workflow_id, user_id, limit=100)
            
            # Calculate analytics
            total_executions = len(executions)
            successful_executions = len([e for e in executions if e.status == WorkflowStatus.COMPLETED])
            failed_executions = len([e for e in executions if e.status == WorkflowStatus.FAILED])
            
            avg_duration = 0
            if executions:
                durations = [e.duration_seconds for e in executions if e.duration_seconds]
                if durations:
                    avg_duration = sum(durations) / len(durations)
            
            return {
                "workflow_id": workflow_id,
                "workflow_name": workflow.name,
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "failed_executions": failed_executions,
                "success_rate": (successful_executions / total_executions * 100) if total_executions > 0 else 0,
                "average_duration_seconds": avg_duration,
                "total_steps": len(workflow.steps),
                "last_execution_at": workflow.last_execution_at,
                "recent_executions": executions[:10]
            }
        except Exception as e:
            print(f"Error getting workflow analytics: {e}")
            return None
    
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get workflow dashboard analytics for a user"""
        try:
            # Get user workflows
            workflows = await self.workflow_service.get_user_workflows(user_id)
            
            # Get recent executions
            recent_executions = await self.get_user_executions(user_id, limit=20)
            
            # Calculate dashboard metrics
            total_workflows = len(workflows)
            active_workflows = len([w for w in workflows if w.status == WorkflowStatus.ACTIVE])
            
            total_executions = len(recent_executions)
            successful_executions = len([e for e in recent_executions if e.status == WorkflowStatus.COMPLETED])
            
            return {
                "total_workflows": total_workflows,
                "active_workflows": active_workflows,
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "success_rate": (successful_executions / total_executions * 100) if total_executions > 0 else 0,
                "recent_executions": recent_executions[:5],
                "popular_workflows": workflows[:5]  # Most recently updated
            }
        except Exception as e:
            print(f"Error getting user dashboard: {e}")
            return {}