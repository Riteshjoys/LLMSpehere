"""
Pydantic models for Full Stack AI Assistant
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class ProjectScale(str, Enum):
    SMALL = "small"          # <1K users, <1M records
    MEDIUM = "medium"        # <100K users, <100M records  
    LARGE = "large"          # <1M users, <1B records
    ENTERPRISE = "enterprise" # >1M users, >1B records

class DeploymentTarget(str, Enum):
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    VERCEL = "vercel"
    NETLIFY = "netlify"
    AWS_LAMBDA = "aws_lambda"
    RAILWAY = "railway"

class SecurityLevel(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    ENTERPRISE = "enterprise"

class FullStackProjectRequest(BaseModel):
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Detailed project description")
    target_users: Optional[str] = Field(None, description="Target user base description")
    expected_scale: ProjectScale = Field(ProjectScale.MEDIUM, description="Expected project scale")
    
    # Technical preferences
    frontend_preference: Optional[str] = Field(None, description="Preferred frontend framework")
    backend_preference: Optional[str] = Field(None, description="Preferred backend technology")
    database_requirements: Optional[str] = Field(None, description="Database requirements")
    
    # Performance and scaling
    performance_requirements: Optional[Dict[str, Any]] = Field(default_factory=dict)
    geographic_distribution: Optional[str] = Field("global", description="Geographic distribution requirements")
    
    # Integration and security
    integrations: Optional[List[str]] = Field(default_factory=list, description="Required third-party integrations")
    security_requirements: SecurityLevel = Field(SecurityLevel.STANDARD, description="Security level required")
    
    # Deployment and infrastructure
    deployment_targets: List[DeploymentTarget] = Field(default_factory=lambda: [DeploymentTarget.DOCKER])
    budget: Optional[str] = Field(None, description="Budget constraints")
    timeline: Optional[str] = Field(None, description="Project timeline")
    
    # Additional specifications
    special_requirements: Optional[List[str]] = Field(default_factory=list)
    existing_systems: Optional[List[str]] = Field(default_factory=list)

class TaskExecutionRequest(BaseModel):
    project_id: str
    task_id: Optional[str] = None  # If None, execute next available task
    force_execution: bool = False  # Skip dependency checks
    execution_mode: str = Field("auto", description="auto, manual, or debug")

class CodeGenerationRequest(BaseModel):
    project_id: str
    task_id: str
    file_path: str
    generation_type: str = Field("generate", description="generate, modify, or debug")
    additional_context: Optional[str] = None

class DatabaseOptimizationRequest(BaseModel):
    project_id: str
    database_type: str
    table_schemas: List[Dict[str, Any]]
    query_patterns: List[Dict[str, Any]]
    performance_requirements: Dict[str, Any]
    expected_scale: ProjectScale

class DeploymentRequest(BaseModel):
    project_id: str
    target_platform: DeploymentTarget
    environment: str = Field("production", description="development, staging, or production")
    custom_config: Optional[Dict[str, Any]] = None

class ProjectStatus(BaseModel):
    project_id: str
    user_id: str
    project_name: str
    description: str
    current_phase: str
    progress_percentage: float
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    estimated_completion: Optional[datetime] = None
    last_activity: datetime
    active_task: Optional[Dict[str, Any]] = None

class TaskExecution(BaseModel):
    task_id: str
    project_id: str
    execution_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    output_files: List[str] = Field(default_factory=list)
    test_results: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    generated_code: Optional[str] = None
    documentation: Optional[str] = None

class DatabaseSchema(BaseModel):
    database_name: str
    database_type: str
    tables: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    optimization_strategies: List[str]
    performance_benchmarks: Dict[str, Any]
    scaling_configuration: Dict[str, Any]

class DeploymentConfiguration(BaseModel):
    project_id: str
    target_platform: DeploymentTarget
    docker_config: Optional[Dict[str, Any]] = None
    kubernetes_config: Optional[Dict[str, Any]] = None
    serverless_config: Optional[Dict[str, Any]] = None
    environment_variables: Dict[str, str] = Field(default_factory=dict)
    scaling_rules: Dict[str, Any] = Field(default_factory=dict)
    monitoring_config: Dict[str, Any] = Field(default_factory=dict)

class ProjectAnalytics(BaseModel):
    project_id: str
    total_lines_of_code: int
    test_coverage_percentage: float
    performance_score: float
    security_score: float
    maintainability_index: float
    technical_debt_ratio: float
    estimated_hosting_cost: Optional[float] = None
    deployment_readiness_score: float

class AIAssistantResponse(BaseModel):
    success: bool
    message: str
    project_id: Optional[str] = None
    execution_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    next_recommended_action: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    estimated_completion_time: Optional[int] = None  # in minutes

class CodeQualityReport(BaseModel):
    file_path: str
    lines_of_code: int
    complexity_score: int
    test_coverage: float
    security_issues: List[Dict[str, Any]]
    performance_issues: List[Dict[str, Any]]
    maintainability_score: float
    documentation_completeness: float
    recommendations: List[str]

class PerformanceBenchmark(BaseModel):
    project_id: str
    benchmark_type: str  # "database", "api", "frontend"
    metrics: Dict[str, float]
    baseline_comparison: Optional[Dict[str, float]] = None
    recommendations: List[str]
    optimization_potential: float
    tested_at: datetime