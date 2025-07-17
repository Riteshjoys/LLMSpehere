from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Response
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime
import io
import base64

from utils.auth_utils import get_current_user
from services.auth_service import AuthService
from services.presentation_service import PresentationService

router = APIRouter(prefix="/api/presentations", tags=["presentations"])

# Initialize presentation service
presentation_service = PresentationService()

@router.get("/templates")
async def get_templates(current_user: str = Depends(get_current_user)):
    """Get all available presentation templates"""
    try:
        from utils.database import get_database
        db = get_database()
        templates = await presentation_service.get_templates(db)
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates")
async def create_template(
    name: str = Form(...),
    description: str = Form(...),
    template_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """Upload a new presentation template"""
    try:
        # Check if user is admin
        if not AuthService.is_admin(current_user):
            raise HTTPException(status_code=403, detail="Only admins can create templates")
        
        from utils.database import get_database
        db = get_database()
        template_id = await presentation_service.create_template(
            db, name, description, template_type, file, current_user
        )
        return {"template_id": template_id, "message": "Template created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get a specific template by ID"""
    try:
        from utils.database import get_database
        db = get_database()
        template = presentation_service.get_template(db, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"Error in get_template route: {str(e)}")  # Debug logging
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create")
async def create_presentation(
    request: dict,
    current_user: str = Depends(get_current_user)
):
    """Create a new presentation from template"""
    try:
        from utils.database import get_database
        db = get_database()
        presentation_id = await presentation_service.create_presentation(
            db, 
            template_id=request.get('template_id'),
            title=request.get('title', 'New Presentation'),
            data=request.get('data', {}),
            user_id=current_user
        )
        return {"presentation_id": presentation_id, "message": "Presentation created successfully"}
    except Exception as e:
        print(f"Error in create_presentation route: {str(e)}")  # Debug logging
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_presentations(current_user: str = Depends(get_current_user)):
    """Get all presentations for the current user"""
    try:
        from utils.database import get_database
        db = get_database()
        presentations = await presentation_service.get_user_presentations(db, current_user)
        return {"presentations": presentations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{presentation_id}")
async def get_presentation(
    presentation_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get a specific presentation by ID"""
    try:
        from utils.database import get_database
        db = get_database()
        presentation = await presentation_service.get_presentation_by_id(db, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Check if user owns this presentation
        if presentation['user_id'] != current_user:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return presentation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{presentation_id}")
async def update_presentation(
    presentation_id: str,
    request: dict,
    current_user: str = Depends(get_current_user)
):
    """Update a presentation"""
    try:
        from utils.database import get_database
        db = get_database()
        # Check if user owns this presentation
        presentation = await presentation_service.get_presentation_by_id(db, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        if presentation['user_id'] != current_user:
            raise HTTPException(status_code=403, detail="Access denied")
        
        await presentation_service.update_presentation(db, presentation_id, request)
        return {"message": "Presentation updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{presentation_id}")
async def delete_presentation(
    presentation_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete a presentation"""
    try:
        from utils.database import get_database
        db = get_database()
        # Check if user owns this presentation
        presentation = await presentation_service.get_presentation_by_id(db, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        if presentation['user_id'] != current_user:
            raise HTTPException(status_code=403, detail="Access denied")
        
        await presentation_service.delete_presentation(db, presentation_id)
        return {"message": "Presentation deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{presentation_id}/export/{format}")
async def export_presentation(
    presentation_id: str,
    format: str,
    current_user: str = Depends(get_current_user)
):
    """Export presentation in various formats (pptx, pdf, google-slides)"""
    try:
        from utils.database import get_database
        db = get_database()
        # Check if user owns this presentation
        presentation = await presentation_service.get_presentation_by_id(db, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        if presentation['user_id'] != current_user:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if format not in ['pptx', 'pdf', 'google-slides']:
            raise HTTPException(status_code=400, detail="Invalid export format")
        
        result = await presentation_service.export_presentation(db, presentation_id, format)
        
        if format == 'google-slides':
            # Return Google Slides URL
            return {"url": result['url'], "presentation_id": result['presentation_id']}
        else:
            # Return file content
            content_type = (
                "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                if format == 'pptx' else "application/pdf"
            )
            filename = f"presentation.{format}"
            
            return StreamingResponse(
                io.BytesIO(result),
                media_type=content_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_presentation_history(current_user: str = Depends(get_current_user)):
    """Get presentation generation history for the current user"""
    try:
        from utils.database import get_database
        db = get_database()
        history = presentation_service.get_presentation_history(db, current_user)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_presentation_stats(current_user: str = Depends(get_current_user)):
    """Get presentation statistics for the current user"""
    try:
        from utils.database import get_database
        db = get_database()
        stats = presentation_service.get_presentation_stats(db, current_user)
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))