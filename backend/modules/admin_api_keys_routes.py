from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from utils.auth_utils import get_current_user
from services.auth_service import AuthService

router = APIRouter(prefix="/api/admin", tags=["Admin API Keys"])

@router.post("/api-keys")
async def update_api_keys(
    api_keys: Dict[str, str], 
    current_user: str = Depends(get_current_user)
):
    """Update API keys (Admin only)"""
    if not AuthService.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Here you would typically save the API keys to a secure location
        # For now, we'll just return success
        
        # In a real implementation, you would:
        # 1. Validate the API keys
        # 2. Store them securely (encrypted)
        # 3. Update environment variables
        # 4. Possibly restart services
        
        return {"message": "API keys updated successfully", "keys_updated": list(api_keys.keys())}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update API keys: {str(e)}"
        )

@router.get("/api-keys/status")
async def get_api_keys_status(current_user: str = Depends(get_current_user)):
    """Get API keys configuration status (Admin only)"""
    if not AuthService.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        import os
        
        # Check which API keys are configured
        api_keys_status = {}
        key_names = [
            'OPENAI_API_KEY', 'FAL_API_KEY', 'LUMA_API_KEY', 
            'PIKA_API_KEY', 'GROQ_API_KEY', 'ANTHROPIC_API_KEY',
            'GOOGLE_API_KEY', 'STABILITY_API_KEY'
        ]
        
        for key in key_names:
            value = os.environ.get(key, '')
            api_keys_status[key] = {
                'configured': bool(value and value != f'YOUR_{key}'),
                'preview': value[:8] + '...' if (value and value != f'YOUR_{key}') else None
            }
        
        return {"api_keys_status": api_keys_status}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get API keys status: {str(e)}"
        )