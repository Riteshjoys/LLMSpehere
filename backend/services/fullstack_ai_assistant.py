"""
Fully Capable Full Stack AI Assistant Service
Based on advanced AI agent architectures like Devin and Replit Agent
"""

import asyncio
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from emergentintegrations.llm.chat import LlmChat, UserMessage
from utils.database import db
import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class ProjectPhase(str, Enum):
    PLANNING = "planning"
    ANALYSIS = "analysis"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"

class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    MYSQL = "mysql"
    REDIS = "redis"
    CASSANDRA = "cassandra"
    ELASTIC = "elasticsearch"

@dataclass
class TaskDependency:
    task_id: str
    dependency_type: str  # "requires", "blocks", "optional"

@dataclass
class SubTask:
    id: str
    name: str
    description: str
    status: TaskStatus
    estimated_time: int  # in minutes
    dependencies: List[TaskDependency]
    files_to_modify: List[str]
    tests_required: List[str]
    completion_criteria: List[str]
    priority: int  # 1-5, 5 being highest
    assigned_to: str  # "frontend", "backend", "database", "devops"
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    output: Optional[Dict[str, Any]] = None

@dataclass
class ProjectMemory:
    project_id: str
    user_id: str
    project_name: str
    description: str
    tech_stack: Dict[str, Any]
    database_design: Dict[str, Any]
    architecture_decisions: List[Dict[str, Any]]
    current_phase: ProjectPhase
    subtasks: List[SubTask]
    completed_features: List[str]
    known_issues: List[Dict[str, Any]]
    deployment_config: Dict[str, Any]
    performance_requirements: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class FullStackAIAssistant:
    """
    Advanced AI Assistant capable of building complete full-stack applications
    with production-ready code, optimized databases, and automated deployment
    """
    
    def __init__(self):
        self.db = db
        self.active_projects: Dict[str, ProjectMemory] = {}
        
        # AI Models configuration for different tasks
        self.models_config = {
            "planning": {"provider": "anthropic", "model": "claude-sonnet-4-20250514"},
            "architecture": {"provider": "openai", "model": "gpt-4o"},
            "database": {"provider": "anthropic", "model": "claude-opus-4-20250514"},
            "frontend": {"provider": "openai", "model": "gpt-4o"},
            "backend": {"provider": "anthropic", "model": "claude-sonnet-4-20250514"},
            "testing": {"provider": "openai", "model": "o1-mini"},
            "deployment": {"provider": "openai", "model": "gpt-4o"},
            "debugging": {"provider": "openai", "model": "o1-mini"}
        }
        
        self.system_prompts = self._initialize_system_prompts()
        
    def _initialize_system_prompts(self) -> Dict[str, str]:
        """Initialize specialized system prompts for different development phases"""
        return {
            "planning": """You are an expert software architect and project manager with 20+ years of experience building production-scale applications. Your role is to analyze requirements and create comprehensive, actionable project plans.

CAPABILITIES:
- Break down complex projects into manageable, modular tasks
- Identify dependencies and potential blockers
- Estimate realistic timelines and resource requirements
- Consider scalability, performance, and maintainability from the start
- Design for cloud-native, containerized deployment

APPROACH:
1. Thoroughly analyze the requirements and ask clarifying questions
2. Research best practices and current technology trends
3. Create detailed task breakdowns with clear acceptance criteria
4. Identify potential risks and mitigation strategies
5. Provide realistic estimates and milestone planning

DELIVERABLES:
- Comprehensive project breakdown with subtasks
- Technology stack recommendations
- Architecture overview
- Database design strategy
- Deployment and scaling considerations
- Risk assessment and mitigation plan""",

            "architecture": """You are a senior solution architect specializing in scalable, high-performance full-stack applications. You design systems that can handle millions of users and massive data volumes.

FOCUS AREAS:
- Microservices architecture with clear boundaries
- Database sharding and partitioning strategies
- Caching layers and performance optimization
- Security and compliance considerations
- Container orchestration and cloud deployment
- API design and inter-service communication

DESIGN PRINCIPLES:
- Scalability from day one
- Fault tolerance and resilience
- Performance and efficiency
- Security by design
- Maintainability and modularity
- Cost optimization

DELIVERABLES:
- System architecture diagrams
- Database schema and optimization strategies
- API specifications and contracts
- Infrastructure and deployment architecture
- Performance and scalability benchmarks""",

            "database": """You are a database architect and performance optimization expert specializing in high-scale systems handling 1000M+ records and concurrent users.

EXPERTISE:
- Multi-database architectures (SQL, NoSQL, Graph, Time-series)
- Horizontal and vertical scaling strategies
- Sharding, partitioning, and replication
- Query optimization and indexing strategies
- Data modeling for performance
- ACID compliance and eventual consistency
- Backup, recovery, and disaster planning

OPTIMIZATION STRATEGIES:
- Read/write splitting and connection pooling
- Caching layers (Redis, Memcached, CDN)
- Data archiving and lifecycle management
- Monitoring and performance tuning
- Security and access control

DELIVERABLES:
- Optimized database schemas
- Indexing and query optimization plans
- Scaling and partitioning strategies
- Performance benchmarking scripts
- Monitoring and alerting setup""",

            "development": """You are an expert full-stack developer with mastery in modern frameworks, clean code principles, and production-ready development practices.

TECHNICAL SKILLS:
- Frontend: React, Vue, Angular, TypeScript, responsive design
- Backend: Node.js, Python, Java, Go, microservices
- Databases: PostgreSQL, MongoDB, Redis, Elasticsearch
- DevOps: Docker, Kubernetes, CI/CD, monitoring
- Testing: Unit, integration, e2e, performance testing

DEVELOPMENT PRINCIPLES:
- Clean, maintainable, well-documented code
- Test-driven development (TDD)
- Security best practices
- Performance optimization
- Error handling and logging
- Code reusability and modularity

DELIVERABLES:
- Production-ready code with comprehensive tests
- API documentation and examples
- Error handling and validation
- Security implementations
- Performance optimizations
- Deployment configurations""",

            "testing": """You are a QA automation engineer and testing specialist focused on ensuring production readiness and reliability.

TESTING STRATEGIES:
- Unit tests with high coverage (>90%)
- Integration tests for API contracts
- End-to-end tests for critical user flows
- Performance and load testing
- Security and penetration testing
- Accessibility and usability testing

QUALITY ASSURANCE:
- Automated test suites with CI/CD integration
- Code quality metrics and static analysis
- Performance benchmarking and monitoring
- Error tracking and debugging
- User acceptance testing scenarios

DELIVERABLES:
- Comprehensive test suites
- Performance benchmarking reports
- Security audit findings
- Quality metrics dashboard
- Automated testing pipelines""",

            "deployment": """You are a DevOps engineer and cloud architect specializing in containerized deployments and serverless architectures.

DEPLOYMENT EXPERTISE:
- Docker containerization and optimization
- Kubernetes orchestration and scaling
- Serverless platforms (Vercel, Netlify, AWS Lambda)
- CI/CD pipelines and automation
- Infrastructure as Code (Terraform, CloudFormation)
- Monitoring and observability

DEPLOYMENT STRATEGIES:
- Blue-green deployments
- Canary releases
- Rolling updates
- Auto-scaling configurations
- Health checks and monitoring
- Disaster recovery planning

DELIVERABLES:
- Docker configurations and optimizations
- Kubernetes manifests and helm charts
- CI/CD pipeline configurations
- Infrastructure automation scripts
- Monitoring and alerting setup
- Deployment documentation and runbooks"""
        }
    
    async def initialize_project(self, project_request: Dict[str, Any], user_id: str) -> str:
        """Initialize a new full-stack project with comprehensive analysis"""
        try:
            project_id = str(uuid.uuid4())
            
            # Phase 1: Requirements Analysis and Planning
            planning_response = await self._execute_planning_phase(project_request, user_id)
            
            # Create project memory
            project_memory = ProjectMemory(
                project_id=project_id,
                user_id=user_id,
                project_name=project_request.get("name", f"Project_{project_id[:8]}"),
                description=project_request.get("description", ""),
                tech_stack=planning_response.get("tech_stack", {}),
                database_design=planning_response.get("database_design", {}),
                architecture_decisions=planning_response.get("architecture_decisions", []),
                current_phase=ProjectPhase.PLANNING,
                subtasks=planning_response.get("subtasks", []),
                completed_features=[],
                known_issues=[],
                deployment_config=planning_response.get("deployment_config", {}),
                performance_requirements=planning_response.get("performance_requirements", {}),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store in memory and database
            self.active_projects[project_id] = project_memory
            await self._save_project_memory(project_memory)
            
            logger.info(f"Initialized project {project_id} for user {user_id}")
            return project_id
            
        except Exception as e:
            logger.error(f"Error initializing project: {str(e)}")
            raise
    
    async def _execute_planning_phase(self, project_request: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute comprehensive project planning using advanced AI analysis"""
        try:
            # Get provider configuration for planning
            provider_config = await self._get_provider_config(
                self.models_config["planning"]["provider"],
                self.models_config["planning"]["model"]
            )
            
            # Create specialized planning chat
            chat = LlmChat(
                api_key=provider_config["api_key"],
                session_id=str(uuid.uuid4()),
                system_message=self.system_prompts["planning"]
            ).with_model(
                self.models_config["planning"]["provider"],
                self.models_config["planning"]["model"]
            ).with_max_tokens(8000)
            
            # Construct comprehensive planning prompt
            planning_prompt = f"""
FULL-STACK PROJECT ANALYSIS REQUEST:

PROJECT DETAILS:
- Name: {project_request.get('name', 'Unnamed Project')}
- Description: {project_request.get('description', 'No description provided')}
- Target Users: {project_request.get('target_users', 'Not specified')}
- Expected Scale: {project_request.get('expected_scale', 'Not specified')}
- Performance Requirements: {project_request.get('performance_requirements', {})}
- Budget Constraints: {project_request.get('budget', 'Not specified')}
- Timeline: {project_request.get('timeline', 'Not specified')}

TECHNICAL REQUIREMENTS:
- Preferred Frontend Framework: {project_request.get('frontend_preference', 'React (recommended)')}
- Preferred Backend Technology: {project_request.get('backend_preference', 'FastAPI/Node.js (recommended)')}
- Database Requirements: {project_request.get('database_requirements', 'High performance, scalable')}
- Integration Requirements: {project_request.get('integrations', [])}
- Security Requirements: {project_request.get('security_requirements', 'Standard')}

DEPLOYMENT PREFERENCES:
- Target Platforms: Containerized (Docker, Kubernetes) and Serverless (Vercel, Netlify)
- Scaling Requirements: Must handle 1000M+ records and high concurrent users
- Geographic Distribution: {project_request.get('geographic_distribution', 'Global')}

ANALYSIS REQUIRED:
1. **Project Breakdown**: Create detailed subtasks with dependencies, estimates, and priorities
2. **Technology Stack**: Recommend optimal tech stack for requirements and scale
3. **Database Design Strategy**: Design for 1000M+ records with optimal performance
4. **Architecture Overview**: Scalable, maintainable system architecture
5. **Performance Strategy**: Caching, optimization, and scaling approaches
6. **Security Framework**: Authentication, authorization, and data protection
7. **Deployment Strategy**: Container and serverless deployment configurations
8. **Risk Assessment**: Potential challenges and mitigation strategies

Please provide a comprehensive JSON response with detailed analysis and actionable recommendations.
"""
            
            # Get AI planning response
            response = await chat.send_message(UserMessage(text=planning_prompt))
            
            # Parse and structure the response
            planning_data = await self._parse_planning_response(response)
            
            return planning_data
            
        except Exception as e:
            logger.error(f"Error in planning phase: {str(e)}")
            raise
    
    async def _parse_planning_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse and structure AI planning response into actionable data"""
        try:
            # Extract JSON from response if wrapped in markdown or text
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = ai_response[json_start:json_end]
                planning_data = json.loads(json_str)
            else:
                # Fallback parsing if no JSON structure found
                planning_data = self._create_default_planning_structure(ai_response)
            
            # Ensure all required fields are present
            required_fields = [
                "tech_stack", "database_design", "architecture_decisions",
                "subtasks", "deployment_config", "performance_requirements"
            ]
            
            for field in required_fields:
                if field not in planning_data:
                    planning_data[field] = {}
            
            # Convert subtasks to SubTask objects
            if "subtasks" in planning_data:
                structured_subtasks = []
                for task_data in planning_data["subtasks"]:
                    subtask = SubTask(
                        id=task_data.get("id", str(uuid.uuid4())),
                        name=task_data.get("name", "Unnamed Task"),
                        description=task_data.get("description", ""),
                        status=TaskStatus.PENDING,
                        estimated_time=task_data.get("estimated_time", 60),
                        dependencies=[TaskDependency(**dep) for dep in task_data.get("dependencies", [])],
                        files_to_modify=task_data.get("files_to_modify", []),
                        tests_required=task_data.get("tests_required", []),
                        completion_criteria=task_data.get("completion_criteria", []),
                        priority=task_data.get("priority", 3),
                        assigned_to=task_data.get("assigned_to", "development"),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    structured_subtasks.append(subtask)
                
                planning_data["subtasks"] = structured_subtasks
            
            return planning_data
            
        except Exception as e:
            logger.error(f"Error parsing planning response: {str(e)}")
            return self._create_default_planning_structure(ai_response)
    
    async def _get_provider_config(self, provider: str, model: str) -> Dict[str, Any]:
        """Get provider configuration from database"""
        try:
            providers_collection = self.db.providers
            
            provider_mapping = {
                "openai": "openai_api_key",
                "anthropic": "anthropic_api_key", 
                "gemini": "gemini_api_key"
            }
            
            provider_key = provider_mapping.get(provider)
            if not provider_key:
                raise ValueError(f"Unsupported provider: {provider}")
            
            provider_doc = await providers_collection.find_one({"provider": provider})
            
            if not provider_doc or not provider_doc.get(provider_key):
                raise ValueError(f"API key not configured for provider: {provider}")
            
            return {
                "api_key": provider_doc[provider_key],
                "model": model
            }
            
        except Exception as e:
            logger.error(f"Error getting provider config: {str(e)}")
            raise
    
    async def _save_project_memory(self, project_memory: ProjectMemory):
        """Save project memory to database"""
        try:
            ai_projects_collection = self.db.ai_assistant_projects
            
            # Convert to dict for MongoDB storage
            project_doc = asdict(project_memory)
            
            # Convert datetime objects to ISO format
            project_doc["created_at"] = project_memory.created_at.isoformat()
            project_doc["updated_at"] = project_memory.updated_at.isoformat()
            
            # Handle subtasks serialization
            project_doc["subtasks"] = [asdict(task) for task in project_memory.subtasks]
            for task_doc in project_doc["subtasks"]:
                task_doc["created_at"] = task_doc["created_at"].isoformat()
                task_doc["updated_at"] = task_doc["updated_at"].isoformat()
                if task_doc.get("completed_at"):
                    task_doc["completed_at"] = task_doc["completed_at"].isoformat()
            
            await ai_projects_collection.replace_one(
                {"project_id": project_memory.project_id},
                project_doc,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error saving project memory: {str(e)}")
            raise
    
    def _create_default_planning_structure(self, ai_response: str) -> Dict[str, Any]:
        """Create default planning structure if parsing fails"""
        return {
            "tech_stack": {
                "frontend": "React with TypeScript",
                "backend": "FastAPI with Python",
                "database": "PostgreSQL with Redis caching",
                "deployment": "Docker containers with Kubernetes"
            },
            "database_design": {
                "primary_database": "PostgreSQL",
                "caching_layer": "Redis",
                "search_engine": "Elasticsearch",
                "sharding_strategy": "Horizontal partitioning"
            },
            "architecture_decisions": [
                {
                    "decision": "Microservices Architecture",
                    "rationale": "Better scalability and maintainability",
                    "impact": "Enables independent scaling of components"
                }
            ],
            "subtasks": [],
            "deployment_config": {
                "containerization": "Docker",
                "orchestration": "Kubernetes",
                "serverless": "Vercel for frontend"
            },
            "performance_requirements": {
                "response_time": "<200ms",
                "throughput": "10,000 requests/second",
                "availability": "99.9%"
            },
            "raw_response": ai_response
        }