import uuid
import base64
import asyncio
from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException
import httpx
from models.generation_models import VideoGenerationRequest
from utils.database import providers_collection, video_generations_collection
from utils.template_utils import substitute_variables, extract_response_content
from utils.config import LUMA_API_KEY, PIKA_API_KEY

class VideoGenerationService:
    @staticmethod
    async def generate_video(request: VideoGenerationRequest, user_id: str) -> Dict[str, Any]:
        """Generate video using various providers"""
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        video_url = None
        video_base64 = None
        
        # Handle built-in providers
        if request.provider_name == "luma" and LUMA_API_KEY:
            video_url = await VideoGenerationService._generate_with_luma(request)
        
        elif request.provider_name == "pika" and PIKA_API_KEY:
            video_url = await VideoGenerationService._generate_with_pika(request)
        
        else:
            # Custom provider from database
            provider = providers_collection.find_one({
                "name": request.provider_name, 
                "is_active": True, 
                "provider_type": "video"
            })
            
            if not provider:
                raise HTTPException(status_code=404, detail="Video provider not found or inactive")
            
            # Check if model is supported
            if request.model not in provider["models"]:
                raise HTTPException(status_code=400, detail="Model not supported by this provider")
            
            video_url = await VideoGenerationService._generate_with_custom_provider(request, provider)
        
        if not video_url:
            raise HTTPException(status_code=500, detail="No video URL found in response")
        
        # Download video and convert to base64 for storage
        if video_url:
            async with httpx.AsyncClient() as client:
                video_response = await client.get(video_url, timeout=300.0)  # 5 min timeout
                video_response.raise_for_status()
                video_base64 = base64.b64encode(video_response.content).decode('utf-8')
        
        # Save generation record
        generation_record = {
            "generation_id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": session_id,
            "provider_name": request.provider_name,
            "model": request.model,
            "prompt": request.prompt,
            "video_base64": video_base64,
            "video_url": video_url,
            "parameters": {
                "duration": request.duration,
                "aspect_ratio": request.aspect_ratio,
                "resolution": request.resolution
            },
            "created_at": datetime.utcnow()
        }
        
        video_generations_collection.insert_one(generation_record)
        
        return {
            "video_base64": video_base64,
            "video_url": video_url,
            "session_id": session_id,
            "provider": request.provider_name,
            "model": request.model,
            "prompt": request.prompt
        }
    
    @staticmethod
    async def _generate_with_luma(request: VideoGenerationRequest) -> str:
        """Generate video using Luma AI Dream Machine"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.lumalabs.ai/dream-machine/v1/generations/video",
                    headers={
                        "Authorization": f"Bearer {LUMA_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "prompt": request.prompt,
                        "aspect_ratio": request.aspect_ratio,
                        "duration": f"{request.duration}s"
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                generation_id = result.get("id")
                
                # Poll for completion (simplified - in production, use webhooks)
                if generation_id:
                    for i in range(60):  # Poll for up to 5 minutes
                        await asyncio.sleep(5)
                        status_response = await client.get(
                            f"https://api.lumalabs.ai/dream-machine/v1/generations/{generation_id}",
                            headers={"Authorization": f"Bearer {LUMA_API_KEY}"}
                        )
                        status_response.raise_for_status()
                        status_result = status_response.json()
                        
                        if status_result.get("state") == "completed":
                            return status_result.get("assets", {}).get("video")
                        elif status_result.get("state") == "failed":
                            raise HTTPException(status_code=500, detail="Video generation failed")
                
                raise HTTPException(status_code=500, detail="Video generation timeout")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Luma API error: {str(e)}")
    
    @staticmethod
    async def _generate_with_pika(request: VideoGenerationRequest) -> str:
        """Generate video using Pika Labs"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://app.ai4chat.co/api/v1/video/generate",
                    headers={
                        "Authorization": f"Bearer {PIKA_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "prompt": request.prompt,
                        "aspectRatio": request.aspect_ratio,
                        "model": request.model,
                        "img2video": False
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                return result.get("video_url")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Pika API error: {str(e)}")
    
    @staticmethod
    async def _generate_with_custom_provider(request: VideoGenerationRequest, provider: Dict[str, Any]) -> str:
        """Generate video using custom provider"""
        try:
            # Prepare request variables
            variables = {
                "prompt": request.prompt,
                "model": request.model,
                "duration": request.duration,
                "aspect_ratio": request.aspect_ratio,
                "resolution": request.resolution
            }
            
            # Substitute variables in request template
            request_body = substitute_variables(provider["request_body_template"], variables)
            
            # Make API call
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    provider["base_url"],
                    json=request_body,
                    headers=provider["headers"],
                    timeout=120.0  # Longer timeout for video generation
                )
                response.raise_for_status()
                response_data = response.json()
            
            # Extract video URL
            return extract_response_content(response_data, provider["response_parser"])
            
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"API error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")
    
    @staticmethod
    async def get_user_video_generations(user_id: str) -> Dict[str, Any]:
        """Get user video generations"""
        generations = list(video_generations_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).limit(50))
        
        return {"generations": generations}