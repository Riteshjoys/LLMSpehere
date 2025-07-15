import asyncio
import json
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime
from io import BytesIO
import uuid

from models.presentation_models import (
    PresentationRequest, PresentationResponse, PresentationGeneration,
    SlideContent, SlideType, ChartType, PresentationFormat, PresentationTheme,
    SlideGenerationRequest, ChartData, PresentationTemplate, SlideLayout
)
from services.text_generation_service import TextGenerationService
from services.image_generation_service import ImageGenerationService
from utils.database import get_database

class PresentationService:
    def __init__(self):
        self.db = get_database()
        self.text_service = TextGenerationService()
        self.image_service = ImageGenerationService()

    async def generate_presentation(self, request: PresentationRequest, user_id: str) -> PresentationResponse:
        """Generate a complete presentation"""
        try:
            # Generate presentation outline
            outline = await self._generate_outline(request)
            
            # Generate slides based on outline
            slides = await self._generate_slides(outline, request, user_id)
            
            # Create presentation record
            presentation = PresentationGeneration(
                presentation_id=str(uuid.uuid4()),
                user_id=user_id,
                title=request.title,
                topic=request.topic,
                slides=slides,
                theme=request.theme,
                format=request.format,
                total_slides=len(slides),
                provider=request.provider_name,
                model=request.model
            )
            
            # Save to database
            await self._save_presentation(presentation)
            
            # Generate file if requested
            file_data = await self._generate_file(presentation)
            
            return PresentationResponse(
                presentation_id=presentation.presentation_id,
                title=presentation.title,
                topic=presentation.topic,
                slides=presentation.slides,
                theme=presentation.theme,
                format=presentation.format,
                total_slides=presentation.total_slides,
                file_base64=file_data.get('base64') if file_data else None,
                file_url=file_data.get('url') if file_data else None,
                thumbnail_url=file_data.get('thumbnail') if file_data else None,
                created_at=presentation.created_at,
                user_id=presentation.user_id,
                provider=presentation.provider,
                model=presentation.model
            )
            
        except Exception as e:
            raise Exception(f"Failed to generate presentation: {str(e)}")

    async def _generate_outline(self, request: PresentationRequest) -> List[str]:
        """Generate presentation outline using AI"""
        if request.outline:
            return request.outline
        
        prompt = f"""
        Create a detailed outline for a {request.num_slides}-slide presentation on "{request.topic}".
        
        Title: {request.title}
        Audience: {request.audience}
        Tone: {request.tone}
        
        Please provide a JSON array of slide titles/topics that would make an effective presentation.
        Each slide should be a string describing the main point or topic for that slide.
        
        The first slide should be a title slide, and the last slide should be a conclusion or thank you slide.
        
        Example format:
        [
            "Title: {request.title}",
            "Introduction to {request.topic}",
            "Key Benefits",
            "Implementation Strategy",
            "Case Studies",
            "Next Steps",
            "Thank You & Questions"
        ]
        """
        
        try:
            # Use text generation service to create outline
            outline_response = await self.text_service.generate_text(
                provider_name=request.provider_name or "openai",
                model=request.model or "gpt-4",
                prompt=prompt,
                max_tokens=1000,
                user_id=request.user_id if hasattr(request, 'user_id') else "system"
            )
            
            # Parse the response to extract outline
            outline_text = outline_response.get('content', '').strip()
            
            # Try to parse as JSON first
            try:
                outline = json.loads(outline_text)
                if isinstance(outline, list):
                    return outline[:request.num_slides]
            except:
                # If not JSON, split by lines and clean up
                lines = outline_text.split('\n')
                outline = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith(('```', 'json', 'Here')):
                        # Clean up line formatting
                        line = line.replace('"', '').replace(',', '').strip()
                        if line.startswith(('- ', '* ', '1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
                            line = line[2:].strip()
                        outline.append(line)
                
                return outline[:request.num_slides]
            
        except Exception as e:
            # Fallback to default outline
            return self._get_default_outline(request)

    def _get_default_outline(self, request: PresentationRequest) -> List[str]:
        """Generate a default outline if AI generation fails"""
        base_outline = [
            f"Title: {request.title}",
            f"Introduction to {request.topic}",
            "Key Points",
            "Benefits and Advantages",
            "Implementation",
            "Examples and Case Studies",
            "Challenges and Solutions",
            "Future Outlook",
            "Conclusion",
            "Thank You & Questions"
        ]
        
        return base_outline[:request.num_slides]

    async def _generate_slides(self, outline: List[str], request: PresentationRequest, user_id: str) -> List[SlideContent]:
        """Generate slide content for each outline item"""
        slides = []
        
        for i, slide_title in enumerate(outline):
            slide_type = self._determine_slide_type(slide_title, i, len(outline))
            
            slide_content = await self._generate_slide_content(
                slide_title=slide_title,
                slide_type=slide_type,
                request=request,
                user_id=user_id,
                position=i
            )
            
            slides.append(slide_content)
        
        return slides

    def _determine_slide_type(self, title: str, position: int, total_slides: int) -> SlideType:
        """Determine slide type based on title and position"""
        title_lower = title.lower()
        
        if position == 0 or "title" in title_lower:
            return SlideType.TITLE
        elif position == total_slides - 1 or any(word in title_lower for word in ["conclusion", "thank", "questions", "summary"]):
            return SlideType.CONCLUSION
        elif any(word in title_lower for word in ["chart", "data", "statistics", "metrics", "numbers"]):
            return SlideType.CHART
        elif any(word in title_lower for word in ["image", "example", "case", "demo"]):
            return SlideType.IMAGE
        elif any(word in title_lower for word in ["vs", "comparison", "compare", "differences"]):
            return SlideType.COMPARISON
        else:
            return SlideType.CONTENT

    async def _generate_slide_content(self, slide_title: str, slide_type: SlideType, request: PresentationRequest, user_id: str, position: int) -> SlideContent:
        """Generate content for a specific slide"""
        
        # Create base slide
        slide = SlideContent(
            type=slide_type,
            layout_id=self._get_layout_for_type(slide_type),
            title=slide_title,
            position=position
        )
        
        if slide_type == SlideType.TITLE:
            slide.title = request.title
            slide.content = f"Presentation on {request.topic}"
            slide.speaker_notes = f"Welcome to this presentation on {request.topic}. Today we'll explore the key aspects and insights."
        
        elif slide_type == SlideType.CONCLUSION:
            slide.title = "Conclusion"
            slide.content = await self._generate_conclusion_content(request, user_id)
            slide.speaker_notes = "Thank you for your attention. Are there any questions?"
        
        else:
            # Generate detailed content for regular slides
            content_prompt = f"""
            Create content for a presentation slide with the title: "{slide_title}"
            
            Context:
            - Overall presentation topic: {request.topic}
            - Audience: {request.audience}
            - Tone: {request.tone}
            
            Please provide:
            1. Main content/bullet points (3-5 key points)
            2. Speaker notes (2-3 sentences for the presenter)
            
            Format the response as:
            CONTENT:
            • Point 1
            • Point 2
            • Point 3
            
            SPEAKER_NOTES:
            Notes for the presenter...
            """
            
            try:
                content_response = await self.text_service.generate_text(
                    provider_name=request.provider_name or "openai",
                    model=request.model or "gpt-4",
                    prompt=content_prompt,
                    max_tokens=500,
                    user_id=user_id
                )
                
                content_text = content_response.get('content', '').strip()
                
                # Parse content and speaker notes
                if "CONTENT:" in content_text and "SPEAKER_NOTES:" in content_text:
                    parts = content_text.split("SPEAKER_NOTES:")
                    content_part = parts[0].replace("CONTENT:", "").strip()
                    notes_part = parts[1].strip()
                    
                    # Extract bullet points
                    bullet_points = []
                    for line in content_part.split('\n'):
                        line = line.strip()
                        if line and line.startswith(('•', '-', '*')):
                            bullet_points.append(line[1:].strip())
                    
                    slide.bullet_points = bullet_points
                    slide.content = content_part
                    slide.speaker_notes = notes_part
                else:
                    slide.content = content_text
                    slide.speaker_notes = f"Present the content about {slide_title}."
                
            except Exception as e:
                # Fallback content
                slide.content = f"Key points about {slide_title} will be discussed here."
                slide.speaker_notes = f"Discuss the main aspects of {slide_title}."
        
        # Generate image if requested and appropriate
        if request.include_images and slide_type in [SlideType.CONTENT, SlideType.IMAGE]:
            try:
                image_data = await self._generate_slide_image(slide_title, request, user_id)
                if image_data:
                    slide.image_base64 = image_data
            except Exception as e:
                print(f"Failed to generate image for slide: {e}")
        
        # Generate chart if requested and appropriate
        if request.include_charts and slide_type == SlideType.CHART:
            try:
                chart_data = await self._generate_chart_data(slide_title, request)
                if chart_data:
                    slide.chart_data = chart_data
                    slide.chart_type = ChartType.BAR  # Default
            except Exception as e:
                print(f"Failed to generate chart for slide: {e}")
        
        return slide

    async def _generate_conclusion_content(self, request: PresentationRequest, user_id: str) -> str:
        """Generate conclusion content"""
        prompt = f"""
        Create a conclusion for a presentation on "{request.topic}".
        
        Title: {request.title}
        Audience: {request.audience}
        
        Please provide a brief conclusion that summarizes the key takeaways and includes a call to action.
        Keep it concise and impactful.
        """
        
        try:
            response = await self.text_service.generate_text(
                provider_name=request.provider_name or "openai",
                model=request.model or "gpt-4",
                prompt=prompt,
                max_tokens=200,
                user_id=user_id
            )
            return response.get('content', 'Thank you for your attention. Questions?')
        except:
            return 'Thank you for your attention. Questions?'

    async def _generate_slide_image(self, slide_title: str, request: PresentationRequest, user_id: str) -> Optional[str]:
        """Generate an image for a slide"""
        image_prompt = f"Professional illustration for presentation slide about {slide_title}, {request.tone} style, business presentation format"
        
        try:
            image_response = await self.image_service.generate_image(
                provider_name="openai",  # Default to OpenAI for now
                model="dall-e-3",
                prompt=image_prompt,
                user_id=user_id
            )
            return image_response.get('image_base64')
        except Exception as e:
            print(f"Image generation failed: {e}")
            return None

    async def _generate_chart_data(self, slide_title: str, request: PresentationRequest) -> Optional[Dict[str, Any]]:
        """Generate sample chart data for a slide"""
        # This would integrate with a data visualization service
        # For now, return sample data
        return {
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "datasets": [{
                "label": "Performance",
                "data": [65, 59, 80, 81],
                "backgroundColor": "#4F46E5"
            }]
        }

    def _get_layout_for_type(self, slide_type: SlideType) -> str:
        """Get appropriate layout ID for slide type"""
        layout_map = {
            SlideType.TITLE: "title_layout",
            SlideType.CONTENT: "content_layout",
            SlideType.IMAGE: "image_layout",
            SlideType.CHART: "chart_layout",
            SlideType.COMPARISON: "comparison_layout",
            SlideType.CONCLUSION: "conclusion_layout"
        }
        return layout_map.get(slide_type, "content_layout")

    async def _save_presentation(self, presentation: PresentationGeneration):
        """Save presentation to database"""
        try:
            presentation_data = presentation.dict()
            presentation_data['_id'] = presentation.presentation_id
            
            await self.db.presentation_generations.insert_one(presentation_data)
        except Exception as e:
            print(f"Failed to save presentation: {e}")

    async def _generate_file(self, presentation: PresentationGeneration) -> Optional[Dict[str, Any]]:
        """Generate presentation file (placeholder for now)"""
        # This would integrate with presentation generation libraries
        # For now, return placeholder data
        return {
            "base64": "placeholder_base64_data",
            "url": f"/presentations/{presentation.presentation_id}.pptx",
            "thumbnail": f"/presentations/{presentation.presentation_id}_thumb.png"
        }

    async def get_user_presentations(self, user_id: str, limit: int = 50, offset: int = 0) -> List[PresentationResponse]:
        """Get user's presentations"""
        try:
            presentations = await self.db.presentation_generations.find(
                {"user_id": user_id}
            ).sort("created_at", -1).skip(offset).limit(limit).to_list(length=limit)
            
            return [
                PresentationResponse(
                    presentation_id=p["presentation_id"],
                    title=p["title"],
                    topic=p["topic"],
                    slides=p["slides"],
                    theme=p["theme"],
                    format=p["format"],
                    total_slides=p["total_slides"],
                    file_base64=p.get("file_base64"),
                    file_url=p.get("file_url"),
                    thumbnail_url=p.get("thumbnail_url"),
                    created_at=p["created_at"],
                    user_id=p["user_id"],
                    provider=p.get("provider"),
                    model=p.get("model")
                )
                for p in presentations
            ]
        except Exception as e:
            print(f"Failed to get presentations: {e}")
            return []

    async def get_presentation(self, presentation_id: str, user_id: str) -> Optional[PresentationResponse]:
        """Get a specific presentation"""
        try:
            presentation = await self.db.presentation_generations.find_one({
                "presentation_id": presentation_id,
                "user_id": user_id
            })
            
            if not presentation:
                return None
                
            return PresentationResponse(
                presentation_id=presentation["presentation_id"],
                title=presentation["title"],
                topic=presentation["topic"],
                slides=presentation["slides"],
                theme=presentation["theme"],
                format=presentation["format"],
                total_slides=presentation["total_slides"],
                file_base64=presentation.get("file_base64"),
                file_url=presentation.get("file_url"),
                thumbnail_url=presentation.get("thumbnail_url"),
                created_at=presentation["created_at"],
                user_id=presentation["user_id"],
                provider=presentation.get("provider"),
                model=presentation.get("model")
            )
        except Exception as e:
            print(f"Failed to get presentation: {e}")
            return None

    async def delete_presentation(self, presentation_id: str, user_id: str) -> bool:
        """Delete a presentation"""
        try:
            result = await self.db.presentation_generations.delete_one({
                "presentation_id": presentation_id,
                "user_id": user_id
            })
            return result.deleted_count > 0
        except Exception as e:
            print(f"Failed to delete presentation: {e}")
            return False

    async def get_templates(self) -> List[PresentationTemplate]:
        """Get available presentation templates"""
        # This would load from database or config
        # For now, return sample templates
        return [
            PresentationTemplate(
                template_id="business_template",
                name="Business Professional",
                description="Clean and professional template for business presentations",
                theme=PresentationTheme.BUSINESS,
                category="business",
                slides=[],
                color_scheme={"primary": "#1f2937", "secondary": "#3b82f6", "accent": "#10b981"},
                font_settings={"heading": "Arial", "body": "Arial"},
                thumbnail_url="/templates/business_thumb.png"
            ),
            PresentationTemplate(
                template_id="creative_template",
                name="Creative Modern",
                description="Vibrant and creative template for innovative presentations",
                theme=PresentationTheme.CREATIVE,
                category="creative",
                slides=[],
                color_scheme={"primary": "#7c3aed", "secondary": "#f59e0b", "accent": "#ef4444"},
                font_settings={"heading": "Helvetica", "body": "Helvetica"},
                thumbnail_url="/templates/creative_thumb.png"
            )
        ]