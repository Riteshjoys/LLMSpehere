from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Response
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime
import io
import base64

from .database import get_db
from .auth import get_current_user
from .models import User
from .presentation_service import PresentationService

router = APIRouter(prefix="/api/presentations", tags=["presentations"])

# Initialize presentation service
presentation_service = PresentationService()

@router.get("/templates")
async def get_templates(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all available presentation templates"""
    try:
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
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Upload a new presentation template"""
    try:
        # Check if user is admin
        if not current_user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Only admins can create templates")
        
        template_id = await presentation_service.create_template(
            db, name, description, template_type, file, current_user['user_id']
        )
        return {"template_id": template_id, "message": "Template created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get a specific template by ID"""
    try:
        template = await presentation_service.get_template(db, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create")
async def create_presentation(
    request: dict,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new presentation from template"""
    try:
        presentation_id = await presentation_service.create_presentation(
            db, 
            template_id=request.get('template_id'),
            title=request.get('title', 'New Presentation'),
            data=request.get('data', {}),
            user_id=current_user['user_id']
        )
        return {"presentation_id": presentation_id, "message": "Presentation created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_presentations(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all presentations for the current user"""
    try:
        presentations = await presentation_service.get_user_presentations(
            db, current_user['user_id']
        )
        return {"presentations": presentations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{presentation_id}")
async def get_presentation(
    presentation_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get a specific presentation by ID"""
    try:
        presentation = await presentation_service.get_presentation(db, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Check if user owns this presentation
        if presentation['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return presentation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{presentation_id}")
async def update_presentation(
    presentation_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update a presentation"""
    try:
        # Check if user owns this presentation
        presentation = await presentation_service.get_presentation(db, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        if presentation['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        await presentation_service.update_presentation(
            db, presentation_id, request
        )
        return {"message": "Presentation updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{presentation_id}")
async def delete_presentation(
    presentation_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete a presentation"""
    try:
        # Check if user owns this presentation
        presentation = await presentation_service.get_presentation(db, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        if presentation['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        await presentation_service.delete_presentation(db, presentation_id)
        return {"message": "Presentation deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{presentation_id}/generate")
async def generate_presentation(
    presentation_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Generate presentation content using AI"""
    try:
        # Check if user owns this presentation
        presentation = await presentation_service.get_presentation(db, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        if presentation['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = await presentation_service.generate_presentation_content(
            db, presentation_id, request
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{presentation_id}/export/{format}")
async def export_presentation(
    presentation_id: str,
    format: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Export presentation in various formats (pptx, pdf, google-slides)"""
    try:
        # Check if user owns this presentation
        presentation = await presentation_service.get_presentation(db, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        if presentation['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if format not in ['pptx', 'pdf', 'google-slides']:
            raise HTTPException(status_code=400, detail="Invalid export format")
        
        result = await presentation_service.export_presentation(
            db, presentation_id, format
        )
        
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

@router.post("/{presentation_id}/slides")
async def add_slide(
    presentation_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Add a new slide to presentation"""
    try:
        # Check if user owns this presentation
        presentation = await presentation_service.get_presentation(db, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        if presentation['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        slide_id = await presentation_service.add_slide(
            db, presentation_id, request
        )
        return {"slide_id": slide_id, "message": "Slide added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{presentation_id}/slides/{slide_id}")
async def update_slide(
    presentation_id: str,
    slide_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update a slide in presentation"""
    try:
        # Check if user owns this presentation
        presentation = await presentation_service.get_presentation(db, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        if presentation['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        await presentation_service.update_slide(
            db, presentation_id, slide_id, request
        )
        return {"message": "Slide updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{presentation_id}/slides/{slide_id}")
async def delete_slide(
    presentation_id: str,
    slide_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete a slide from presentation"""
    try:
        # Check if user owns this presentation
        presentation = await presentation_service.get_presentation(db, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        if presentation['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        await presentation_service.delete_slide(db, presentation_id, slide_id)
        return {"message": "Slide deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{presentation_id}/charts")
async def create_chart(
    presentation_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a chart for presentation"""
    try:
        # Check if user owns this presentation
        presentation = await presentation_service.get_presentation(db, presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        if presentation['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        chart_data = await presentation_service.create_chart(
            db, presentation_id, request
        )
        return {"chart_data": chart_data, "message": "Chart created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_presentation_history(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get presentation generation history for the current user"""
    try:
        history = await presentation_service.get_presentation_history(
            db, current_user['user_id']
        )
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_presentation_stats(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get presentation statistics for the current user"""
    try:
        stats = await presentation_service.get_presentation_stats(
            db, current_user['user_id']
        )
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))