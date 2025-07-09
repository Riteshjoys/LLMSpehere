from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import json
import os
import base64
import re
import shlex
import fal_client
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import uuid
from decouple import config
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

# Initialize FastAPI app
app = FastAPI(title="ContentForge AI API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = config('MONGO_URL', default='mongodb://localhost:27017/contentforge')
client = MongoClient(MONGO_URL)
db = client.contentforge

# Collections
users_collection = db.users
providers_collection = db.providers
conversations_collection = db.conversations
generations_collection = db.generations
image_generations_collection = db.image_generations
video_generations_collection = db.video_generations

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = config('JWT_SECRET_KEY', default='your-secret-key-here-change-in-production')
ALGORITHM = config('JWT_ALGORITHM', default='HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(config('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', default=30))

# API Keys
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
FAL_API_KEY = config('FAL_API_KEY', default='')
LUMA_API_KEY = config('LUMA_API_KEY', default='')
PIKA_API_KEY = config('PIKA_API_KEY', default='')

# Set fal.ai API key
if FAL_API_KEY:
    os.environ["FAL_KEY"] = FAL_API_KEY

# Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class LLMProvider(BaseModel):
    name: str
    description: str
    base_url: str
    headers: Dict[str, str]
    request_body_template: Dict[str, Any]
    response_parser: Dict[str, str]  # JSONPath expressions to extract response
    models: List[str]
    provider_type: str = "text"  # "text" or "image"
    is_active: bool = True

class CurlProvider(BaseModel):
    name: str
    description: str
    curl_command: str
    models: List[str]
    provider_type: str = "text"  # "text" or "image"
    is_active: bool = True

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

class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime

# Helper functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def parse_curl_command(curl_command: str) -> Dict[str, Any]:
    """Parse curl command and extract URL, headers, and body"""
    try:
        # Remove 'curl' from the beginning
        curl_command = curl_command.strip()
        if curl_command.startswith('curl '):
            curl_command = curl_command[5:]
        
        # Split command into parts
        parts = shlex.split(curl_command)
        
        url = ""
        headers = {}
        body = {}
        method = "GET"
        
        i = 0
        while i < len(parts):
            part = parts[i]
            
            # Extract URL (first non-flag argument)
            if not part.startswith('-') and not url:
                url = part
            
            # Extract headers
            elif part == '-H' or part == '--header':
                if i + 1 < len(parts):
                    header_line = parts[i + 1]
                    if ':' in header_line:
                        key, value = header_line.split(':', 1)
                        headers[key.strip()] = value.strip()
                    i += 1
            
            # Extract method
            elif part == '-X' or part == '--request':
                if i + 1 < len(parts):
                    method = parts[i + 1]
                    i += 1
            
            # Extract body data
            elif part == '-d' or part == '--data':
                if i + 1 < len(parts):
                    try:
                        body = json.loads(parts[i + 1])
                    except json.JSONDecodeError:
                        body = {"data": parts[i + 1]}
                    i += 1
            
            i += 1
        
        # Create request body template with variables
        request_body_template = body.copy() if body else {}
        
        # Replace common prompt fields with variables
        if "prompt" in request_body_template:
            request_body_template["prompt"] = "{prompt}"
        if "message" in request_body_template:
            request_body_template["message"] = "{prompt}"
        if "input" in request_body_template:
            request_body_template["input"] = "{prompt}"
        if "text" in request_body_template:
            request_body_template["text"] = "{prompt}"
        
        # Add common parameters
        if "max_tokens" not in request_body_template:
            request_body_template["max_tokens"] = "{max_tokens}"
        if "temperature" not in request_body_template:
            request_body_template["temperature"] = "{temperature}"
        if "model" not in request_body_template:
            request_body_template["model"] = "{model}"
        
        return {
            "base_url": url,
            "headers": headers,
            "request_body_template": request_body_template,
            "response_parser": {
                "content_path": "choices.0.message.content"  # Default parser
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse curl command: {str(e)}")

def substitute_variables(template: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
    """Substitute variables in request template"""
    template_str = json.dumps(template)
    for key, value in variables.items():
        template_str = template_str.replace(f"{{{key}}}", str(value))
    return json.loads(template_str)

def extract_response_content(response_data: Dict[str, Any], parser_config: Dict[str, str]) -> str:
    """Extract content from API response using parser configuration"""
    try:
        # Simple JSONPath-like extraction
        content_path = parser_config.get("content_path", "choices.0.message.content")
        
        current = response_data
        for key in content_path.split('.'):
            if key.isdigit():
                current = current[int(key)]
            else:
                current = current[key]
        
        return str(current)
    except (KeyError, IndexError, TypeError):
        # Fallback to raw response
        return str(response_data)

# Authentication Routes
@app.post("/api/auth/register")
async def register(user: UserCreate):
    # Check if user exists
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(user.password)
    user_doc = {
        "user_id": str(uuid.uuid4()),
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "is_admin": False,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    users_collection.insert_one(user_doc)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/login")
async def login(user: UserLogin):
    user_doc = users_collection.find_one({"username": user.username})
    
    if not user_doc or not verify_password(user.password, user_doc["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me")
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    user_doc = users_collection.find_one({"username": current_user})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_doc["user_id"],
        "username": user_doc["username"],
        "email": user_doc["email"],
        "is_admin": user_doc.get("is_admin", False),
        "created_at": user_doc["created_at"]
    }

# Provider Management Routes (Admin only)
@app.post("/api/admin/providers")
async def add_provider(provider: LLMProvider, current_user: str = Depends(get_current_user)):
    user_doc = users_collection.find_one({"username": current_user})
    if not user_doc.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    provider_doc = {
        "provider_id": str(uuid.uuid4()),
        "name": provider.name,
        "description": provider.description,
        "base_url": provider.base_url,
        "headers": provider.headers,
        "request_body_template": provider.request_body_template,
        "response_parser": provider.response_parser,
        "models": provider.models,
        "provider_type": provider.provider_type,
        "is_active": provider.is_active,
        "created_at": datetime.utcnow(),
        "created_by": current_user
    }
    
    providers_collection.insert_one(provider_doc)
    return {"message": "Provider added successfully", "provider_id": provider_doc["provider_id"]}

@app.post("/api/admin/providers/curl")
async def add_provider_from_curl(provider: CurlProvider, current_user: str = Depends(get_current_user)):
    user_doc = users_collection.find_one({"username": current_user})
    if not user_doc.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Parse curl command
    parsed_config = parse_curl_command(provider.curl_command)
    
    provider_doc = {
        "provider_id": str(uuid.uuid4()),
        "name": provider.name,
        "description": provider.description,
        "base_url": parsed_config["base_url"],
        "headers": parsed_config["headers"],
        "request_body_template": parsed_config["request_body_template"],
        "response_parser": parsed_config["response_parser"],
        "models": provider.models,
        "provider_type": provider.provider_type,
        "is_active": provider.is_active,
        "curl_command": provider.curl_command,
        "created_at": datetime.utcnow(),
        "created_by": current_user
    }
    
    providers_collection.insert_one(provider_doc)
    return {"message": "Provider added successfully from curl command", "provider_id": provider_doc["provider_id"]}

@app.get("/api/admin/providers")
async def get_all_providers(current_user: str = Depends(get_current_user)):
    user_doc = users_collection.find_one({"username": current_user})
    if not user_doc.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    providers = list(providers_collection.find({}, {"_id": 0}))
    return {"providers": providers}

@app.put("/api/admin/providers/{provider_id}")
async def update_provider(provider_id: str, provider: LLMProvider, current_user: str = Depends(get_current_user)):
    user_doc = users_collection.find_one({"username": current_user})
    if not user_doc.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = providers_collection.update_one(
        {"provider_id": provider_id},
        {"$set": {
            "name": provider.name,
            "description": provider.description,
            "base_url": provider.base_url,
            "headers": provider.headers,
            "request_body_template": provider.request_body_template,
            "response_parser": provider.response_parser,
            "models": provider.models,
            "provider_type": provider.provider_type,
            "is_active": provider.is_active,
            "updated_at": datetime.utcnow()
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return {"message": "Provider updated successfully"}

@app.delete("/api/admin/providers/{provider_id}")
async def delete_provider(provider_id: str, current_user: str = Depends(get_current_user)):
    user_doc = users_collection.find_one({"username": current_user})
    if not user_doc.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = providers_collection.delete_one({"provider_id": provider_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return {"message": "Provider deleted successfully"}

# Public Provider Routes
@app.get("/api/providers")
async def get_active_providers(current_user: str = Depends(get_current_user)):
    providers = list(providers_collection.find(
        {"is_active": True}, 
        {"_id": 0, "provider_id": 1, "name": 1, "description": 1, "models": 1, "provider_type": 1}
    ))
    return {"providers": providers}

@app.get("/api/providers/text")
async def get_text_providers(current_user: str = Depends(get_current_user)):
    providers = list(providers_collection.find(
        {"is_active": True, "provider_type": "text"}, 
        {"_id": 0, "provider_id": 1, "name": 1, "description": 1, "models": 1}
    ))
    return {"providers": providers}

@app.get("/api/providers/image")
async def get_image_providers(current_user: str = Depends(get_current_user)):
    providers = list(providers_collection.find(
        {"is_active": True, "provider_type": "image"}, 
        {"_id": 0, "provider_id": 1, "name": 1, "description": 1, "models": 1}
    ))
    return {"providers": providers}

# Text Generation Routes
@app.post("/api/generate/text")
async def generate_text(request: TextGenerationRequest, current_user: str = Depends(get_current_user)):
    # Get provider configuration
    provider = providers_collection.find_one({"name": request.provider_name, "is_active": True})
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found or inactive")
    
    # Check if model is supported
    if request.model not in provider["models"]:
        raise HTTPException(status_code=400, detail="Model not supported by this provider")
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get conversation history
    conversation = conversations_collection.find_one({"session_id": session_id})
    if not conversation:
        conversation = {
            "session_id": session_id,
            "user_id": current_user,
            "messages": [],
            "created_at": datetime.utcnow()
        }
        conversations_collection.insert_one(conversation)
    
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
    
    try:
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
        generated_content = extract_response_content(response_data, provider["response_parser"])
        
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
            "user_id": current_user,
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
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

# Image Generation Routes
@app.post("/api/generate/image")
async def generate_image(request: ImageGenerationRequest, current_user: str = Depends(get_current_user)):
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        image_base64 = None
        
        # Handle built-in providers
        if request.provider_name == "openai" and OPENAI_API_KEY:
            # OpenAI DALL-E 3 via emergentintegrations
            image_gen = OpenAIImageGeneration(api_key=OPENAI_API_KEY)
            images = await image_gen.generate_images(
                prompt=request.prompt,
                model=request.model,
                number_of_images=request.number_of_images
            )
            
            if images and len(images) > 0:
                image_base64 = base64.b64encode(images[0]).decode('utf-8')
            else:
                raise HTTPException(status_code=500, detail="No image was generated")
                
        elif request.provider_name == "fal" and FAL_API_KEY:
            # Stable Diffusion via fal.ai
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
                    image_base64 = base64.b64encode(img_response.content).decode('utf-8')
            else:
                raise HTTPException(status_code=500, detail="No image was generated")
        
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
                    image_base64 = base64.b64encode(img_response.content).decode('utf-8')
            else:
                raise HTTPException(status_code=500, detail="No image URL found in response")
        
        # Save generation record
        generation_record = {
            "generation_id": str(uuid.uuid4()),
            "user_id": current_user,
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
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@app.get("/api/conversations/{session_id}")
async def get_conversation(session_id: str, current_user: str = Depends(get_current_user)):
    conversation = conversations_collection.find_one(
        {"session_id": session_id, "user_id": current_user},
        {"_id": 0}
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation

@app.get("/api/conversations")
async def get_user_conversations(current_user: str = Depends(get_current_user)):
    conversations = list(conversations_collection.find(
        {"user_id": current_user},
        {"_id": 0, "session_id": 1, "created_at": 1}
    ).sort("created_at", -1))
    
    return {"conversations": conversations}

@app.get("/api/generations")
async def get_user_generations(current_user: str = Depends(get_current_user)):
    generations = list(generations_collection.find(
        {"user_id": current_user},
        {"_id": 0}
    ).sort("created_at", -1).limit(50))
    
    return {"generations": generations}

@app.get("/api/generations/images")
async def get_user_image_generations(current_user: str = Depends(get_current_user)):
    generations = list(image_generations_collection.find(
        {"user_id": current_user},
        {"_id": 0}
    ).sort("created_at", -1).limit(50))
    
    return {"generations": generations}

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Root endpoint
@app.get("/api/")
async def root():
    return {"message": "ContentForge AI API", "version": "1.0.0"}

# Initialize default providers
@app.on_event("startup")
async def initialize_default_providers():
    """Initialize default providers if they don't exist"""
    
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
    
    # Insert default providers if they don't exist
    for provider in default_text_providers + default_image_providers:
        if not providers_collection.find_one({"provider_id": provider["provider_id"]}):
            providers_collection.insert_one(provider)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)