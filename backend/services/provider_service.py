import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import HTTPException
from models.provider_models import LLMProvider, CurlProvider, ProviderResponse
from utils.database import providers_collection
from utils.curl_parser import parse_curl_command

class ProviderService:
    @staticmethod
    async def add_provider(provider_data: LLMProvider, created_by: str) -> Dict[str, Any]:
        """Add a new provider"""
        provider_doc = {
            "provider_id": str(uuid.uuid4()),
            "name": provider_data.name,
            "description": provider_data.description,
            "base_url": provider_data.base_url,
            "headers": provider_data.headers,
            "request_body_template": provider_data.request_body_template,
            "response_parser": provider_data.response_parser,
            "models": provider_data.models,
            "provider_type": provider_data.provider_type,
            "is_active": provider_data.is_active,
            "created_at": datetime.utcnow(),
            "created_by": created_by
        }
        
        providers_collection.insert_one(provider_doc)
        return {"message": "Provider added successfully", "provider_id": provider_doc["provider_id"]}
    
    @staticmethod
    async def add_provider_from_curl(provider_data: CurlProvider, created_by: str) -> Dict[str, Any]:
        """Add a provider from curl command"""
        # Parse curl command
        parsed_config = parse_curl_command(provider_data.curl_command)
        
        provider_doc = {
            "provider_id": str(uuid.uuid4()),
            "name": provider_data.name,
            "description": provider_data.description,
            "base_url": parsed_config["base_url"],
            "headers": parsed_config["headers"],
            "request_body_template": parsed_config["request_body_template"],
            "response_parser": parsed_config["response_parser"],
            "models": provider_data.models,
            "provider_type": provider_data.provider_type,
            "is_active": provider_data.is_active,
            "curl_command": provider_data.curl_command,
            "created_at": datetime.utcnow(),
            "created_by": created_by
        }
        
        providers_collection.insert_one(provider_doc)
        return {"message": "Provider added successfully from curl command", "provider_id": provider_doc["provider_id"]}
    
    @staticmethod
    async def get_all_providers() -> List[Dict[str, Any]]:
        """Get all providers"""
        providers = list(providers_collection.find({}, {"_id": 0}))
        return providers
    
    @staticmethod
    async def get_active_providers() -> List[Dict[str, Any]]:
        """Get active providers"""
        providers = list(providers_collection.find(
            {"is_active": True}, 
            {"_id": 0, "provider_id": 1, "name": 1, "description": 1, "models": 1, "provider_type": 1}
        ))
        return providers
    
    @staticmethod
    async def get_providers_by_type(provider_type: str) -> List[Dict[str, Any]]:
        """Get providers by type"""
        providers = list(providers_collection.find(
            {"is_active": True, "provider_type": provider_type}, 
            {"_id": 0, "provider_id": 1, "name": 1, "description": 1, "models": 1}
        ))
        return providers
    
    @staticmethod
    async def update_provider(provider_id: str, provider_data: LLMProvider) -> Dict[str, str]:
        """Update provider"""
        result = providers_collection.update_one(
            {"provider_id": provider_id},
            {"$set": {
                "name": provider_data.name,
                "description": provider_data.description,
                "base_url": provider_data.base_url,
                "headers": provider_data.headers,
                "request_body_template": provider_data.request_body_template,
                "response_parser": provider_data.response_parser,
                "models": provider_data.models,
                "provider_type": provider_data.provider_type,
                "is_active": provider_data.is_active,
                "updated_at": datetime.utcnow()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        return {"message": "Provider updated successfully"}
    
    @staticmethod
    async def delete_provider(provider_id: str) -> Dict[str, str]:
        """Delete provider"""
        result = providers_collection.delete_one({"provider_id": provider_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        return {"message": "Provider deleted successfully"}
    
    @staticmethod
    def get_provider_by_name(name: str) -> Dict[str, Any]:
        """Get provider by name"""
        return providers_collection.find_one({"name": name, "is_active": True})