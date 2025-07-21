import os
import asyncio
import io
import base64
import json
import uuid
import tempfile
import subprocess
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

import aiofiles
from elevenlabs.client import ElevenLabs as ElevenLabsClient
from elevenlabs import Voice, VoiceSettings
from pymongo import MongoClient
from bson import Binary
import ffmpeg
import requests

from models.faceless_content_models import (
    FacelessContentRequest,
    FacelessContentResponse,
    FacelessContent,
    TTSRequest,
    TTSResponse,
    ScreenRecordingRequest,
    ScreenRecordingResponse,
    AnimatedCharacterRequest,
    BackgroundMusicRequest,
    Voice as VoiceModel,
    VoiceCloneRequest,
    VoiceCloneResponse,
    FacelessContentTemplate,
    FacelessContentStats,
    AnimatedCharacter,
    BackgroundMusic
)
from utils.database import get_database
from utils.config import ELEVENLABS_API_KEY

class FacelessContentService:
    def __init__(self):
        self.db = get_database()
        self.elevenlabs_client = ElevenLabsClient(api_key=ELEVENLABS_API_KEY)
        self.content_collection = self.db.faceless_content
        self.voices_collection = self.db.voices
        self.characters_collection = self.db.animated_characters
        self.music_collection = self.db.background_music
        self.templates_collection = self.db.faceless_templates
        
        # Create temp directories
        self.temp_dir = Path(tempfile.gettempdir()) / "faceless_content"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Initialize default data will be done on first use
        self._initialized = False
    
    async def _initialize_default_data(self):
        """Initialize default voices, characters, and music"""
        try:
            # Initialize default voices
            await self._initialize_default_voices()
            
            # Initialize default characters
            await self._initialize_default_characters()
            
            # Initialize default background music
            await self._initialize_default_music()
            
            # Initialize default templates
            await self._initialize_default_templates()
            
        except Exception as e:
            print(f"Error initializing default data: {e}")
    
    async def _initialize_default_voices(self):
        """Initialize default ElevenLabs voices"""
        try:
            # Get available voices from ElevenLabs
            voices_response = self.elevenlabs_client.voices.get_all()
            
            # Store voices in database
            for voice in voices_response.voices:
                voice_data = {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category or "General",
                    "gender": "Unknown",
                    "age": "Unknown",
                    "accent": "Unknown",
                    "language": "English",
                    "preview_url": voice.preview_url,
                    "created_at": datetime.utcnow()
                }
                
                self.voices_collection.replace_one(
                    {"voice_id": voice.voice_id},
                    voice_data,
                    upsert=True
                )
                
        except Exception as e:
            print(f"Error initializing voices: {e}")
            # Add some default voices if API fails
            default_voices = [
                {
                    "voice_id": "21m00Tcm4TlvDq8ikWAM",
                    "name": "Rachel",
                    "category": "General",
                    "gender": "Female",
                    "age": "Adult",
                    "accent": "American",
                    "language": "English",
                    "preview_url": None,
                    "created_at": datetime.utcnow()
                },
                {
                    "voice_id": "AZnzlk1XvdvUeBnXmlld",
                    "name": "Domi",
                    "category": "General",
                    "gender": "Female",
                    "age": "Adult",
                    "accent": "American",
                    "language": "English",
                    "preview_url": None,
                    "created_at": datetime.utcnow()
                },
                {
                    "voice_id": "EXAVITQu4vr4fYnSx1bJ",
                    "name": "Bella",
                    "category": "General",
                    "gender": "Female",
                    "age": "Adult",
                    "accent": "American",
                    "language": "English",
                    "preview_url": None,
                    "created_at": datetime.utcnow()
                }
            ]
            
            for voice in default_voices:
                self.voices_collection.replace_one(
                    {"voice_id": voice["voice_id"]},
                    voice,
                    upsert=True
                )
    
    async def _initialize_default_characters(self):
        """Initialize default animated characters"""
        default_characters = [
            {
                "character_id": "avatar_1",
                "name": "Professional Avatar",
                "animation_type": "simple",
                "position": {"x": 0.8, "y": 0.7},
                "scale": 1.0,
                "animations": ["idle", "talking", "gesturing", "nodding"],
                "description": "A professional-looking avatar for business content"
            },
            {
                "character_id": "avatar_2",
                "name": "Casual Avatar",
                "animation_type": "simple",
                "position": {"x": 0.2, "y": 0.7},
                "scale": 0.8,
                "animations": ["idle", "talking", "waving", "pointing"],
                "description": "A casual avatar for educational content"
            },
            {
                "character_id": "mascot_1",
                "name": "Friendly Mascot",
                "animation_type": "animated",
                "position": {"x": 0.5, "y": 0.8},
                "scale": 0.6,
                "animations": ["bounce", "talking", "celebrating", "thinking"],
                "description": "A friendly mascot character for engaging content"
            }
        ]
        
        for character in default_characters:
            character["created_at"] = datetime.utcnow()
            self.characters_collection.replace_one(
                {"character_id": character["character_id"]},
                character,
                upsert=True
            )
    
    async def _initialize_default_music(self):
        """Initialize default background music tracks"""
        default_music = [
            {
                "track_id": "corporate_1",
                "name": "Corporate Inspiration",
                "genre": "Corporate",
                "duration": 120.0,
                "tempo": "Medium",
                "mood": "Motivational",
                "file_url": "/static/music/corporate_inspiration.mp3",
                "description": "Uplifting corporate background music"
            },
            {
                "track_id": "tech_1",
                "name": "Tech Innovation",
                "genre": "Electronic",
                "duration": 180.0,
                "tempo": "Fast",
                "mood": "Energetic",
                "file_url": "/static/music/tech_innovation.mp3",
                "description": "Modern electronic music for tech content"
            },
            {
                "track_id": "calm_1",
                "name": "Peaceful Focus",
                "genre": "Ambient",
                "duration": 300.0,
                "tempo": "Slow",
                "mood": "Calm",
                "file_url": "/static/music/peaceful_focus.mp3",
                "description": "Calm ambient music for educational content"
            }
        ]
        
        for music in default_music:
            music["created_at"] = datetime.utcnow()
            self.music_collection.replace_one(
                {"track_id": music["track_id"]},
                music,
                upsert=True
            )
    
    async def _initialize_default_templates(self):
        """Initialize default faceless content templates"""
        default_templates = [
            {
                "template_id": "business_presentation",
                "name": "Business Presentation",
                "description": "Professional business presentation template",
                "category": "Business",
                "default_voice_id": "21m00Tcm4TlvDq8ikWAM",
                "default_character": "avatar_1",
                "default_music": "corporate_1",
                "video_duration": 60.0,
                "video_format": "mp4",
                "video_quality": "high",
                "video_resolution": "1920x1080",
                "content_structure": [
                    {"type": "intro", "duration": 10, "text": "Welcome to our presentation"},
                    {"type": "main", "duration": 40, "text": "Main content goes here"},
                    {"type": "outro", "duration": 10, "text": "Thank you for watching"}
                ]
            },
            {
                "template_id": "educational_tutorial",
                "name": "Educational Tutorial",
                "description": "Tutorial template for educational content",
                "category": "Education",
                "default_voice_id": "EXAVITQu4vr4fYnSx1bJ",
                "default_character": "avatar_2",
                "default_music": "calm_1",
                "video_duration": 300.0,
                "video_format": "mp4",
                "video_quality": "high",
                "video_resolution": "1920x1080",
                "content_structure": [
                    {"type": "intro", "duration": 30, "text": "Introduction to the topic"},
                    {"type": "steps", "duration": 240, "text": "Step-by-step instructions"},
                    {"type": "conclusion", "duration": 30, "text": "Summary and next steps"}
                ]
            },
            {
                "template_id": "product_demo",
                "name": "Product Demo",
                "description": "Product demonstration template",
                "category": "Marketing",
                "default_voice_id": "pNInz6obpgDQGcFmaJgB",
                "default_character": "mascot_1",
                "default_music": "tech_1",
                "video_duration": 120.0,
                "video_format": "mp4",
                "video_quality": "high",
                "video_resolution": "1920x1080",
                "content_structure": [
                    {"type": "hook", "duration": 15, "text": "Attention-grabbing hook"},
                    {"type": "demo", "duration": 90, "text": "Product demonstration"},
                    {"type": "cta", "duration": 15, "text": "Call to action"}
                ]
            }
        ]
        
        for template in default_templates:
            template["created_at"] = datetime.utcnow()
            template["updated_at"] = datetime.utcnow()
            template["is_active"] = True
            self.templates_collection.replace_one(
                {"template_id": template["template_id"]},
                template,
                upsert=True
            )
    
    async def generate_tts_audio(self, tts_request: TTSRequest) -> TTSResponse:
        """Generate text-to-speech audio using ElevenLabs"""
        try:
            # Generate audio using the new API
            audio_generator = self.elevenlabs_client.generate(
                text=tts_request.text,
                voice=tts_request.voice_id,
                model="eleven_monolingual_v1",
                stream=True
            )
            
            # Collect audio data
            audio_data = b""
            for chunk in audio_generator:
                audio_data += chunk
            
            # Create unique filename
            audio_filename = f"tts_{uuid.uuid4().hex}.{tts_request.format}"
            audio_path = self.temp_dir / audio_filename
            
            # Save audio file
            with open(audio_path, "wb") as f:
                f.write(audio_data)
            
            # Get audio duration using ffmpeg
            try:
                probe = ffmpeg.probe(str(audio_path))
                duration = float(probe['format']['duration'])
            except:
                duration = 0.0
            
            # Convert to base64 for storage
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return TTSResponse(
                audio_url=f"data:audio/{tts_request.format};base64,{audio_base64}",
                duration=duration,
                voice_id=tts_request.voice_id,
                format=tts_request.format,
                file_size=len(audio_data)
            )
            
        except Exception as e:
            raise Exception(f"TTS generation failed: {str(e)}")
    
    async def simulate_screen_recording(self, recording_request: ScreenRecordingRequest) -> ScreenRecordingResponse:
        """Simulate screen recording (placeholder implementation)"""
        try:
            # This is a placeholder - in a real implementation, you would use
            # libraries like python-mss or opencv to capture screen content
            
            # For now, create a simple colored video
            video_filename = f"screen_record_{uuid.uuid4().hex}.mp4"
            video_path = self.temp_dir / video_filename
            
            # Create a simple colored video using ffmpeg
            width, height = 1920, 1080
            if recording_request.region:
                width = recording_request.region.get('width', 1920)
                height = recording_request.region.get('height', 1080)
            
            # Generate a simple test video
            (
                ffmpeg
                .input('color=blue:size={}x{}:duration={}'.format(width, height, recording_request.duration), f='lavfi')
                .output(str(video_path), vcodec='libx264', pix_fmt='yuv420p', r=recording_request.fps)
                .overwrite_output()
                .run(quiet=True)
            )
            
            # Get video info
            probe = ffmpeg.probe(str(video_path))
            duration = float(probe['format']['duration'])
            file_size = int(probe['format']['size'])
            
            # Convert to base64
            with open(video_path, "rb") as f:
                video_data = f.read()
            video_base64 = base64.b64encode(video_data).decode('utf-8')
            
            return ScreenRecordingResponse(
                video_url=f"data:video/mp4;base64,{video_base64}",
                duration=duration,
                fps=recording_request.fps,
                resolution=f"{width}x{height}",
                file_size=file_size
            )
            
        except Exception as e:
            raise Exception(f"Screen recording failed: {str(e)}")
    
    async def generate_animated_character(self, character_request: AnimatedCharacterRequest) -> Dict[str, Any]:
        """Generate animated character overlay (placeholder implementation)"""
        try:
            # This is a placeholder - in a real implementation, you would use
            # libraries like Manim, Blender Python API, or other animation tools
            
            character = self.characters_collection.find_one(
                {"character_id": character_request.character_id}
            )
            
            if not character:
                raise Exception(f"Character {character_request.character_id} not found")
            
            # Generate simple animated character data
            character_data = {
                "character_id": character_request.character_id,
                "animation": character_request.animation,
                "duration": character_request.duration,
                "position": character_request.position,
                "scale": character_request.scale,
                "text": character_request.text,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return character_data
            
        except Exception as e:
            raise Exception(f"Character generation failed: {str(e)}")
    
    async def compose_faceless_video(self, content_request: FacelessContentRequest, user_id: str) -> FacelessContentResponse:
        """Compose complete faceless video content"""
        start_time = datetime.utcnow()
        content_id = str(uuid.uuid4())
        
        try:
            # Create content record
            content_record = FacelessContent(
                content_id=content_id,
                user_id=user_id,
                title=content_request.title,
                description=content_request.description,
                tts_settings=content_request.dict(),
                status="processing"
            )
            
            self.content_collection.insert_one(content_record.dict())
            
            # Generate TTS audio
            tts_request = TTSRequest(
                text=content_request.tts_text,
                voice_id=content_request.voice_id
            )
            tts_response = await self.generate_tts_audio(tts_request)
            
            # Generate screen recording if requested
            screen_video = None
            if content_request.screen_recording:
                screen_video = await self.simulate_screen_recording(content_request.screen_recording)
            
            # Generate animated character if requested
            character_data = None
            if content_request.animated_character:
                character_data = await self.generate_animated_character(content_request.animated_character)
            
            # Compose final video
            final_video = await self._compose_final_video(
                tts_response,
                screen_video,
                character_data,
                content_request.background_music,
                content_request
            )
            
            # Update content record
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            self.content_collection.update_one(
                {"content_id": content_id},
                {
                    "$set": {
                        "status": "completed",
                        "video_file": final_video["video_url"],
                        "audio_file": tts_response.audio_url,
                        "duration": final_video["duration"],
                        "file_size": final_video["file_size"],
                        "processing_time": processing_time,
                        "completed_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return FacelessContentResponse(
                content_id=content_id,
                title=content_request.title,
                status="completed",
                video_url=final_video["video_url"],
                audio_url=tts_response.audio_url,
                duration=final_video["duration"],
                file_size=final_video["file_size"],
                processing_time=processing_time
            )
            
        except Exception as e:
            # Update content record with error
            self.content_collection.update_one(
                {"content_id": content_id},
                {
                    "$set": {
                        "status": "failed",
                        "error_message": str(e),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            raise Exception(f"Video composition failed: {str(e)}")
    
    async def _compose_final_video(self, tts_response: TTSResponse, screen_video: Optional[ScreenRecordingResponse], 
                                 character_data: Optional[Dict], background_music: Optional[BackgroundMusicRequest], 
                                 content_request: FacelessContentRequest) -> Dict[str, Any]:
        """Compose the final video from all components"""
        try:
            # Create output video filename
            output_filename = f"faceless_video_{uuid.uuid4().hex}.mp4"
            output_path = self.temp_dir / output_filename
            
            # For now, create a simple video with audio
            # In a real implementation, you would compose the video using ffmpeg
            # with all the components (screen recording, animated character, background music)
            
            # Create a simple video with the TTS audio
            duration = tts_response.duration
            
            # Create a simple colored background video
            (
                ffmpeg
                .input('color=black:size=1920x1080:duration={}'.format(duration), f='lavfi')
                .output(str(output_path), vcodec='libx264', pix_fmt='yuv420p', r=30)
                .overwrite_output()
                .run(quiet=True)
            )
            
            # Get video info
            probe = ffmpeg.probe(str(output_path))
            video_duration = float(probe['format']['duration'])
            file_size = int(probe['format']['size'])
            
            # Convert to base64
            with open(output_path, "rb") as f:
                video_data = f.read()
            video_base64 = base64.b64encode(video_data).decode('utf-8')
            
            return {
                "video_url": f"data:video/mp4;base64,{video_base64}",
                "duration": video_duration,
                "file_size": file_size,
                "resolution": "1920x1080",
                "format": "mp4"
            }
            
        except Exception as e:
            raise Exception(f"Video composition failed: {str(e)}")
    
    async def get_available_voices(self) -> List[VoiceModel]:
        """Get all available voices"""
        try:
            voices = []
            for voice_doc in self.voices_collection.find({}):
                voices.append(VoiceModel(
                    voice_id=voice_doc["voice_id"],
                    name=voice_doc["name"],
                    category=voice_doc["category"],
                    gender=voice_doc.get("gender", "Unknown"),
                    age=voice_doc.get("age", "Unknown"),
                    accent=voice_doc.get("accent", "Unknown"),
                    language=voice_doc.get("language", "English"),
                    preview_url=voice_doc.get("preview_url")
                ))
            return voices
        except Exception as e:
            raise Exception(f"Failed to get voices: {str(e)}")
    
    async def get_animated_characters(self) -> List[AnimatedCharacter]:
        """Get all available animated characters"""
        try:
            characters = []
            for char_doc in self.characters_collection.find({}):
                characters.append(AnimatedCharacter(
                    character_id=char_doc["character_id"],
                    name=char_doc["name"],
                    animation_type=char_doc["animation_type"],
                    position=char_doc["position"],
                    scale=char_doc["scale"],
                    animations=char_doc["animations"]
                ))
            return characters
        except Exception as e:
            raise Exception(f"Failed to get characters: {str(e)}")
    
    async def get_background_music(self) -> List[BackgroundMusic]:
        """Get all available background music"""
        try:
            music_list = []
            for music_doc in self.music_collection.find({}):
                music_list.append(BackgroundMusic(
                    track_id=music_doc["track_id"],
                    name=music_doc["name"],
                    genre=music_doc["genre"],
                    duration=music_doc["duration"],
                    tempo=music_doc["tempo"],
                    mood=music_doc["mood"],
                    file_url=music_doc["file_url"]
                ))
            return music_list
        except Exception as e:
            raise Exception(f"Failed to get background music: {str(e)}")
    
    async def get_content_templates(self) -> List[FacelessContentTemplate]:
        """Get all available content templates"""
        try:
            templates = []
            for template_doc in self.templates_collection.find({"is_active": True}):
                templates.append(FacelessContentTemplate(**template_doc))
            return templates
        except Exception as e:
            raise Exception(f"Failed to get templates: {str(e)}")
    
    async def get_user_content(self, user_id: str, limit: int = 50) -> List[FacelessContent]:
        """Get user's faceless content"""
        try:
            content_list = []
            for content_doc in self.content_collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit):
                content_list.append(FacelessContent(**content_doc))
            return content_list
        except Exception as e:
            raise Exception(f"Failed to get user content: {str(e)}")
    
    async def get_content_by_id(self, content_id: str, user_id: str) -> Optional[FacelessContent]:
        """Get specific content by ID"""
        try:
            content_doc = self.content_collection.find_one({
                "content_id": content_id,
                "user_id": user_id
            })
            return FacelessContent(**content_doc) if content_doc else None
        except Exception as e:
            raise Exception(f"Failed to get content: {str(e)}")
    
    async def delete_content(self, content_id: str, user_id: str) -> bool:
        """Delete user's content"""
        try:
            result = self.content_collection.delete_one({
                "content_id": content_id,
                "user_id": user_id
            })
            return result.deleted_count > 0
        except Exception as e:
            raise Exception(f"Failed to delete content: {str(e)}")
    
    async def get_content_stats(self, user_id: str) -> FacelessContentStats:
        """Get user's content statistics"""
        try:
            # Get total content count
            total_content = self.content_collection.count_documents({"user_id": user_id})
            
            # Get completed content for stats
            completed_content = []
            for content_doc in self.content_collection.find({
                "user_id": user_id,
                "status": "completed"
            }):
                completed_content.append(content_doc)
            
            # Calculate stats
            total_duration = sum(c.get("duration", 0) for c in completed_content)
            success_rate = (len(completed_content) / total_content * 100) if total_content > 0 else 0
            avg_processing_time = sum(c.get("processing_time", 0) for c in completed_content) / len(completed_content) if completed_content else 0
            
            # Get popular voices
            voice_usage = {}
            for content in completed_content:
                voice_id = content.get("tts_settings", {}).get("voice_id")
                if voice_id:
                    voice_usage[voice_id] = voice_usage.get(voice_id, 0) + 1
            
            popular_voices = [{"voice_id": k, "count": v} for k, v in sorted(voice_usage.items(), key=lambda x: x[1], reverse=True)[:5]]
            
            # Get recent content
            recent_content = []
            for content_doc in self.content_collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(10):
                recent_content.append({
                    "content_id": content_doc["content_id"],
                    "title": content_doc["title"],
                    "status": content_doc["status"],
                    "created_at": content_doc["created_at"].isoformat(),
                    "duration": content_doc.get("duration", 0)
                })
            
            return FacelessContentStats(
                total_content=total_content,
                total_duration=total_duration,
                success_rate=success_rate,
                avg_processing_time=avg_processing_time,
                popular_voices=popular_voices,
                popular_characters=[],
                content_by_category={"general": total_content},
                recent_content=recent_content
            )
        except Exception as e:
            raise Exception(f"Failed to get content stats: {str(e)}")