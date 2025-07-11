from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from copy import deepcopy

from utils.database import get_database
from models.generation_models import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowTemplate,
    WorkflowStep, WorkflowStepType, WorkflowStatus
)

class WorkflowService:
    def __init__(self):
        self.db = get_database()
        self.workflows_collection = self.db.workflows
        self.templates_collection = self.db.workflow_templates
        
    async def get_templates(self) -> List[WorkflowTemplate]:
        """Get all available workflow templates"""
        try:
            templates = []
            for template in self.templates_collection.find():
                template["template_id"] = str(template.pop("_id"))
                templates.append(WorkflowTemplate(**template))
            return templates
        except Exception as e:
            print(f"Error getting workflow templates: {e}")
            return []
    
    async def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get a specific workflow template"""
        try:
            template = self.templates_collection.find_one({"_id": template_id})
            if template:
                template["template_id"] = str(template.pop("_id"))
                return WorkflowTemplate(**template)
            return None
        except Exception as e:
            print(f"Error getting workflow template: {e}")
            return None
    
    async def create_from_template(self, template_id: str, user_id: str, variables: Dict[str, Any]) -> Optional[WorkflowResponse]:
        """Create a workflow from a template"""
        try:
            template = await self.get_template(template_id)
            if not template:
                return None
            
            # Create workflow from template
            workflow_data = {
                "name": f"{template.name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "description": template.description,
                "category": template.category,
                "tags": template.tags,
                "steps": [step.dict() for step in template.steps],
                "variables": {**template.variables, **variables},
                "is_template": False,
                "schedule": None
            }
            
            workflow_create = WorkflowCreate(**workflow_data)
            return await self.create_workflow(workflow_create, user_id)
        except Exception as e:
            print(f"Error creating workflow from template: {e}")
            return None
    
    async def create_workflow(self, workflow: WorkflowCreate, user_id: str) -> WorkflowResponse:
        """Create a new workflow"""
        try:
            workflow_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            workflow_data = {
                "_id": workflow_id,
                "name": workflow.name,
                "description": workflow.description,
                "category": workflow.category or "custom",
                "tags": workflow.tags or [],
                "status": WorkflowStatus.DRAFT,
                "steps": [step.dict() for step in workflow.steps],
                "variables": workflow.variables or {},
                "is_template": workflow.is_template or False,
                "schedule": workflow.schedule,
                "created_at": now,
                "updated_at": now,
                "user_id": user_id,
                "executions_count": 0,
                "last_execution_at": None
            }
            
            await self.workflows_collection.insert_one(workflow_data)
            
            return WorkflowResponse(
                workflow_id=workflow_id,
                name=workflow_data["name"],
                description=workflow_data["description"],
                category=workflow_data["category"],
                tags=workflow_data["tags"],
                status=workflow_data["status"],
                steps=[WorkflowStep(**step) for step in workflow_data["steps"]],
                variables=workflow_data["variables"],
                is_template=workflow_data["is_template"],
                schedule=workflow_data["schedule"],
                created_at=workflow_data["created_at"],
                updated_at=workflow_data["updated_at"],
                user_id=workflow_data["user_id"],
                executions_count=workflow_data["executions_count"],
                last_execution_at=workflow_data["last_execution_at"]
            )
        except Exception as e:
            print(f"Error creating workflow: {e}")
            raise
    
    async def get_user_workflows(self, user_id: str, category: str = None, tag: str = None, status: WorkflowStatus = None) -> List[WorkflowResponse]:
        """Get all workflows for a user"""
        try:
            query = {"user_id": user_id}
            
            if category:
                query["category"] = category
            if tag:
                query["tags"] = {"$in": [tag]}
            if status:
                query["status"] = status
            
            workflows = []
            async for workflow in self.workflows_collection.find(query).sort("updated_at", -1):
                workflow["workflow_id"] = str(workflow.pop("_id"))
                workflow["steps"] = [WorkflowStep(**step) for step in workflow["steps"]]
                workflows.append(WorkflowResponse(**workflow))
            
            return workflows
        except Exception as e:
            print(f"Error getting user workflows: {e}")
            return []
    
    async def get_workflow(self, workflow_id: str, user_id: str) -> Optional[WorkflowResponse]:
        """Get a specific workflow"""
        try:
            workflow = await self.workflows_collection.find_one({"_id": workflow_id, "user_id": user_id})
            if workflow:
                workflow["workflow_id"] = str(workflow.pop("_id"))
                workflow["steps"] = [WorkflowStep(**step) for step in workflow["steps"]]
                return WorkflowResponse(**workflow)
            return None
        except Exception as e:
            print(f"Error getting workflow: {e}")
            return None
    
    async def update_workflow(self, workflow_id: str, workflow_update: WorkflowUpdate, user_id: str) -> Optional[WorkflowResponse]:
        """Update a workflow"""
        try:
            update_data = {}
            
            if workflow_update.name is not None:
                update_data["name"] = workflow_update.name
            if workflow_update.description is not None:
                update_data["description"] = workflow_update.description
            if workflow_update.category is not None:
                update_data["category"] = workflow_update.category
            if workflow_update.tags is not None:
                update_data["tags"] = workflow_update.tags
            if workflow_update.steps is not None:
                update_data["steps"] = [step.dict() for step in workflow_update.steps]
            if workflow_update.variables is not None:
                update_data["variables"] = workflow_update.variables
            if workflow_update.is_template is not None:
                update_data["is_template"] = workflow_update.is_template
            if workflow_update.schedule is not None:
                update_data["schedule"] = workflow_update.schedule
            
            update_data["updated_at"] = datetime.now(timezone.utc)
            
            result = await self.workflows_collection.update_one(
                {"_id": workflow_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                return await self.get_workflow(workflow_id, user_id)
            return None
        except Exception as e:
            print(f"Error updating workflow: {e}")
            return None
    
    async def delete_workflow(self, workflow_id: str, user_id: str) -> bool:
        """Delete a workflow"""
        try:
            result = await self.workflows_collection.delete_one({"_id": workflow_id, "user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting workflow: {e}")
            return False
    
    async def duplicate_workflow(self, workflow_id: str, user_id: str) -> Optional[WorkflowResponse]:
        """Duplicate a workflow"""
        try:
            workflow = await self.get_workflow(workflow_id, user_id)
            if not workflow:
                return None
            
            # Create a copy with a new name
            workflow_create = WorkflowCreate(
                name=f"{workflow.name} - Copy",
                description=workflow.description,
                category=workflow.category,
                tags=workflow.tags,
                steps=workflow.steps,
                variables=workflow.variables,
                is_template=False,
                schedule=workflow.schedule
            )
            
            return await self.create_workflow(workflow_create, user_id)
        except Exception as e:
            print(f"Error duplicating workflow: {e}")
            return None
    
    async def initialize_templates(self):
        """Initialize default workflow templates"""
        try:
            # Check if templates already exist
            count = await self.templates_collection.count_documents({})
            if count > 0:
                return
            
            # Create default templates
            templates = [
                {
                    "_id": "content-marketing-pipeline",
                    "name": "Content Marketing Pipeline",
                    "description": "Generate blog post, create social media posts, and generate promotional images",
                    "category": "marketing",
                    "tags": ["marketing", "content", "social-media"],
                    "steps": [
                        {
                            "step_id": "generate-blog-post",
                            "step_type": "text_generation",
                            "name": "Generate Blog Post",
                            "description": "Create a comprehensive blog post",
                            "provider": "openai",
                            "model": "gpt-4",
                            "prompt_template": "Write a comprehensive blog post about {topic}. Make it engaging and informative.",
                            "settings": {"max_tokens": 2000, "temperature": 0.7},
                            "depends_on": [],
                            "order": 1
                        },
                        {
                            "step_id": "create-social-posts",
                            "step_type": "social_media_generation",
                            "name": "Create Social Media Posts",
                            "description": "Generate social media posts based on the blog post",
                            "provider": "openai",
                            "model": "gpt-4",
                            "prompt_template": "Based on this blog post: {previous_output}, create engaging social media posts for Twitter, LinkedIn, and Facebook.",
                            "settings": {"platform": "twitter", "tone": "professional"},
                            "depends_on": ["generate-blog-post"],
                            "order": 2
                        },
                        {
                            "step_id": "generate-promotional-image",
                            "step_type": "image_generation",
                            "name": "Generate Promotional Image",
                            "description": "Create a promotional image for the content",
                            "provider": "openai",
                            "model": "dall-e-3",
                            "prompt_template": "Create a professional promotional image for a blog post about {topic}. Make it visually appealing and relevant.",
                            "settings": {"number_of_images": 1},
                            "depends_on": [],
                            "order": 3
                        }
                    ],
                    "variables": {
                        "topic": "Enter your blog post topic"
                    }
                },
                {
                    "_id": "product-launch-workflow",
                    "name": "Product Launch Workflow",
                    "description": "Complete product launch content creation workflow",
                    "category": "product",
                    "tags": ["product", "launch", "marketing"],
                    "steps": [
                        {
                            "step_id": "product-description",
                            "step_type": "text_generation",
                            "name": "Product Description",
                            "description": "Create compelling product description",
                            "provider": "openai",
                            "model": "gpt-4",
                            "prompt_template": "Write a compelling product description for {product_name}. Features: {features}. Target audience: {target_audience}.",
                            "settings": {"max_tokens": 1000, "temperature": 0.7},
                            "depends_on": [],
                            "order": 1
                        },
                        {
                            "step_id": "marketing-copy",
                            "step_type": "text_generation",
                            "name": "Marketing Copy",
                            "description": "Create marketing copy for various channels",
                            "provider": "openai",
                            "model": "gpt-4",
                            "prompt_template": "Based on this product description: {previous_output}, create marketing copy for email campaigns, website, and ads.",
                            "settings": {"max_tokens": 1500, "temperature": 0.8},
                            "depends_on": ["product-description"],
                            "order": 2
                        },
                        {
                            "step_id": "promotional-video",
                            "step_type": "video_generation",
                            "name": "Promotional Video",
                            "description": "Generate a promotional video",
                            "provider": "luma",
                            "model": "luma-dream-machine",
                            "prompt_template": "Create a promotional video showcasing {product_name}. Make it engaging and highlight key features.",
                            "settings": {"duration": 10, "aspect_ratio": "16:9"},
                            "depends_on": [],
                            "order": 3
                        }
                    ],
                    "variables": {
                        "product_name": "Enter product name",
                        "features": "List key features",
                        "target_audience": "Describe target audience"
                    }
                },
                {
                    "_id": "code-documentation-workflow",
                    "name": "Code Documentation Workflow",
                    "description": "Generate comprehensive code documentation and tests",
                    "category": "development",
                    "tags": ["code", "documentation", "development"],
                    "steps": [
                        {
                            "step_id": "generate-docs",
                            "step_type": "code_generation",
                            "name": "Generate Documentation",
                            "description": "Create comprehensive code documentation",
                            "provider": "openai",
                            "model": "gpt-4",
                            "prompt_template": "Generate comprehensive documentation for this {language} code: {code}",
                            "settings": {"request_type": "documentation", "language": "python"},
                            "depends_on": [],
                            "order": 1
                        },
                        {
                            "step_id": "generate-tests",
                            "step_type": "code_generation",
                            "name": "Generate Tests",
                            "description": "Create unit tests for the code",
                            "provider": "openai",
                            "model": "gpt-4",
                            "prompt_template": "Generate comprehensive unit tests for this {language} code: {code}",
                            "settings": {"request_type": "test", "language": "python"},
                            "depends_on": [],
                            "order": 2
                        }
                    ],
                    "variables": {
                        "code": "Paste your code here",
                        "language": "Programming language"
                    }
                }
            ]
            
            await self.templates_collection.insert_many(templates)
            print("Workflow templates initialized successfully")
        except Exception as e:
            print(f"Error initializing workflow templates: {e}")