import uuid
import base64
from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException
import httpx
import fal_client
from models.generation_models import ImageGenerationRequest
from utils.database import providers_collection, image_generations_collection
from utils.template_utils import substitute_variables, extract_response_content
from utils.config import OPENAI_API_KEY, FAL_API_KEY
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

class ImageGenerationService:
    @staticmethod
    async def generate_image(request: ImageGenerationRequest, user_id: str) -> Dict[str, Any]:
        """Generate image using various providers"""
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        image_base64 = None
        
        # Handle built-in providers
        if request.provider_name == "openai" and OPENAI_API_KEY:
            image_base64 = await ImageGenerationService._generate_with_openai(request)
        
        elif request.provider_name == "fal" and FAL_API_KEY:
            image_base64 = await ImageGenerationService._generate_with_fal(request)
        
        else:
            # Custom provider from database
            provider = providers_collection.find_one({
                "name": request.provider_name, 
                "is_active": True, 
                "provider_type": "image"
            })
            
            if not provider:
                raise HTTPException(status_code=404, detail="Image provider not found or inactive")
            
            # Check if model is supported
            if request.model not in provider["models"]:
                raise HTTPException(status_code=400, detail="Model not supported by this provider")
            
            image_base64 = await ImageGenerationService._generate_with_custom_provider(request, provider)
        
        if not image_base64:
            raise HTTPException(status_code=500, detail="Failed to generate image")
        
        # Save generation record
        generation_record = {
            "generation_id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": session_id,
            "provider_name": request.provider_name,
            "model": request.model,
            "prompt": request.prompt,
            "image_base64": image_base64,
            "parameters": {
                "number_of_images": request.number_of_images
            },
            "created_at": datetime.utcnow()
        }
        
        image_generations_collection.insert_one(generation_record)
        
        return {
            "image_base64": image_base64,
            "session_id": session_id,
            "provider": request.provider_name,
            "model": request.model,
            "prompt": request.prompt
        }
    
    @staticmethod
    async def _generate_with_openai(request: ImageGenerationRequest) -> str:
        """Generate image using OpenAI DALL-E via emergentintegrations"""
        try:
            image_gen = OpenAIImageGeneration(api_key=OPENAI_API_KEY)
            images = await image_gen.generate_images(
                prompt=request.prompt,
                model=request.model,
                number_of_images=request.number_of_images
            )
            
            if images and len(images) > 0:
                return base64.b64encode(images[0]).decode('utf-8')
            else:
                raise HTTPException(status_code=500, detail="No image was generated")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    
    @staticmethod
    async def _generate_with_fal(request: ImageGenerationRequest) -> str:
        """Generate image using fal.ai Stable Diffusion"""
        try:
            handler = await fal_client.submit_async(
                "fal-ai/flux/dev",
                arguments={"prompt": request.prompt}
            )
            result = await handler.get()
            
            if result and result.get("images") and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]
                
                # Download image and convert to base64
                async with httpx.AsyncClient() as client:
                    img_response = await client.get(image_url)
                    img_response.raise_for_status()
                    return base64.b64encode(img_response.content).decode('utf-8')
            else:
                raise HTTPException(status_code=500, detail="No image was generated")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"FAL API error: {str(e)}")
    
    @staticmethod
    async def _generate_with_custom_provider(request: ImageGenerationRequest, provider: Dict[str, Any]) -> str:
        """Generate image using custom provider"""
        try:
            # Prepare request variables
            variables = {
                "prompt": request.prompt,
                "model": request.model,
                "number_of_images": request.number_of_images
            }
            
            # Substitute variables in request template
            request_body = substitute_variables(provider["request_body_template"], variables)
            
            # Make API call
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    provider["base_url"],
                    json=request_body,
                    headers=provider["headers"],
                    timeout=60.0
                )
                response.raise_for_status()
                response_data = response.json()
            
            # Extract image URL and convert to base64
            image_url = extract_response_content(response_data, provider["response_parser"])
            
            if image_url:
                async with httpx.AsyncClient() as client:
                    img_response = await client.get(image_url)
                    img_response.raise_for_status()
                    return base64.b64encode(img_response.content).decode('utf-8')
            else:
                raise HTTPException(status_code=500, detail="No image URL found in response")
                
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"API error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
    
    @staticmethod
    async def get_user_image_generations(user_id: str) -> Dict[str, Any]:
        """Get user image generations"""
        generations = list(image_generations_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).limit(50))
        
        return {"generations": generations}