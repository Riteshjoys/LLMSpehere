from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import uuid
import asyncio
import logging
from croniter import croniter
from threading import Thread
import time

from utils.database import get_database
from models.generation_models import WorkflowSchedule, ScheduledWorkflow, ScheduleStatus
from services.workflow_execution_service import WorkflowExecutionService

logger = logging.getLogger(__name__)

class WorkflowSchedulerService:
    def __init__(self):
        self.db = get_database()
        self.schedules_collection = self.db.workflow_schedules
        self.execution_service = WorkflowExecutionService()
        self.running = False
        self.scheduler_thread = None
        
    async def create_schedule(self, workflow_id: str, user_id: str, schedule_data: Dict[str, Any]) -> Optional[WorkflowSchedule]:
        """Create a new workflow schedule"""
        try:
            # Validate cron expression
            if not self._validate_cron_expression(schedule_data.get("cron_expression")):
                raise ValueError("Invalid cron expression")
            
            schedule_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            # Calculate next run time
            next_run = self._calculate_next_run(schedule_data.get("cron_expression"))
            
            schedule_doc = {
                "_id": schedule_id,
                "workflow_id": workflow_id,
                "user_id": user_id,
                "name": schedule_data.get("name", f"Schedule for {workflow_id}"),
                "description": schedule_data.get("description", ""),
                "cron_expression": schedule_data.get("cron_expression"),
                "timezone": schedule_data.get("timezone", "UTC"),
                "status": ScheduleStatus.ACTIVE,
                "input_variables": schedule_data.get("input_variables", {}),
                "max_runs": schedule_data.get("max_runs"),
                "runs_count": 0,
                "next_run_at": next_run,
                "last_run_at": None,
                "created_at": now,
                "updated_at": now,
                "created_by": user_id
            }
            
            self.schedules_collection.insert_one(schedule_doc)
            
            return WorkflowSchedule(
                schedule_id=schedule_id,
                workflow_id=workflow_id,
                user_id=user_id,
                name=schedule_doc["name"],
                description=schedule_doc["description"],
                cron_expression=schedule_doc["cron_expression"],
                timezone=schedule_doc["timezone"],
                status=schedule_doc["status"],
                input_variables=schedule_doc["input_variables"],
                max_runs=schedule_doc["max_runs"],
                runs_count=schedule_doc["runs_count"],
                next_run_at=schedule_doc["next_run_at"],
                last_run_at=schedule_doc["last_run_at"],
                created_at=schedule_doc["created_at"],
                updated_at=schedule_doc["updated_at"],
                created_by=schedule_doc["created_by"]
            )
            
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            return None
    
    async def get_user_schedules(self, user_id: str) -> List[WorkflowSchedule]:
        """Get all schedules for a user"""
        try:
            schedules = []
            for schedule in self.schedules_collection.find({"user_id": user_id}).sort("created_at", -1):
                schedule["schedule_id"] = str(schedule.pop("_id"))
                schedules.append(WorkflowSchedule(**schedule))
            return schedules
        except Exception as e:
            logger.error(f"Error getting user schedules: {e}")
            return []
    
    async def get_schedule(self, schedule_id: str, user_id: str) -> Optional[WorkflowSchedule]:
        """Get a specific schedule"""
        try:
            schedule = self.schedules_collection.find_one({"_id": schedule_id, "user_id": user_id})
            if schedule:
                schedule["schedule_id"] = str(schedule.pop("_id"))
                return WorkflowSchedule(**schedule)
            return None
        except Exception as e:
            logger.error(f"Error getting schedule: {e}")
            return None
    
    async def update_schedule(self, schedule_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[WorkflowSchedule]:
        """Update a workflow schedule"""
        try:
            # Validate cron expression if provided
            if "cron_expression" in update_data and not self._validate_cron_expression(update_data["cron_expression"]):
                raise ValueError("Invalid cron expression")
            
            update_doc = {**update_data, "updated_at": datetime.now(timezone.utc)}
            
            # Recalculate next run time if cron expression changed
            if "cron_expression" in update_data:
                update_doc["next_run_at"] = self._calculate_next_run(update_data["cron_expression"])
            
            result = self.schedules_collection.update_one(
                {"_id": schedule_id, "user_id": user_id},
                {"$set": update_doc}
            )
            
            if result.matched_count > 0:
                return await self.get_schedule(schedule_id, user_id)
            return None
            
        except Exception as e:
            logger.error(f"Error updating schedule: {e}")
            return None
    
    async def delete_schedule(self, schedule_id: str, user_id: str) -> bool:
        """Delete a workflow schedule"""
        try:
            result = self.schedules_collection.delete_one({"_id": schedule_id, "user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting schedule: {e}")
            return False
    
    async def pause_schedule(self, schedule_id: str, user_id: str) -> bool:
        """Pause a workflow schedule"""
        try:
            result = self.schedules_collection.update_one(
                {"_id": schedule_id, "user_id": user_id},
                {"$set": {"status": ScheduleStatus.PAUSED, "updated_at": datetime.now(timezone.utc)}}
            )
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"Error pausing schedule: {e}")
            return False
    
    async def resume_schedule(self, schedule_id: str, user_id: str) -> bool:
        """Resume a workflow schedule"""
        try:
            # Recalculate next run time
            schedule = await self.get_schedule(schedule_id, user_id)
            if not schedule:
                return False
            
            next_run = self._calculate_next_run(schedule.cron_expression)
            
            result = self.schedules_collection.update_one(
                {"_id": schedule_id, "user_id": user_id},
                {"$set": {
                    "status": ScheduleStatus.ACTIVE,
                    "next_run_at": next_run,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"Error resuming schedule: {e}")
            return False
    
    def _validate_cron_expression(self, cron_expression: str) -> bool:
        """Validate cron expression"""
        try:
            croniter(cron_expression)
            return True
        except Exception:
            return False
    
    def _calculate_next_run(self, cron_expression: str) -> datetime:
        """Calculate next run time based on cron expression"""
        try:
            cron = croniter(cron_expression, datetime.now(timezone.utc))
            return cron.get_next(datetime)
        except Exception:
            # Default to 1 hour from now if cron expression is invalid
            return datetime.now(timezone.utc) + timedelta(hours=1)
    
    async def get_due_schedules(self) -> List[WorkflowSchedule]:
        """Get schedules that are due for execution"""
        try:
            now = datetime.now(timezone.utc)
            schedules = []
            
            for schedule in self.schedules_collection.find({
                "status": ScheduleStatus.ACTIVE,
                "next_run_at": {"$lte": now}
            }):
                schedule["schedule_id"] = str(schedule.pop("_id"))
                schedules.append(WorkflowSchedule(**schedule))
            
            return schedules
        except Exception as e:
            logger.error(f"Error getting due schedules: {e}")
            return []
    
    async def process_scheduled_workflows(self):
        """Process scheduled workflows that are due"""
        try:
            due_schedules = await self.get_due_schedules()
            
            for schedule in due_schedules:
                try:
                    # Check if we've reached max runs
                    if schedule.max_runs and schedule.runs_count >= schedule.max_runs:
                        await self.schedules_collection.update_one(
                            {"_id": schedule.schedule_id},
                            {"$set": {"status": ScheduleStatus.COMPLETED}}
                        )
                        continue
                    
                    # Execute the workflow
                    execution = await self.execution_service.execute_workflow(
                        workflow_id=schedule.workflow_id,
                        user_id=schedule.user_id,
                        input_variables=schedule.input_variables,
                        run_name=f"Scheduled run - {schedule.name}"
                    )
                    
                    if execution:
                        # Update schedule with last run info
                        next_run = self._calculate_next_run(schedule.cron_expression)
                        self.schedules_collection.update_one(
                            {"_id": schedule.schedule_id},
                            {"$set": {
                                "last_run_at": datetime.now(timezone.utc),
                                "next_run_at": next_run,
                                "runs_count": schedule.runs_count + 1,
                                "updated_at": datetime.now(timezone.utc)
                            }}
                        )
                        
                        logger.info(f"Executed scheduled workflow: {schedule.workflow_id}")
                    else:
                        logger.error(f"Failed to execute scheduled workflow: {schedule.workflow_id}")
                        
                except Exception as e:
                    logger.error(f"Error processing scheduled workflow {schedule.workflow_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing scheduled workflows: {e}")
    
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("Workflow scheduler started")
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Workflow scheduler stopped")
    
    def _scheduler_loop(self):
        """Background scheduler loop"""
        while self.running:
            try:
                # Use asyncio.create_task for the async method
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.process_scheduled_workflows())
                loop.close()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
            
            # Sleep for 60 seconds before checking again
            time.sleep(60)
    
    async def get_schedule_analytics(self, schedule_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get analytics for a specific schedule"""
        try:
            schedule = await self.get_schedule(schedule_id, user_id)
            if not schedule:
                return None
            
            # Get execution history for this schedule
            # This would require tracking executions by schedule_id
            # For now, return basic schedule info
            return {
                "schedule_id": schedule_id,
                "schedule_name": schedule.name,
                "total_runs": schedule.runs_count,
                "status": schedule.status,
                "next_run_at": schedule.next_run_at,
                "last_run_at": schedule.last_run_at,
                "created_at": schedule.created_at,
                "cron_expression": schedule.cron_expression,
                "max_runs": schedule.max_runs,
                "remaining_runs": (schedule.max_runs - schedule.runs_count) if schedule.max_runs else None
            }
        except Exception as e:
            logger.error(f"Error getting schedule analytics: {e}")
            return None