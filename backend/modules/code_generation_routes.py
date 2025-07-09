from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from utils.auth_utils import get_current_user
from services.code_generation_service import CodeGenerationService
from models.generation_models import CodeGenerationRequest, CodeGenerationResponse

router = APIRouter(prefix="/api/code", tags=["code_generation"])

# Initialize code generation service
code_service = CodeGenerationService()

@router.post("/generate", response_model=CodeGenerationResponse)
async def generate_code(
    request: CodeGenerationRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generate code using AI providers
    """
    try:
        response = await code_service.generate_code(request, current_user)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code generation failed: {str(e)}"
        )

@router.get("/history", response_model=List[Dict])
async def get_code_generation_history(
    limit: int = 50,
    current_user: str = Depends(get_current_user)
):
    """
    Get user's code generation history
    """
    try:
        history = await code_service.get_user_code_generations(current_user, limit)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )

@router.get("/generation/{generation_id}")
async def get_code_generation(
    generation_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Get specific code generation by ID
    """
    try:
        generation = await code_service.get_code_generation_by_id(generation_id, current_user)
        if not generation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Code generation not found"
            )
        return generation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve generation: {str(e)}"
        )

@router.get("/providers", response_model=List[Dict])
async def get_code_providers():
    """
    Get available code generation providers and models
    """
    try:
        providers = await code_service.get_available_providers()
        return providers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve providers: {str(e)}"
        )

@router.get("/languages", response_model=List[Dict])
async def get_supported_languages():
    """
    Get supported programming languages
    """
    try:
        languages = await code_service.get_supported_languages()
        return languages
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve languages: {str(e)}"
        )

@router.get("/request-types", response_model=List[Dict])
async def get_request_types():
    """
    Get available code generation request types
    """
    try:
        request_types = await code_service.get_request_types()
        return request_types
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve request types: {str(e)}"
        )

@router.post("/session/{session_id}/continue")
async def continue_code_session(
    session_id: str,
    request: CodeGenerationRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Continue code generation in existing session
    """
    try:
        # Override session_id in request
        request.session_id = session_id
        response = await code_service.generate_code(request, current_user)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code generation failed: {str(e)}"
        )

@router.delete("/generation/{generation_id}")
async def delete_code_generation(
    generation_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Delete a code generation
    """
    try:
        # Check if generation exists and belongs to user
        generation = await code_service.get_code_generation_by_id(generation_id, current_user)
        if not generation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Code generation not found"
            )
        
        # Delete from database
        code_generations_collection = code_service.db.code_generations
        await code_generations_collection.delete_one({
            "id": generation_id,
            "user_id": current_user
        })
        
        return {"message": "Code generation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete generation: {str(e)}"
        )

@router.get("/stats")
async def get_code_generation_stats(
    current_user: str = Depends(get_current_user)
):
    """
    Get user's code generation statistics
    """
    try:
        code_generations_collection = code_service.db.code_generations
        
        # Total generations
        total_generations = await code_generations_collection.count_documents({
            "user_id": current_user
        })
        
        # Generations by language
        language_pipeline = [
            {"$match": {"user_id": current_user}},
            {"$group": {"_id": "$language", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        language_stats = []
        async for doc in code_generations_collection.aggregate(language_pipeline):
            language_stats.append({
                "language": doc["_id"],
                "count": doc["count"]
            })
        
        # Generations by request type
        type_pipeline = [
            {"$match": {"user_id": current_user}},
            {"$group": {"_id": "$request_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        type_stats = []
        async for doc in code_generations_collection.aggregate(type_pipeline):
            type_stats.append({
                "request_type": doc["_id"],
                "count": doc["count"]
            })
        
        # Generations by provider
        provider_pipeline = [
            {"$match": {"user_id": current_user}},
            {"$group": {"_id": "$provider", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        provider_stats = []
        async for doc in code_generations_collection.aggregate(provider_pipeline):
            provider_stats.append({
                "provider": doc["_id"],
                "count": doc["count"]
            })
        
        return {
            "total_generations": total_generations,
            "by_language": language_stats,
            "by_request_type": type_stats,
            "by_provider": provider_stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {str(e)}"
        )
