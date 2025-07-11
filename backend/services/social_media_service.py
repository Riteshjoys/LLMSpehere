import uuid
import json
from datetime import datetime
from typing import Dict, Any, List
from fastapi import HTTPException
import httpx
from models.social_media_models import (
    SocialMediaGenerationRequest, 
    SocialMediaGenerationResponse,
    HashtagGenerationRequest,
    PlatformConfig
)
from utils.database import providers_collection, social_media_generations_collection
from utils.template_utils import substitute_variables, extract_response_content

class SocialMediaService:
    # Platform configurations
    PLATFORM_CONFIGS = {
        "twitter": PlatformConfig(
            platform="twitter",
            max_length=280,
            supports_hashtags=True,
            supports_emojis=True,
            supports_mentions=True,
            content_types=["post", "thread", "bio"]
        ),
        "instagram": PlatformConfig(
            platform="instagram",
            max_length=2200,
            supports_hashtags=True,
            supports_emojis=True,
            supports_mentions=True,
            content_types=["post", "story", "caption", "bio"]
        ),
        "linkedin": PlatformConfig(
            platform="linkedin",
            max_length=3000,
            supports_hashtags=True,
            supports_emojis=True,
            supports_mentions=True,
            content_types=["post", "article", "bio"]
        ),
        "facebook": PlatformConfig(
            platform="facebook",
            max_length=63206,
            supports_hashtags=True,
            supports_emojis=True,
            supports_mentions=True,
            content_types=["post", "story", "bio"]
        ),
        "tiktok": PlatformConfig(
            platform="tiktok",
            max_length=150,
            supports_hashtags=True,
            supports_emojis=True,
            supports_mentions=True,
            content_types=["caption", "bio"]
        ),
        "youtube": PlatformConfig(
            platform="youtube",
            max_length=5000,
            supports_hashtags=True,
            supports_emojis=True,
            supports_mentions=False,
            content_types=["description", "title", "bio"]
        )
    }
    
    @staticmethod
    async def generate_social_media_content(request: SocialMediaGenerationRequest, user_id: str) -> Dict[str, Any]:
        """Generate social media content using AI providers"""
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get platform configuration
        platform_config = SocialMediaService.PLATFORM_CONFIGS.get(request.platform)
        if not platform_config:
            raise HTTPException(status_code=400, detail=f"Platform {request.platform} not supported")
        
        # Validate content type for platform
        if request.content_type not in platform_config.content_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Content type {request.content_type} not supported for {request.platform}"
            )
        
        # Set max length based on platform if not specified
        max_length = request.max_length or platform_config.max_length
        
        # Get provider configuration
        provider = providers_collection.find_one({"name": request.provider_name, "is_active": True})
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found or inactive")
        
        # Check if model is supported
        if request.model not in provider["models"]:
            raise HTTPException(status_code=400, detail="Model not supported by this provider")
        
        # Generate optimized prompt
        optimized_prompt = SocialMediaService._create_optimized_prompt(request, platform_config, max_length)
        
        # Generate content
        generated_content = await SocialMediaService._generate_with_provider(
            optimized_prompt, provider, request.model, max_length
        )
        
        # Extract hashtags from content
        hashtags = SocialMediaService._extract_hashtags(generated_content)
        
        # Clean content (remove hashtags if they should be separate)
        clean_content = SocialMediaService._clean_content(generated_content, request.include_hashtags)
        
        # Save generation record
        generation_record = {
            "generation_id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": session_id,
            "provider_name": request.provider_name,
            "model": request.model,
            "platform": request.platform,
            "content_type": request.content_type,
            "prompt": request.prompt,
            "generated_content": clean_content,
            "hashtags": hashtags,
            "parameters": {
                "tone": request.tone,
                "target_audience": request.target_audience,
                "include_hashtags": request.include_hashtags,
                "hashtag_count": request.hashtag_count,
                "max_length": max_length,
                "include_emojis": request.include_emojis,
                "include_call_to_action": request.include_call_to_action
            },
            "created_at": datetime.utcnow(),
            "status": "completed"
        }
        
        social_media_generations_collection.insert_one(generation_record)
        
        return {
            "id": generation_record["generation_id"],
            "session_id": session_id,
            "provider": request.provider_name,
            "model": request.model,
            "platform": request.platform,
            "content_type": request.content_type,
            "content": clean_content,
            "hashtags": hashtags,
            "created_at": generation_record["created_at"],
            "status": "completed"
        }
    
    @staticmethod
    def _create_optimized_prompt(request: SocialMediaGenerationRequest, platform_config: PlatformConfig, max_length: int) -> str:
        """Create optimized prompt for social media content generation"""
        
        # Base prompt template
        prompt_template = f"""Create a {request.content_type} for {request.platform} about: {request.prompt}

Platform Requirements:
- Maximum length: {max_length} characters
- Tone: {request.tone}
- Target audience: {request.target_audience}
- Content type: {request.content_type}
"""
        
        # Add platform-specific instructions
        if platform_config.supports_hashtags and request.include_hashtags:
            prompt_template += f"- Include {request.hashtag_count} relevant hashtags\n"
        
        if platform_config.supports_emojis and request.include_emojis:
            prompt_template += "- Include relevant emojis to make it engaging\n"
        
        if request.include_call_to_action:
            prompt_template += "- Include a compelling call-to-action\n"
        
        # Add platform-specific best practices
        platform_tips = {
            "twitter": "Keep it concise, use relevant hashtags, and encourage engagement",
            "instagram": "Use visual language, include relevant hashtags, and tell a story",
            "linkedin": "Be professional, provide value, and encourage discussion",
            "facebook": "Be conversational, ask questions, and encourage sharing",
            "tiktok": "Be trendy, use popular hashtags, and create viral appeal",
            "youtube": "Be descriptive, use keywords, and explain the value"
        }
        
        if request.platform in platform_tips:
            prompt_template += f"\n{request.platform.capitalize()} Best Practices: {platform_tips[request.platform]}\n"
        
        prompt_template += "\nGenerate the content now:"
        
        return prompt_template
    
    @staticmethod
    async def _generate_with_provider(prompt: str, provider: Dict[str, Any], model: str, max_length: int) -> str:
        """Generate content using custom provider"""
        try:
            # Prepare request variables
            variables = {
                "prompt": prompt,
                "model": model,
                "max_tokens": min(max_length * 2, 4000),  # Rough estimate for tokens
                "temperature": 0.7
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
            raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")
    
    @staticmethod
    def _extract_hashtags(content: str) -> List[str]:
        """Extract hashtags from generated content"""
        import re
        hashtags = re.findall(r'#\w+', content)
        return [tag.lower() for tag in hashtags]
    
    @staticmethod
    def _clean_content(content: str, include_hashtags: bool) -> str:
        """Clean content by removing hashtags if they should be separate"""
        if not include_hashtags:
            import re
            # Remove hashtags from content
            content = re.sub(r'#\w+', '', content)
            # Clean up extra whitespace
            content = ' '.join(content.split())
        
        return content.strip()
    
    @staticmethod
    async def generate_hashtags(request: HashtagGenerationRequest, user_id: str) -> Dict[str, Any]:
        """Generate hashtags for a specific topic and platform"""
        # Get a text provider for hashtag generation
        provider = providers_collection.find_one({"provider_type": "text", "is_active": True})
        if not provider:
            raise HTTPException(status_code=404, detail="No text provider available for hashtag generation")
        
        # Create hashtag generation prompt
        prompt = f"""Generate {request.count} relevant hashtags for {request.platform} about: {request.topic}

Requirements:
- Platform: {request.platform}
- Topic: {request.topic}
- Number of hashtags: {request.count}
"""
        
        if request.niche:
            prompt += f"- Niche: {request.niche}\n"
        
        if request.trending:
            prompt += "- Include trending hashtags when possible\n"
        
        prompt += """
Return only the hashtags, one per line, starting with #
Do not include any other text or explanations.
"""
        
        # Generate hashtags
        try:
            variables = {
                "prompt": prompt,
                "model": provider["models"][0],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            request_body = substitute_variables(provider["request_body_template"], variables)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    provider["base_url"],
                    json=request_body,
                    headers=provider["headers"],
                    timeout=30.0
                )
                response.raise_for_status()
                response_data = response.json()
            
            generated_text = extract_response_content(response_data, provider["response_parser"])
            
            # Extract hashtags from generated text
            hashtags = SocialMediaService._extract_hashtags(generated_text)
            
            return {
                "hashtags": hashtags,
                "topic": request.topic,
                "platform": request.platform,
                "count": len(hashtags)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Hashtag generation failed: {str(e)}")
    
    @staticmethod
    async def get_user_social_media_generations(user_id: str, platform: str = None) -> Dict[str, Any]:
        """Get user's social media generations"""
        query = {"user_id": user_id}
        if platform:
            query["platform"] = platform
        
        generations = list(social_media_generations_collection.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(50))
        
        return {"generations": generations}
    
    @staticmethod
    async def get_social_media_templates(platform: str = None, content_type: str = None) -> Dict[str, Any]:
        """Get social media content templates"""
        templates = {
            "twitter": {
                "post": [
                    "🚀 {topic} tip: {content} What's your experience? #TwitterTip",
                    "Breaking: {content} 📈 Thoughts? #News #Trending",
                    "📊 Quick poll: {content} Vote below! 👇"
                ],
                "thread": [
                    "🧵 Thread: Everything you need to know about {topic} (1/n)",
                    "💡 {topic} breakdown: Let me explain this step by step (1/n)"
                ]
            },
            "instagram": {
                "post": [
                    "✨ {content} 💫\n\n{cta} \n\n#Instagram #Content #Inspiration",
                    "🌟 {topic} vibes ✨\n\n{content}\n\n#Aesthetic #Lifestyle #Inspiration"
                ],
                "story": [
                    "📱 Story: {content} Swipe up for more! 👆",
                    "🔥 {topic} alert! {content} 💯"
                ]
            },
            "linkedin": {
                "post": [
                    "💼 Professional insight: {content}\n\nWhat's your take on this? #LinkedIn #Professional",
                    "🎯 {topic} strategy: {content}\n\nLet's discuss in the comments! #Strategy #Business"
                ]
            }
        }
        
        if platform and content_type:
            return {"templates": templates.get(platform, {}).get(content_type, [])}
        elif platform:
            return {"templates": templates.get(platform, {})}
        else:
            return {"templates": templates}
    
    @staticmethod
    async def get_platform_configs() -> Dict[str, Any]:
        """Get all platform configurations"""
        return {
            "platforms": {
                platform: config.dict() 
                for platform, config in SocialMediaService.PLATFORM_CONFIGS.items()
            }
        }
    
    @staticmethod
    async def get_social_media_analytics(user_id: str, platform: str = None) -> Dict[str, Any]:
        """Get social media content analytics"""
        query = {"user_id": user_id}
        if platform:
            query["platform"] = platform
        
        # Total generations
        total_generations = social_media_generations_collection.count_documents(query)
        
        # Generations by platform
        platform_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$platform", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        platform_stats = []
        for doc in social_media_generations_collection.aggregate(platform_pipeline):
            platform_stats.append({
                "platform": doc["_id"],
                "count": doc["count"]
            })
        
        # Generations by content type
        content_type_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$content_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        content_type_stats = []
        for doc in social_media_generations_collection.aggregate(content_type_pipeline):
            content_type_stats.append({
                "content_type": doc["_id"],
                "count": doc["count"]
            })
        
        return {
            "total_generations": total_generations,
            "by_platform": platform_stats,
            "by_content_type": content_type_stats
        }