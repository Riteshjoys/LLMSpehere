from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import uuid

from utils.database import get_database
from models.generation_models import WorkflowExecution, WorkflowStatus, WorkflowStepStatus
from services.workflow_service import WorkflowService
from services.workflow_execution_service import WorkflowExecutionService
from services.workflow_scheduler_service import WorkflowSchedulerService

class WorkflowMonitoringService:
    def __init__(self):
        self.db = get_database()
        self.executions_collection = self.db.workflow_executions
        self.workflows_collection = self.db.workflows
        self.schedules_collection = self.db.workflow_schedules
        
        # Initialize related services
        self.workflow_service = WorkflowService()
        self.execution_service = WorkflowExecutionService()
        self.scheduler_service = WorkflowSchedulerService()
    
    async def get_user_dashboard_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard metrics for a user"""
        try:
            # Get time ranges
            now = datetime.now(timezone.utc)
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            # Get workflows
            workflows = await self.workflow_service.get_user_workflows(user_id)
            
            # Get executions
            all_executions = await self.execution_service.get_user_executions(user_id, limit=1000)
            
            # Get schedules
            schedules = await self.scheduler_service.get_user_schedules(user_id)
            
            # Calculate metrics
            metrics = {
                # Basic counts
                "total_workflows": len(workflows),
                "total_executions": len(all_executions),
                "total_schedules": len(schedules),
                "active_schedules": len([s for s in schedules if s.status == "active"]),
                
                # Workflow status breakdown
                "workflows_by_status": self._count_by_status(workflows),
                "schedules_by_status": self._count_by_status(schedules),
                
                # Execution metrics
                "execution_metrics": self._calculate_execution_metrics(all_executions),
                
                # Time-based metrics
                "today_executions": len([e for e in all_executions if e.started_at >= today]),
                "week_executions": len([e for e in all_executions if e.started_at >= week_ago]),
                "month_executions": len([e for e in all_executions if e.started_at >= month_ago]),
                
                # Performance metrics
                "avg_execution_time": self._calculate_avg_execution_time(all_executions),
                "success_rate": self._calculate_success_rate(all_executions),
                
                # Recent activity
                "recent_executions": [self._format_execution_summary(e) for e in all_executions[:10]],
                "recent_workflows": [self._format_workflow_summary(w) for w in workflows[:5]],
                "upcoming_schedules": await self._get_upcoming_schedules(user_id),
                
                # Trending data
                "execution_trends": self._calculate_execution_trends(all_executions),
                "workflow_usage": self._calculate_workflow_usage(workflows, all_executions),
                
                # System health
                "system_health": self._calculate_system_health(all_executions, schedules)
            }
            
            return metrics
            
        except Exception as e:
            print(f"Error getting dashboard metrics: {e}")
            return {}
    
    def _count_by_status(self, items: List[Any]) -> Dict[str, int]:
        """Count items by status"""
        counts = defaultdict(int)
        for item in items:
            if hasattr(item, 'status'):
                counts[item.status] += 1
        return dict(counts)
    
    def _calculate_execution_metrics(self, executions: List[WorkflowExecution]) -> Dict[str, Any]:
        """Calculate execution metrics"""
        if not executions:
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "running": 0,
                "success_rate": 0,
                "avg_duration": 0
            }
        
        total = len(executions)
        successful = len([e for e in executions if e.status == WorkflowStatus.COMPLETED])
        failed = len([e for e in executions if e.status == WorkflowStatus.FAILED])
        running = len([e for e in executions if e.status == WorkflowStatus.RUNNING])
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "running": running,
            "success_rate": round((successful / total) * 100, 2) if total > 0 else 0,
            "avg_duration": self._calculate_avg_execution_time(executions)
        }
    
    def _calculate_avg_execution_time(self, executions: List[WorkflowExecution]) -> float:
        """Calculate average execution time in seconds"""
        completed_executions = [e for e in executions if e.status == WorkflowStatus.COMPLETED and e.duration_seconds]
        if not completed_executions:
            return 0
        
        total_duration = sum(e.duration_seconds for e in completed_executions)
        return round(total_duration / len(completed_executions), 2)
    
    def _calculate_success_rate(self, executions: List[WorkflowExecution]) -> float:
        """Calculate overall success rate"""
        if not executions:
            return 0
        
        completed = len([e for e in executions if e.status == WorkflowStatus.COMPLETED])
        total = len(executions)
        return round((completed / total) * 100, 2)
    
    def _format_execution_summary(self, execution: WorkflowExecution) -> Dict[str, Any]:
        """Format execution for summary display"""
        return {
            "execution_id": execution.execution_id,
            "workflow_id": execution.workflow_id,
            "run_name": execution.run_name,
            "status": execution.status,
            "started_at": execution.started_at.isoformat(),
            "duration_seconds": execution.duration_seconds,
            "step_count": len(execution.step_executions),
            "completed_steps": len([s for s in execution.step_executions if s.status == WorkflowStepStatus.COMPLETED])
        }
    
    def _format_workflow_summary(self, workflow) -> Dict[str, Any]:
        """Format workflow for summary display"""
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "category": workflow.category,
            "status": workflow.status,
            "step_count": len(workflow.steps),
            "executions_count": workflow.executions_count,
            "last_execution_at": workflow.last_execution_at.isoformat() if workflow.last_execution_at else None
        }
    
    async def _get_upcoming_schedules(self, user_id: str) -> List[Dict[str, Any]]:
        """Get upcoming scheduled executions"""
        try:
            schedules = await self.scheduler_service.get_user_schedules(user_id)
            active_schedules = [s for s in schedules if s.status == "active" and s.next_run_at]
            
            # Sort by next run time
            active_schedules.sort(key=lambda x: x.next_run_at)
            
            return [
                {
                    "schedule_id": s.schedule_id,
                    "name": s.name,
                    "workflow_id": s.workflow_id,
                    "next_run_at": s.next_run_at.isoformat(),
                    "cron_expression": s.cron_expression,
                    "runs_count": s.runs_count
                }
                for s in active_schedules[:10]
            ]
        except Exception as e:
            print(f"Error getting upcoming schedules: {e}")
            return []
    
    def _calculate_execution_trends(self, executions: List[WorkflowExecution]) -> Dict[str, Any]:
        """Calculate execution trends over time"""
        now = datetime.now(timezone.utc)
        
        # Group executions by day for the last 30 days
        daily_counts = defaultdict(int)
        daily_success = defaultdict(int)
        
        for execution in executions:
            if execution.started_at >= now - timedelta(days=30):
                day_key = execution.started_at.strftime("%Y-%m-%d")
                daily_counts[day_key] += 1
                if execution.status == WorkflowStatus.COMPLETED:
                    daily_success[day_key] += 1
        
        # Create time series data
        trend_data = []
        for i in range(30):
            date = now - timedelta(days=29-i)
            day_key = date.strftime("%Y-%m-%d")
            trend_data.append({
                "date": day_key,
                "executions": daily_counts[day_key],
                "successful": daily_success[day_key],
                "success_rate": round((daily_success[day_key] / daily_counts[day_key]) * 100, 2) if daily_counts[day_key] > 0 else 0
            })
        
        return {
            "daily_trends": trend_data,
            "total_days": 30,
            "avg_daily_executions": round(sum(daily_counts.values()) / 30, 2)
        }
    
    def _calculate_workflow_usage(self, workflows: List[Any], executions: List[WorkflowExecution]) -> List[Dict[str, Any]]:
        """Calculate workflow usage statistics"""
        workflow_usage = defaultdict(lambda: {"executions": 0, "successful": 0, "failed": 0})
        
        for execution in executions:
            workflow_usage[execution.workflow_id]["executions"] += 1
            if execution.status == WorkflowStatus.COMPLETED:
                workflow_usage[execution.workflow_id]["successful"] += 1
            elif execution.status == WorkflowStatus.FAILED:
                workflow_usage[execution.workflow_id]["failed"] += 1
        
        # Combine with workflow info
        usage_data = []
        for workflow in workflows:
            usage = workflow_usage[workflow.workflow_id]
            usage_data.append({
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "category": workflow.category,
                "executions": usage["executions"],
                "successful": usage["successful"],
                "failed": usage["failed"],
                "success_rate": round((usage["successful"] / usage["executions"]) * 100, 2) if usage["executions"] > 0 else 0
            })
        
        # Sort by usage
        usage_data.sort(key=lambda x: x["executions"], reverse=True)
        return usage_data[:10]
    
    def _calculate_system_health(self, executions: List[WorkflowExecution], schedules: List[Any]) -> Dict[str, Any]:
        """Calculate system health metrics"""
        now = datetime.now(timezone.utc)
        recent_executions = [e for e in executions if e.started_at >= now - timedelta(hours=24)]
        
        if not recent_executions:
            return {
                "status": "healthy",
                "score": 100,
                "issues": [],
                "recommendations": []
            }
        
        # Calculate health score
        health_score = 100
        issues = []
        recommendations = []
        
        # Check success rate
        success_rate = self._calculate_success_rate(recent_executions)
        if success_rate < 80:
            health_score -= 20
            issues.append("Low success rate in last 24 hours")
            recommendations.append("Review failed executions and fix common issues")
        
        # Check for stuck executions
        stuck_executions = [e for e in recent_executions if e.status == WorkflowStatus.RUNNING and 
                           e.started_at < now - timedelta(hours=2)]
        if stuck_executions:
            health_score -= 15
            issues.append(f"{len(stuck_executions)} executions appear to be stuck")
            recommendations.append("Review and potentially restart stuck executions")
        
        # Check schedule health
        failed_schedules = [s for s in schedules if s.status == "failed"]
        if failed_schedules:
            health_score -= 10
            issues.append(f"{len(failed_schedules)} schedules are in failed state")
            recommendations.append("Review and fix failed schedules")
        
        # Determine status
        if health_score >= 90:
            status = "healthy"
        elif health_score >= 70:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "status": status,
            "score": max(0, health_score),
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def get_workflow_analytics(self, workflow_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed analytics for a specific workflow"""
        try:
            # Get workflow
            workflow = await self.workflow_service.get_workflow(workflow_id, user_id)
            if not workflow:
                return None
            
            # Get executions for this workflow
            executions = await self.execution_service.get_workflow_executions(workflow_id, user_id, limit=100)
            
            # Get schedules for this workflow
            all_schedules = await self.scheduler_service.get_user_schedules(user_id)
            workflow_schedules = [s for s in all_schedules if s.workflow_id == workflow_id]
            
            # Calculate analytics
            analytics = {
                "workflow_info": {
                    "workflow_id": workflow.workflow_id,
                    "name": workflow.name,
                    "description": workflow.description,
                    "category": workflow.category,
                    "status": workflow.status,
                    "created_at": workflow.created_at.isoformat(),
                    "step_count": len(workflow.steps),
                    "total_executions": len(executions)
                },
                "execution_metrics": self._calculate_execution_metrics(executions),
                "performance_trends": self._calculate_workflow_performance_trends(executions),
                "step_analytics": self._calculate_step_analytics(executions),
                "schedule_info": [
                    {
                        "schedule_id": s.schedule_id,
                        "name": s.name,
                        "status": s.status,
                        "cron_expression": s.cron_expression,
                        "runs_count": s.runs_count,
                        "next_run_at": s.next_run_at.isoformat() if s.next_run_at else None
                    }
                    for s in workflow_schedules
                ],
                "recent_executions": [self._format_execution_summary(e) for e in executions[:20]]
            }
            
            return analytics
            
        except Exception as e:
            print(f"Error getting workflow analytics: {e}")
            return None
    
    def _calculate_workflow_performance_trends(self, executions: List[WorkflowExecution]) -> Dict[str, Any]:
        """Calculate performance trends for a specific workflow"""
        if not executions:
            return {"trends": [], "avg_duration": 0}
        
        # Sort executions by date
        sorted_executions = sorted(executions, key=lambda x: x.started_at)
        
        # Group by day
        daily_data = defaultdict(lambda: {"executions": 0, "successful": 0, "total_duration": 0})
        
        for execution in sorted_executions:
            day_key = execution.started_at.strftime("%Y-%m-%d")
            daily_data[day_key]["executions"] += 1
            if execution.status == WorkflowStatus.COMPLETED:
                daily_data[day_key]["successful"] += 1
                if execution.duration_seconds:
                    daily_data[day_key]["total_duration"] += execution.duration_seconds
        
        # Convert to trend data
        trends = []
        for day_key, data in daily_data.items():
            avg_duration = data["total_duration"] / data["successful"] if data["successful"] > 0 else 0
            trends.append({
                "date": day_key,
                "executions": data["executions"],
                "successful": data["successful"],
                "success_rate": round((data["successful"] / data["executions"]) * 100, 2) if data["executions"] > 0 else 0,
                "avg_duration": round(avg_duration, 2)
            })
        
        return {
            "trends": trends,
            "avg_duration": self._calculate_avg_execution_time(executions)
        }
    
    def _calculate_step_analytics(self, executions: List[WorkflowExecution]) -> Dict[str, Any]:
        """Calculate analytics for workflow steps"""
        step_data = defaultdict(lambda: {"total": 0, "successful": 0, "failed": 0, "avg_duration": 0})
        
        for execution in executions:
            for step in execution.step_executions:
                step_data[step.step_id]["total"] += 1
                if step.status == WorkflowStepStatus.COMPLETED:
                    step_data[step.step_id]["successful"] += 1
                elif step.status == WorkflowStepStatus.FAILED:
                    step_data[step.step_id]["failed"] += 1
                
                if step.duration_seconds:
                    step_data[step.step_id]["avg_duration"] += step.duration_seconds
        
        # Calculate averages and success rates
        step_analytics = []
        for step_id, data in step_data.items():
            avg_duration = data["avg_duration"] / data["successful"] if data["successful"] > 0 else 0
            step_analytics.append({
                "step_id": step_id,
                "total_executions": data["total"],
                "successful": data["successful"],
                "failed": data["failed"],
                "success_rate": round((data["successful"] / data["total"]) * 100, 2) if data["total"] > 0 else 0,
                "avg_duration": round(avg_duration, 2)
            })
        
        return {
            "step_breakdown": step_analytics,
            "total_steps": len(step_analytics)
        }
    
    async def get_real_time_status(self, user_id: str) -> Dict[str, Any]:
        """Get real-time system status"""
        try:
            now = datetime.now(timezone.utc)
            
            # Get running executions
            all_executions = await self.execution_service.get_user_executions(user_id, limit=50)
            running_executions = [e for e in all_executions if e.status == WorkflowStatus.RUNNING]
            
            # Get active schedules
            schedules = await self.scheduler_service.get_user_schedules(user_id)
            active_schedules = [s for s in schedules if s.status == "active"]
            
            # Get next scheduled execution
            next_execution = None
            if active_schedules:
                next_schedule = min(active_schedules, key=lambda s: s.next_run_at or datetime.max.replace(tzinfo=timezone.utc))
                if next_schedule.next_run_at:
                    next_execution = {
                        "schedule_id": next_schedule.schedule_id,
                        "name": next_schedule.name,
                        "next_run_at": next_schedule.next_run_at.isoformat(),
                        "time_until": str(next_schedule.next_run_at - now)
                    }
            
            return {
                "timestamp": now.isoformat(),
                "running_executions": len(running_executions),
                "active_schedules": len(active_schedules),
                "next_execution": next_execution,
                "recent_activity": [self._format_execution_summary(e) for e in all_executions[:5]],
                "system_load": {
                    "current_executions": len(running_executions),
                    "max_concurrent": 10,  # Could be configurable
                    "load_percentage": round((len(running_executions) / 10) * 100, 2)
                }
            }
            
        except Exception as e:
            print(f"Error getting real-time status: {e}")
            return {"timestamp": now.isoformat(), "error": str(e)}