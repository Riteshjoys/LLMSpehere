from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class WorkflowStepType(str, Enum):
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    CODE_GENERATION = "code_generation"
    SOCIAL_MEDIA_GENERATION = "social_media_generation"

class WorkflowStepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class ScheduleStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowStep(BaseModel):
    step_id: str
    step_type: WorkflowStepType
    name: str
    description: Optional[str] = None
    provider: str
    model: str
    prompt_template: str  # Can include variables like {previous_output}, {user_input}
    settings: Optional[Dict[str, Any]] = {}
    depends_on: Optional[List[str]] = []  # List of step_ids this step depends on
    condition: Optional[str] = None  # Optional condition to run this step
    order: int = 0

class WorkflowTemplate(BaseModel):
    template_id: str
    name: str
    description: str
    category: str
    tags: List[str] = []
    steps: List[WorkflowStep]
    variables: Optional[Dict[str, Any]] = {}  # Template variables

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = "custom"
    tags: Optional[List[str]] = []
    steps: List[WorkflowStep]
    variables: Optional[Dict[str, Any]] = {}
    is_template: Optional[bool] = False
    schedule: Optional[Dict[str, Any]] = None  # Cron-like scheduling

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    steps: Optional[List[WorkflowStep]] = None
    variables: Optional[Dict[str, Any]] = None
    is_template: Optional[bool] = None
    schedule: Optional[Dict[str, Any]] = None

class WorkflowExecutionRequest(BaseModel):
    workflow_id: str
    input_variables: Optional[Dict[str, Any]] = {}
    run_name: Optional[str] = None

class WorkflowStepExecution(BaseModel):
    step_id: str
    execution_id: str
    status: WorkflowStepStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

class WorkflowExecution(BaseModel):
    execution_id: str
    workflow_id: str
    run_name: str
    status: WorkflowStatus
    input_variables: Dict[str, Any]
    step_executions: List[WorkflowStepExecution]
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    user_id: str
    error_message: Optional[str] = None
    final_output: Optional[Dict[str, Any]] = None

class WorkflowResponse(BaseModel):
    workflow_id: str
    name: str
    description: Optional[str] = None
    category: str
    tags: List[str]
    status: WorkflowStatus
    steps: List[WorkflowStep]
    variables: Dict[str, Any]
    is_template: bool
    schedule: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    user_id: str
    executions_count: int = 0
    last_execution_at: Optional[datetime] = None

# Workflow Scheduling Models
class WorkflowSchedule(BaseModel):
    schedule_id: str
    workflow_id: str
    user_id: str
    name: str
    description: Optional[str] = None
    cron_expression: str  # Cron expression for scheduling
    timezone: str = "UTC"
    status: ScheduleStatus
    input_variables: Dict[str, Any] = {}
    max_runs: Optional[int] = None  # Maximum number of runs (None = unlimited)
    runs_count: int = 0
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: str

class ScheduledWorkflow(BaseModel):
    workflow_id: str
    schedule_id: str
    user_id: str
    name: str
    description: Optional[str] = None
    cron_expression: str
    status: ScheduleStatus
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None

class WorkflowScheduleCreate(BaseModel):
    workflow_id: str
    name: str
    description: Optional[str] = None
    cron_expression: str
    timezone: str = "UTC"
    input_variables: Dict[str, Any] = {}
    max_runs: Optional[int] = None

class WorkflowScheduleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cron_expression: Optional[str] = None
    timezone: Optional[str] = None
    input_variables: Optional[Dict[str, Any]] = None
    max_runs: Optional[int] = None
    status: Optional[ScheduleStatus] = None

class TextGenerationRequest(BaseModel):
    provider_name: str
    model: str
    prompt: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    session_id: Optional[str] = None

class ImageGenerationRequest(BaseModel):
    provider_name: str
    model: str
    prompt: str
    number_of_images: Optional[int] = 1
    session_id: Optional[str] = None

class VideoGenerationRequest(BaseModel):
    provider_name: str
    model: str
    prompt: str
    duration: Optional[int] = 5  # seconds
    aspect_ratio: Optional[str] = "16:9"
    resolution: Optional[str] = "720p"
    session_id: Optional[str] = None

class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime

class GenerationResponse(BaseModel):
    generation_id: str
    session_id: str
    provider: str
    model: str
    prompt: str
    content: str
    created_at: datetime

class CodeGenerationRequest(BaseModel):
    provider: str
    model: str
    request_type: str  # generate, debug, optimize, refactor, review, documentation, test, explain, architecture
    language: str  # programming language
    prompt: str
    max_tokens: Optional[int] = 4000
    session_id: Optional[str] = None

class CodeGenerationResponse(BaseModel):
    id: str
    session_id: str
    provider: str
    model: str
    request_type: str
    language: str
    prompt: str
    response: str
    user_id: str
    created_at: datetime
    status: str = "completed"