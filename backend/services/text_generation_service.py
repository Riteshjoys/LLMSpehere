import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException
import httpx
from groq import Groq
from models.generation_models import TextGenerationRequest
from utils.database import providers_collection, conversations_collection, generations_collection
from utils.template_utils import substitute_variables, extract_response_content
from utils.config import GROQ_API_KEY

class TextGenerationService:
    @staticmethod
    async def generate_text(request: TextGenerationRequest, user_id: str) -> Dict[str, Any]:
        """Generate text using various providers"""
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get conversation history
        conversation = conversations_collection.find_one({"session_id": session_id})
        if not conversation:
            conversation = {
                "session_id": session_id,
                "user_id": user_id,
                "messages": [],
                "created_at": datetime.utcnow()
            }
            conversations_collection.insert_one(conversation)
        
        generated_content = None
        
        # Handle built-in providers
        if request.provider_name == "groq" and GROQ_API_KEY:
            generated_content = await TextGenerationService._generate_with_groq(request, conversation)
        
        else:
            # Get provider configuration from database
            provider = providers_collection.find_one({"name": request.provider_name, "is_active": True})
            if not provider:
                raise HTTPException(status_code=404, detail="Provider not found or inactive")
            
            # Check if model is supported
            if request.model not in provider["models"]:
                raise HTTPException(status_code=400, detail="Model not supported by this provider")
            
            generated_content = await TextGenerationService._generate_with_custom_provider(
                request, provider, conversation
            )
        
        if not generated_content:
            raise HTTPException(status_code=500, detail="Failed to generate text")
        
        # Update conversation
        user_message = {"role": "user", "content": request.prompt, "timestamp": datetime.utcnow()}
        assistant_message = {"role": "assistant", "content": generated_content, "timestamp": datetime.utcnow()}
        
        conversations_collection.update_one(
            {"session_id": session_id},
            {"$push": {"messages": {"$each": [user_message, assistant_message]}}}
        )
        
        # Save generation record
        generation_record = {
            "generation_id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": session_id,
            "provider_name": request.provider_name,
            "model": request.model,
            "prompt": request.prompt,
            "generated_content": generated_content,
            "parameters": {
                "max_tokens": request.max_tokens,
                "temperature": request.temperature
            },
            "created_at": datetime.utcnow()
        }
        
        generations_collection.insert_one(generation_record)
        
        return {
            "generated_content": generated_content,
            "session_id": session_id,
            "provider": request.provider_name,
            "model": request.model
        }
    
    @staticmethod
    async def _generate_with_groq(request: TextGenerationRequest, conversation: Dict[str, Any]) -> str:
        """Generate text using Groq API"""
        try:
            client = Groq(api_key=GROQ_API_KEY)
            
            # Prepare messages for conversation
            messages = [{"role": msg["role"], "content": msg["content"]} for msg in conversation["messages"]]
            messages.append({"role": "user", "content": request.prompt})
            
            # Make API call
            chat_completion = client.chat.completions.create(
                messages=messages,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")
    
    @staticmethod
    async def _generate_with_custom_provider(
        request: TextGenerationRequest, 
        provider: Dict[str, Any], 
        conversation: Dict[str, Any]
    ) -> str:
        """Generate text using custom provider"""
        try:
            # Prepare request variables
            variables = {
                "prompt": request.prompt,
                "model": request.model,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "messages": conversation["messages"]
            }
            
            # Substitute variables in request template
            request_body = substitute_variables(provider["request_body_template"], variables)
            
            # Make API call
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    provider["base_url"],
                    json=request_body,
                    headers=provider["headers"],
                    timeout=30.0
                )
                response.raise_for_status()
                response_data = response.json()
            
            # Extract content using parser
            return extract_response_content(response_data, provider["response_parser"])
            
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"API error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
    
    @staticmethod
    async def get_conversation(session_id: str, user_id: str) -> Dict[str, Any]:
        """Get conversation by session ID"""
        conversation = conversations_collection.find_one(
            {"session_id": session_id, "user_id": user_id},
            {"_id": 0}
        )
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return conversation
    
    @staticmethod
    async def get_user_conversations(user_id: str) -> Dict[str, Any]:
        """Get all user conversations"""
        conversations = list(conversations_collection.find(
            {"user_id": user_id},
            {"_id": 0, "session_id": 1, "created_at": 1}
        ).sort("created_at", -1))
        
        return {"conversations": conversations}
    
    @staticmethod
    async def get_user_generations(user_id: str) -> Dict[str, Any]:
        """Get user text generations"""
        generations = list(generations_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).limit(50))
        
        return {"generations": generations}