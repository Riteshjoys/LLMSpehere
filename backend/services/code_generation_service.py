import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from emergentintegrations.llm.chat import LlmChat, UserMessage
from utils.database import db
from models.generation_models import CodeGenerationRequest, CodeGenerationResponse
import logging

logger = logging.getLogger(__name__)

class CodeGenerationService:
    def __init__(self):
        self.db = db
    
    async def generate_code(self, request: CodeGenerationRequest, user_id: str) -> CodeGenerationResponse:
        """
        Generate code based on the request type and content
        """
        try:
            # Get provider configuration
            provider_config = await self._get_provider_config(request.provider, request.model)
            
            # Create system message based on request type
            system_message = self._create_system_message(request.request_type, request.language)
            
            # Create chat instance
            session_id = str(uuid.uuid4())
            chat = LlmChat(
                api_key=provider_config["api_key"],
                session_id=session_id,
                system_message=system_message
            ).with_model(request.provider, request.model)
            
            if request.max_tokens:
                chat.with_max_tokens(request.max_tokens)
            
            # Create user message
            user_message = UserMessage(text=request.prompt)
            
            # Send message and get response
            response = await chat.send_message(user_message)
            
            # Create response object
            generation_response = CodeGenerationResponse(
                id=str(uuid.uuid4()),
                session_id=session_id,
                provider=request.provider,
                model=request.model,
                request_type=request.request_type,
                language=request.language,
                prompt=request.prompt,
                response=response,
                user_id=user_id,
                created_at=datetime.utcnow(),
                status="completed"
            )
            
            # Save to database
            await self._save_generation(generation_response)
            
            return generation_response
            
        except Exception as e:
            logger.error(f"Error in code generation: {str(e)}")
            # Return error response
            return CodeGenerationResponse(
                id=str(uuid.uuid4()),
                session_id="",
                provider=request.provider,
                model=request.model,
                request_type=request.request_type,
                language=request.language,
                prompt=request.prompt,
                response=f"Error: {str(e)}",
                user_id=user_id,
                created_at=datetime.utcnow(),
                status="error"
            )
    
    def _create_system_message(self, request_type: str, language: str) -> str:
        """
        Create system message based on request type and programming language
        """
        base_message = f"You are an expert software developer and code generation assistant specializing in {language}. "
        
        type_specific_messages = {
            "generate": f"Generate clean, efficient, and well-documented {language} code based on user requirements. Include comments and follow best practices.",
            "debug": f"Debug and fix {language} code. Identify issues, explain what's wrong, and provide corrected code with explanations.",
            "optimize": f"Optimize {language} code for performance, readability, and maintainability. Explain the optimizations made.",
            "refactor": f"Refactor {language} code to improve structure, readability, and maintainability while preserving functionality.",
            "review": f"Review {language} code and provide constructive feedback, suggestions for improvements, and identify potential issues.",
            "documentation": f"Generate comprehensive documentation for {language} code including docstrings, comments, and usage examples.",
            "test": f"Generate unit tests for {language} code using appropriate testing frameworks and best practices.",
            "explain": f"Explain {language} code in detail, including how it works, its purpose, and any complex logic or algorithms used.",
            "architecture": f"Provide architectural guidance and design patterns for {language} applications. Focus on scalability and maintainability."
        }
        
        return base_message + type_specific_messages.get(request_type, type_specific_messages["generate"])
    
    async def _get_provider_config(self, provider: str, model: str) -> Dict[str, Any]:
        """
        Get provider configuration from database
        """
        providers_collection = self.db.providers
        
        # Map provider names to database keys
        provider_mapping = {
            "openai": "openai_api_key",
            "anthropic": "anthropic_api_key", 
            "gemini": "gemini_api_key"
        }
        
        provider_key = provider_mapping.get(provider)
        if not provider_key:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Get provider from database
        provider_doc = await providers_collection.find_one({"provider": provider})
        
        if not provider_doc or not provider_doc.get(provider_key):
            raise ValueError(f"API key not configured for provider: {provider}")
        
        return {
            "api_key": provider_doc[provider_key],
            "model": model
        }
    
    async def _save_generation(self, generation: CodeGenerationResponse):
        """
        Save code generation to database
        """
        try:
            code_generations_collection = self.db.code_generations
            
            generation_doc = {
                "id": generation.id,
                "session_id": generation.session_id,
                "provider": generation.provider,
                "model": generation.model,
                "request_type": generation.request_type,
                "language": generation.language,
                "prompt": generation.prompt,
                "response": generation.response,
                "user_id": generation.user_id,
                "created_at": generation.created_at,
                "status": generation.status
            }
            
            await code_generations_collection.insert_one(generation_doc)
            
        except Exception as e:
            logger.error(f"Error saving code generation: {str(e)}")
    
    async def get_user_code_generations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get user's code generation history
        """
        try:
            code_generations_collection = self.db.code_generations
            
            cursor = code_generations_collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit)
            
            generations = []
            async for doc in cursor:
                # Convert ObjectId to string
                doc["_id"] = str(doc["_id"])
                generations.append(doc)
            
            return generations
            
        except Exception as e:
            logger.error(f"Error retrieving code generations: {str(e)}")
            return []
    
    async def get_code_generation_by_id(self, generation_id: str, user_id: str) -> Optional[Dict]:
        """
        Get specific code generation by ID
        """
        try:
            code_generations_collection = self.db.code_generations
            
            doc = await code_generations_collection.find_one({
                "id": generation_id,
                "user_id": user_id
            })
            
            if doc:
                doc["_id"] = str(doc["_id"])
                return doc
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving code generation: {str(e)}")
            return None
    
    async def get_available_providers(self) -> List[Dict]:
        """
        Get available code generation providers and models
        """
        return [
            {
                "provider": "openai",
                "name": "OpenAI GPT-4",
                "models": [
                    {"id": "gpt-4o", "name": "GPT-4o", "description": "Latest GPT-4 model, excellent for code generation"},
                    {"id": "gpt-4.1", "name": "GPT-4.1", "description": "Enhanced GPT-4 with improved reasoning"},
                    {"id": "o1-mini", "name": "o1-mini", "description": "Optimized for code tasks"},
                    {"id": "o3-mini", "name": "o3-mini", "description": "Fast and efficient for code generation"}
                ]
            },
            {
                "provider": "anthropic",
                "name": "Anthropic Claude",
                "models": [
                    {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4", "description": "Great for code analysis and debugging"},
                    {"id": "claude-opus-4-20250514", "name": "Claude Opus 4", "description": "Most capable for complex code tasks"}
                ]
            },
            {
                "provider": "gemini",
                "name": "Google Gemini",
                "models": [
                    {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "description": "Fast and efficient for code understanding"},
                    {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "description": "Advanced reasoning for complex code tasks"}
                ]
            }
        ]
    
    async def get_supported_languages(self) -> List[Dict]:
        """
        Get list of supported programming languages
        """
        return [
            {"id": "python", "name": "Python", "extension": ".py"},
            {"id": "javascript", "name": "JavaScript", "extension": ".js"},
            {"id": "typescript", "name": "TypeScript", "extension": ".ts"},
            {"id": "java", "name": "Java", "extension": ".java"},
            {"id": "cpp", "name": "C++", "extension": ".cpp"},
            {"id": "csharp", "name": "C#", "extension": ".cs"},
            {"id": "go", "name": "Go", "extension": ".go"},
            {"id": "rust", "name": "Rust", "extension": ".rs"},
            {"id": "php", "name": "PHP", "extension": ".php"},
            {"id": "ruby", "name": "Ruby", "extension": ".rb"},
            {"id": "swift", "name": "Swift", "extension": ".swift"},
            {"id": "kotlin", "name": "Kotlin", "extension": ".kt"},
            {"id": "html", "name": "HTML", "extension": ".html"},
            {"id": "css", "name": "CSS", "extension": ".css"},
            {"id": "sql", "name": "SQL", "extension": ".sql"},
            {"id": "bash", "name": "Bash", "extension": ".sh"},
            {"id": "powershell", "name": "PowerShell", "extension": ".ps1"},
            {"id": "r", "name": "R", "extension": ".r"},
            {"id": "scala", "name": "Scala", "extension": ".scala"},
            {"id": "dart", "name": "Dart", "extension": ".dart"}
        ]
    
    async def get_request_types(self) -> List[Dict]:
        """
        Get available code generation request types
        """
        return [
            {"id": "generate", "name": "Generate Code", "description": "Generate new code from requirements"},
            {"id": "debug", "name": "Debug & Fix", "description": "Debug and fix existing code"},
            {"id": "optimize", "name": "Optimize", "description": "Optimize code for performance"},
            {"id": "refactor", "name": "Refactor", "description": "Refactor code structure"},
            {"id": "review", "name": "Code Review", "description": "Review and suggest improvements"},
            {"id": "documentation", "name": "Documentation", "description": "Generate documentation"},
            {"id": "test", "name": "Unit Tests", "description": "Generate unit tests"},
            {"id": "explain", "name": "Explain Code", "description": "Explain how code works"},
            {"id": "architecture", "name": "Architecture", "description": "Architectural guidance"}
        ]