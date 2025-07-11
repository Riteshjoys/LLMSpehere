import uuid
from datetime import datetime
from utils.database import users_collection, providers_collection
from utils.auth_utils import get_password_hash
from services.workflow_service import WorkflowService

async def initialize_default_data():
    """Initialize default providers and admin user if they don't exist"""
    
    # Check if admin user exists
    admin_user = users_collection.find_one({"username": "admin"})
    if not admin_user:
        # Create admin user
        hashed_password = get_password_hash("admin123")
        admin_doc = {
            "user_id": str(uuid.uuid4()),
            "username": "admin",
            "email": "admin@contentforge.ai",
            "hashed_password": hashed_password,
            "is_admin": True,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        users_collection.insert_one(admin_doc)
    
    # Default text providers
    default_text_providers = [
        {
            "provider_id": "openai-text-default",
            "name": "OpenAI",
            "description": "OpenAI GPT models for text generation",
            "base_url": "https://api.openai.com/v1/chat/completions",
            "headers": {"Authorization": "Bearer YOUR_OPENAI_API_KEY", "Content-Type": "application/json"},
            "request_body_template": {
                "model": "{model}",
                "messages": [{"role": "user", "content": "{prompt}"}],
                "max_tokens": "{max_tokens}",
                "temperature": "{temperature}"
            },
            "response_parser": {"content_path": "choices.0.message.content"},
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
            "provider_type": "text",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "created_by": "system"
        },
        {
            "provider_id": "groq-text-default",
            "name": "groq",
            "description": "Groq fast inference for text generation",
            "base_url": "https://api.groq.com/openai/v1/chat/completions",
            "headers": {"Authorization": "Bearer YOUR_GROQ_API_KEY", "Content-Type": "application/json"},
            "request_body_template": {
                "model": "{model}",
                "messages": [{"role": "user", "content": "{prompt}"}],
                "max_tokens": "{max_tokens}",
                "temperature": "{temperature}"
            },
            "response_parser": {"content_path": "choices.0.message.content"},
            "models": ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
            "provider_type": "text",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "created_by": "system"
        },
        {
            "provider_id": "claude-text-default",
            "name": "Claude",
            "description": "Anthropic Claude models for text generation",
            "base_url": "https://api.anthropic.com/v1/messages",
            "headers": {"x-api-key": "YOUR_ANTHROPIC_API_KEY", "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            "request_body_template": {
                "model": "{model}",
                "max_tokens": "{max_tokens}",
                "messages": [{"role": "user", "content": "{prompt}"}]
            },
            "response_parser": {"content_path": "content.0.text"},
            "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
            "provider_type": "text",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "created_by": "system"
        },
        {
            "provider_id": "gemini-text-default",
            "name": "Gemini",
            "description": "Google Gemini models for text generation",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            "headers": {"Content-Type": "application/json"},
            "request_body_template": {
                "contents": [{"parts": [{"text": "{prompt}"}]}],
                "generationConfig": {"temperature": "{temperature}", "maxOutputTokens": "{max_tokens}"}
            },
            "response_parser": {"content_path": "candidates.0.content.parts.0.text"},
            "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
            "provider_type": "text",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "created_by": "system"
        }
    ]
    
    # Default image providers
    default_image_providers = [
        {
            "provider_id": "openai-image-default",
            "name": "openai",
            "description": "OpenAI DALL-E for image generation",
            "base_url": "https://api.openai.com/v1/images/generations",
            "headers": {"Authorization": "Bearer YOUR_OPENAI_API_KEY", "Content-Type": "application/json"},
            "request_body_template": {
                "prompt": "{prompt}",
                "model": "{model}",
                "n": "{number_of_images}",
                "size": "1024x1024"
            },
            "response_parser": {"content_path": "data.0.url"},
            "models": ["gpt-image-1"],
            "provider_type": "image",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "created_by": "system"
        },
        {
            "provider_id": "fal-image-default",
            "name": "fal",
            "description": "Stable Diffusion via fal.ai for image generation",
            "base_url": "https://fal.run/fal-ai/flux/dev",
            "headers": {"Authorization": "Key YOUR_FAL_API_KEY", "Content-Type": "application/json"},
            "request_body_template": {
                "prompt": "{prompt}",
                "num_images": "{number_of_images}"
            },
            "response_parser": {"content_path": "images.0.url"},
            "models": ["flux-dev", "flux-schnell", "flux-pro"],
            "provider_type": "image",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "created_by": "system"
        }
    ]
    
    # Default video providers
    default_video_providers = [
        {
            "provider_id": "luma-video-default",
            "name": "luma",
            "description": "Luma AI Dream Machine for video generation",
            "base_url": "https://api.lumalabs.ai/dream-machine/v1/generations/video",
            "headers": {"Authorization": "Bearer YOUR_LUMA_API_KEY", "Content-Type": "application/json"},
            "request_body_template": {
                "prompt": "{prompt}",
                "aspect_ratio": "{aspect_ratio}",
                "duration": "{duration}s"
            },
            "response_parser": {"content_path": "assets.video"},
            "models": ["luma-dream-machine"],
            "provider_type": "video",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "created_by": "system"
        },
        {
            "provider_id": "pika-video-default",
            "name": "pika",
            "description": "Pika Labs for video generation",
            "base_url": "https://app.ai4chat.co/api/v1/video/generate",
            "headers": {"Authorization": "Bearer YOUR_PIKA_API_KEY", "Content-Type": "application/json"},
            "request_body_template": {
                "prompt": "{prompt}",
                "aspectRatio": "{aspect_ratio}",
                "model": "{model}",
                "img2video": False
            },
            "response_parser": {"content_path": "video_url"},
            "models": ["pika-1.0", "pika-1.5"],
            "provider_type": "video",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "created_by": "system"
        }
    ]
    
    # Insert default providers if they don't exist
    for provider in default_text_providers + default_image_providers + default_video_providers:
        if not providers_collection.find_one({"provider_id": provider["provider_id"]}):
            providers_collection.insert_one(provider)
    
    # Initialize workflow templates
    workflow_service = WorkflowService()
    await workflow_service.initialize_templates()