import asyncio
import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from models.viral_content_models import (
    TrendAnalysisRequest, TrendAnalysisResponse, TrendItem, ViralContentTemplate,
    ViralContentRequest, ViralContentResponse, EngagementPrediction,
    CrossPlatformAdaptation, ViralContentGeneration, HashtagAnalysis,
    ViralContentStats, SocialPlatform, ContentType, ViralityScore
)
from services.text_generation_service import TextGenerationService
from utils.database import get_database

class ViralContentService:
    def __init__(self):
        self.db = get_database()
        self.text_service = TextGenerationService()
        self.trends_collection = "viral_trends"
        self.templates_collection = "viral_templates"
        self.generations_collection = "viral_generations"
        self.hashtag_analysis_collection = "hashtag_analysis"
        
        # Initialize default templates
        self.default_templates = self._get_default_templates()
        
        # Platform-specific configuration
        self.platform_configs = {
            SocialPlatform.TIKTOK: {
                "max_length": 2200,
                "optimal_hashtags": 3,
                "best_times": ["6pm", "10pm", "7am"],
                "viral_elements": ["trending_sounds", "challenges", "effects", "duets"]
            },
            SocialPlatform.INSTAGRAM: {
                "max_length": 2200,
                "optimal_hashtags": 5,
                "best_times": ["11am", "1pm", "5pm"],
                "viral_elements": ["reels", "stories", "carousels", "hashtag_strategies"]
            },
            SocialPlatform.YOUTUBE: {
                "max_length": 5000,
                "optimal_hashtags": 3,
                "best_times": ["2pm", "3pm", "9pm"],
                "viral_elements": ["thumbnails", "titles", "hooks", "retention"]
            },
            SocialPlatform.TWITTER: {
                "max_length": 280,
                "optimal_hashtags": 2,
                "best_times": ["9am", "1pm", "3pm"],
                "viral_elements": ["threads", "polls", "trending_topics", "engagement"]
            },
            SocialPlatform.FACEBOOK: {
                "max_length": 63206,
                "optimal_hashtags": 3,
                "best_times": ["1pm", "3pm", "9pm"],
                "viral_elements": ["groups", "pages", "events", "live_videos"]
            },
            SocialPlatform.LINKEDIN: {
                "max_length": 3000,
                "optimal_hashtags": 3,
                "best_times": ["8am", "12pm", "5pm"],
                "viral_elements": ["articles", "professional_content", "networking", "thought_leadership"]
            }
        }

    async def analyze_trends(self, request: TrendAnalysisRequest) -> TrendAnalysisResponse:
        """Analyze current social media trends"""
        try:
            # In a real implementation, this would call actual social media APIs
            # For now, we'll generate realistic mock data
            trends = await self._generate_mock_trends(request)
            
            # Save trends to database
            await self._save_trends(trends)
            
            return TrendAnalysisResponse(
                trends=trends,
                total_trends=len(trends),
                analysis_date=datetime.utcnow(),
                platforms_analyzed=request.platforms,
                region=request.region,
                timeframe=request.timeframe,
                next_update=datetime.utcnow() + timedelta(hours=1)
            )
        except Exception as e:
            raise Exception(f"Error analyzing trends: {str(e)}")

    async def generate_viral_content(self, request: ViralContentRequest, user_id: str) -> ViralContentResponse:
        """Generate viral content based on current trends"""
        try:
            # Get current trends for the platform
            trends = await self._get_relevant_trends(request.platform, request.topic)
            
            # Get template if specified
            template = None
            if request.template_id:
                template = await self._get_template(request.template_id)
            else:
                template = await self._get_best_template(request.platform, request.content_type)
            
            # Generate content using AI
            content = await self._generate_content_with_ai(request, template, trends, user_id)
            
            # Generate hashtags
            hashtags = await self._generate_hashtags(request.topic, request.platform, trends)
            
            # Predict engagement
            engagement_prediction = await self._predict_engagement(content, request.platform, hashtags)
            
            # Create response
            response = ViralContentResponse(
                content=content,
                platform=request.platform,
                content_type=request.content_type,
                hashtags=hashtags,
                suggested_caption=await self._generate_caption(content, request.platform),
                optimal_post_time=await self._calculate_optimal_time(request.platform),
                engagement_prediction=engagement_prediction,
                viral_elements_used=await self._extract_viral_elements(content, template),
                trending_hooks=await self._extract_trending_hooks(content, trends),
                call_to_action=await self._generate_cta(request.platform, request.content_type),
                platform_specific_tips=await self._get_platform_tips(request.platform),
                user_id=user_id,
                topic=request.topic,
                template_used=template.template_id if template else None
            )
            
            # Save generation to database
            await self._save_generation(response, user_id)
            
            return response
        except Exception as e:
            raise Exception(f"Error generating viral content: {str(e)}")

    async def adapt_content_cross_platform(self, content: str, original_platform: SocialPlatform, 
                                         target_platforms: List[SocialPlatform]) -> CrossPlatformAdaptation:
        """Adapt content for different social media platforms"""
        try:
            adaptations = {}
            adaptation_notes = {}
            
            for platform in target_platforms:
                if platform == original_platform:
                    continue
                    
                # Adapt content for target platform
                adapted_content = await self._adapt_content_for_platform(content, platform)
                adapted_hashtags = await self._adapt_hashtags_for_platform(content, platform)
                
                adaptations[platform] = {
                    "content": adapted_content,
                    "hashtags": adapted_hashtags,
                    "max_length": self.platform_configs[platform]["max_length"],
                    "optimal_timing": self.platform_configs[platform]["best_times"],
                    "platform_features": self.platform_configs[platform]["viral_elements"]
                }
                
                adaptation_notes[platform] = await self._get_adaptation_notes(original_platform, platform)
            
            return CrossPlatformAdaptation(
                original_content=content,
                original_platform=original_platform,
                adaptations=adaptations,
                adaptation_notes=adaptation_notes
            )
        except Exception as e:
            raise Exception(f"Error adapting content cross-platform: {str(e)}")

    async def analyze_hashtags(self, hashtags: List[str], platform: SocialPlatform) -> List[HashtagAnalysis]:
        """Analyze hashtag performance and potential"""
        try:
            analyses = []
            
            for hashtag in hashtags:
                # In a real implementation, this would use actual hashtag analytics APIs
                analysis = HashtagAnalysis(
                    hashtag=hashtag,
                    platform=platform,
                    usage_count=random.randint(1000, 1000000),
                    engagement_rate=random.uniform(0.01, 0.15),
                    growth_rate=random.uniform(-0.1, 0.5),
                    difficulty_score=random.uniform(0.1, 0.9),
                    viral_potential=random.choice(list(ViralityScore)),
                    related_hashtags=await self._get_related_hashtags(hashtag, platform),
                    optimal_usage_time=self.platform_configs[platform]["best_times"],
                    audience_demographics=await self._get_hashtag_demographics(hashtag),
                    content_types=[random.choice(list(ContentType)) for _ in range(2)]
                )
                analyses.append(analysis)
            
            return analyses
        except Exception as e:
            raise Exception(f"Error analyzing hashtags: {str(e)}")

    async def get_viral_templates(self, platform: Optional[SocialPlatform] = None, 
                                content_type: Optional[ContentType] = None) -> List[ViralContentTemplate]:
        """Get available viral content templates"""
        try:
            templates = self.default_templates.copy()
            
            # Get custom templates from database
            filter_criteria = {}
            if platform:
                filter_criteria["platform"] = platform
            if content_type:
                filter_criteria["content_type"] = content_type
            
            custom_templates = []
            for template in self.db[self.templates_collection].find(filter_criteria):
                template['_id'] = str(template['_id'])
                custom_templates.append(ViralContentTemplate(**template))
            
            templates.extend(custom_templates)
            
            return templates
        except Exception as e:
            raise Exception(f"Error getting viral templates: {str(e)}")

    async def get_user_viral_content(self, user_id: str, limit: int = 50) -> List[ViralContentGeneration]:
        """Get user's viral content generations"""
        try:
            generations = []
            for gen in self.db[self.generations_collection].find({"user_id": user_id}).limit(limit):
                gen['_id'] = str(gen['_id'])
                generations.append(ViralContentGeneration(**gen))
            
            return generations
        except Exception as e:
            raise Exception(f"Error getting user viral content: {str(e)}")

    async def get_viral_content_stats(self, user_id: str) -> ViralContentStats:
        """Get viral content statistics for user"""
        try:
            # Get total generated content
            total_generated = self.db[self.generations_collection].count_documents({"user_id": user_id})
            
            # Get by platform
            by_platform = {}
            for platform in SocialPlatform:
                count = self.db[self.generations_collection].count_documents({
                    "user_id": user_id,
                    "platform": platform
                })
                by_platform[platform] = count
            
            # Get by content type
            by_content_type = {}
            for content_type in ContentType:
                count = self.db[self.generations_collection].count_documents({
                    "user_id": user_id,
                    "content_type": content_type
                })
                by_content_type[content_type] = count
            
            # Calculate average viral score
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": None, "avg_score": {"$avg": "$viral_score"}}}
            ]
            avg_result = list(self.db[self.generations_collection].aggregate(pipeline))
            avg_viral_score = avg_result[0]["avg_score"] if avg_result else 0.0
            
            # Get recent generations
            recent_generations = []
            for gen in self.db[self.generations_collection].find({"user_id": user_id}).sort("created_at", -1).limit(10):
                gen['_id'] = str(gen['_id'])
                recent_generations.append(ViralContentGeneration(**gen))
            
            return ViralContentStats(
                total_generated=total_generated,
                by_platform=by_platform,
                by_content_type=by_content_type,
                average_viral_score=avg_viral_score,
                top_performing_topics=await self._get_top_topics(user_id),
                success_rate=0.75,  # Mock success rate
                trending_hashtags=await self._get_trending_hashtags(),
                recent_generations=recent_generations
            )
        except Exception as e:
            raise Exception(f"Error getting viral content stats: {str(e)}")

    # Private helper methods
    async def _generate_mock_trends(self, request: TrendAnalysisRequest) -> List[TrendItem]:
        """Generate mock trend data for testing"""
        mock_trends = []
        
        trend_topics = [
            "AI Revolution", "Sustainable Living", "Remote Work Tips", "Fitness Challenges",
            "Food Trends", "Travel Hacks", "Tech Reviews", "DIY Projects", "Fashion Trends",
            "Mental Health", "Productivity Hacks", "Gaming", "Music Trends", "Art Challenges"
        ]
        
        for platform in request.platforms:
            for i in range(5):  # 5 trends per platform
                topic = random.choice(trend_topics)
                trend = TrendItem(
                    title=f"{topic} - {platform.value.title()}",
                    description=f"Trending topic about {topic} on {platform.value}",
                    platform=platform,
                    category=random.choice(["entertainment", "lifestyle", "technology", "education"]),
                    hashtags=[f"#{topic.replace(' ', '').lower()}", f"#{platform.value}trending", "#viral"],
                    engagement_rate=random.uniform(0.05, 0.25),
                    growth_rate=random.uniform(0.1, 2.0),
                    popularity_score=random.uniform(0.5, 1.0),
                    viral_potential=random.choice(list(ViralityScore)),
                    duration_estimate=random.choice(["1-2 days", "3-5 days", "1 week", "2 weeks"]),
                    related_sounds=["trending_audio_1", "viral_beat_2"] if platform == SocialPlatform.TIKTOK else None,
                    related_effects=["effect_1", "filter_2"] if platform in [SocialPlatform.TIKTOK, SocialPlatform.INSTAGRAM] else None,
                    examples=[f"example_url_{i}" for i in range(3)]
                )
                mock_trends.append(trend)
        
        return mock_trends[:20]  # Return top 20 trends

    async def _generate_content_with_ai(self, request: ViralContentRequest, template: ViralContentTemplate, 
                                      trends: List[TrendItem], user_id: str) -> str:
        """Generate viral content using AI"""
        try:
            # Create context from trends
            trend_context = "\n".join([f"- {trend.title}: {trend.description}" for trend in trends[:3]])
            
            # Build prompt
            prompt = f"""
            Create viral {request.content_type.value} content for {request.platform.value} about "{request.topic}".
            
            Target audience: {request.target_audience}
            Tone: {request.tone}
            Platform: {request.platform.value}
            
            Current trending topics:
            {trend_context}
            
            Template structure: {template.template_content if template else "Be creative and engaging"}
            
            Platform-specific requirements:
            - Max length: {self.platform_configs[request.platform]["max_length"]} characters
            - Best times to post: {', '.join(self.platform_configs[request.platform]["best_times"])}
            - Viral elements to include: {', '.join(self.platform_configs[request.platform]["viral_elements"])}
            
            Create content that:
            1. Hooks the audience in the first 3 seconds
            2. Uses trending elements and hashtags
            3. Includes a strong call-to-action
            4. Is optimized for {request.platform.value} algorithm
            5. Encourages engagement (likes, comments, shares)
            
            Content should be ready to post and highly engaging.
            """
            
            # Generate content using text service
            response = await self.text_service.generate_text(
                provider_name="openai",
                model="gpt-4",
                prompt=prompt,
                max_tokens=800,
                user_id=user_id
            )
            
            content = response.get('content', '').strip()
            
            # Ensure content fits platform constraints
            max_length = self.platform_configs[request.platform]["max_length"]
            if len(content) > max_length:
                content = content[:max_length-3] + "..."
            
            return content
            
        except Exception as e:
            print(f"AI content generation failed: {e}")
            # Fallback to template-based content
            return self._generate_fallback_content(request, template)

    def _generate_fallback_content(self, request: ViralContentRequest, template: ViralContentTemplate) -> str:
        """Generate fallback content when AI fails"""
        if template:
            base_content = template.template_content
            # Replace placeholders
            base_content = base_content.replace("{topic}", request.topic)
            base_content = base_content.replace("{platform}", request.platform.value)
            return base_content
        else:
            return f"🔥 {request.topic} is trending! Check out this amazing content on {request.platform.value}! #viral #trending"

    async def _generate_hashtags(self, topic: str, platform: SocialPlatform, trends: List[TrendItem]) -> List[str]:
        """Generate relevant hashtags for content"""
        hashtags = []
        
        # Add topic-based hashtags
        topic_words = topic.split()
        for word in topic_words:
            if len(word) > 2:
                hashtags.append(f"#{word.lower()}")
        
        # Add trending hashtags from trends
        for trend in trends[:2]:
            if trend.platform == platform:
                hashtags.extend(trend.hashtags[:2])
        
        # Add platform-specific hashtags
        platform_hashtags = {
            SocialPlatform.TIKTOK: ["#fyp", "#viral", "#trending"],
            SocialPlatform.INSTAGRAM: ["#reels", "#explore", "#viral"],
            SocialPlatform.YOUTUBE: ["#shorts", "#viral", "#trending"],
            SocialPlatform.TWITTER: ["#trending", "#viral", "#news"]
        }
        
        hashtags.extend(platform_hashtags.get(platform, []))
        
        # Remove duplicates and limit to optimal count
        hashtags = list(set(hashtags))
        optimal_count = self.platform_configs[platform]["optimal_hashtags"]
        return hashtags[:optimal_count]

    async def _predict_engagement(self, content: str, platform: SocialPlatform, hashtags: List[str]) -> EngagementPrediction:
        """Predict engagement metrics for content"""
        # Mock engagement prediction based on content analysis
        content_score = len(content) / self.platform_configs[platform]["max_length"]
        hashtag_score = len(hashtags) / self.platform_configs[platform]["optimal_hashtags"]
        
        base_views = random.randint(1000, 100000)
        engagement_rate = random.uniform(0.05, 0.20)
        
        return EngagementPrediction(
            predicted_views=base_views,
            predicted_likes=int(base_views * engagement_rate * 0.8),
            predicted_comments=int(base_views * engagement_rate * 0.1),
            predicted_shares=int(base_views * engagement_rate * 0.1),
            virality_score=random.uniform(0.5, 0.95),
            engagement_rate=engagement_rate,
            reach_estimate=int(base_views * 1.5),
            confidence_level=random.uniform(0.7, 0.9),
            factors=["trending_hashtags", "optimal_length", "engaging_hook", "platform_optimization"],
            recommendations=["Post during peak hours", "Use trending audio", "Add call-to-action", "Engage with comments quickly"]
        )

    async def _get_relevant_trends(self, platform: SocialPlatform, topic: str) -> List[TrendItem]:
        """Get relevant trends for platform and topic"""
        # Mock implementation - in real app, this would query the trends database
        return []

    async def _get_template(self, template_id: str) -> Optional[ViralContentTemplate]:
        """Get template by ID"""
        # Check default templates
        for template in self.default_templates:
            if template.template_id == template_id:
                return template
        
        # Check database
        template_doc = self.db[self.templates_collection].find_one({"template_id": template_id})
        if template_doc:
            template_doc['_id'] = str(template_doc['_id'])
            return ViralContentTemplate(**template_doc)
        
        return None

    async def _get_best_template(self, platform: SocialPlatform, content_type: ContentType) -> ViralContentTemplate:
        """Get best template for platform and content type"""
        # Find matching template
        for template in self.default_templates:
            if template.platform == platform and template.content_type == content_type:
                return template
        
        # Return first template for platform
        for template in self.default_templates:
            if template.platform == platform:
                return template
        
        # Return first template
        return self.default_templates[0]

    def _get_default_templates(self) -> List[ViralContentTemplate]:
        """Get default viral content templates"""
        return [
            ViralContentTemplate(
                template_id="tiktok_viral_hook",
                name="TikTok Viral Hook",
                description="High-engagement TikTok content template with viral hooks",
                platform=SocialPlatform.TIKTOK,
                content_type=ContentType.VIDEO,
                category="entertainment",
                structure={"hook": "3 seconds", "content": "main story", "cta": "engagement"},
                suggested_hashtags=["#fyp", "#viral", "#trending"],
                optimal_timing={"best_times": ["6pm", "10pm", "7am"]},
                engagement_hooks=["POV:", "Tell me you're... without telling me", "This is your sign to..."],
                call_to_action=["Follow for more!", "Save this!", "Tag someone who needs this!"],
                viral_elements=["trending_audio", "visual_effects", "quick_cuts", "text_overlay"],
                success_rate=0.85,
                template_content="🔥 {topic} - Here's what you need to know! [Hook] + [Main Content] + [CTA] #fyp #viral",
                placeholder_fields=["topic", "hook", "main_content", "cta"]
            ),
            ViralContentTemplate(
                template_id="instagram_reel_viral",
                name="Instagram Reel Viral",
                description="Instagram Reel template optimized for viral reach",
                platform=SocialPlatform.INSTAGRAM,
                content_type=ContentType.REEL,
                category="lifestyle",
                structure={"hook": "instant grab", "value": "useful info", "cta": "engagement"},
                suggested_hashtags=["#reels", "#viral", "#explore"],
                optimal_timing={"best_times": ["11am", "1pm", "5pm"]},
                engagement_hooks=["You need to see this!", "This changed everything!", "Plot twist:"],
                call_to_action=["Save this post!", "Follow for daily tips!", "Share with friends!"],
                viral_elements=["trending_audio", "quick_transitions", "text_overlay", "carousel"],
                success_rate=0.78,
                template_content="✨ {topic} ✨ [Hook] + [Value] + [CTA] 📱 #reels #viral #explore",
                placeholder_fields=["topic", "hook", "value", "cta"]
            ),
            ViralContentTemplate(
                template_id="youtube_shorts_viral",
                name="YouTube Shorts Viral",
                description="YouTube Shorts template for maximum retention",
                platform=SocialPlatform.YOUTUBE,
                content_type=ContentType.SHORT,
                category="education",
                structure={"hook": "question/promise", "content": "quick delivery", "retention": "keep watching"},
                suggested_hashtags=["#shorts", "#viral", "#trending"],
                optimal_timing={"best_times": ["2pm", "3pm", "9pm"]},
                engagement_hooks=["Watch until the end!", "You won't believe what happens next!", "This will blow your mind!"],
                call_to_action=["Subscribe for more!", "Like if you learned something!", "Comment your thoughts!"],
                viral_elements=["strong_hook", "quick_pacing", "visual_storytelling", "cliffhanger"],
                success_rate=0.82,
                template_content="🎯 {topic} 🎯 [Hook] + [Quick Content] + [Retention Element] #shorts #viral",
                placeholder_fields=["topic", "hook", "quick_content", "retention_element"]
            ),
            ViralContentTemplate(
                template_id="twitter_viral_thread",
                name="Twitter Viral Thread",
                description="Twitter thread template for viral engagement",
                platform=SocialPlatform.TWITTER,
                content_type=ContentType.TEXT,
                category="news",
                structure={"hook_tweet": "attention grabber", "thread": "valuable info", "cta": "retweet"},
                suggested_hashtags=["#thread", "#viral", "#trending"],
                optimal_timing={"best_times": ["9am", "1pm", "3pm"]},
                engagement_hooks=["🧵 Thread:", "This is important:", "Everyone needs to know:"],
                call_to_action=["RT to spread awareness!", "Follow for more insights!", "What are your thoughts?"],
                viral_elements=["controversy", "valuable_info", "timely_topics", "engagement_bait"],
                success_rate=0.72,
                template_content="🧵 {topic} - A thread you need to read: [Hook] + [Thread content] + [CTA] #thread #viral",
                placeholder_fields=["topic", "hook", "thread_content", "cta"]
            )
        ]

    async def _save_trends(self, trends: List[TrendItem]):
        """Save trends to database"""
        try:
            for trend in trends:
                trend_doc = trend.dict()
                # Update existing or insert new
                self.db[self.trends_collection].update_one(
                    {"trend_id": trend.trend_id},
                    {"$set": trend_doc},
                    upsert=True
                )
        except Exception as e:
            print(f"Error saving trends: {e}")

    async def _save_generation(self, response: ViralContentResponse, user_id: str):
        """Save generation to database"""
        try:
            generation = ViralContentGeneration(
                user_id=user_id,
                topic=response.topic,
                platform=response.platform,
                content_type=response.content_type,
                content=response.content,
                hashtags=response.hashtags,
                engagement_prediction=response.engagement_prediction,
                viral_score=response.engagement_prediction.virality_score,
                trend_alignment=random.uniform(0.5, 0.9)
            )
            
            generation_doc = generation.dict()
            self.db[self.generations_collection].insert_one(generation_doc)
        except Exception as e:
            print(f"Error saving generation: {e}")

    async def _generate_caption(self, content: str, platform: SocialPlatform) -> str:
        """Generate suggested caption for content"""
        # Extract first sentence or key phrase
        sentences = content.split('.')
        if sentences:
            return sentences[0].strip() + "..."
        return content[:100] + "..."

    async def _calculate_optimal_time(self, platform: SocialPlatform) -> datetime:
        """Calculate optimal posting time"""
        now = datetime.utcnow()
        best_times = self.platform_configs[platform]["best_times"]
        
        # For demo, return next optimal time
        next_time = now.replace(hour=18, minute=0, second=0, microsecond=0)  # 6 PM UTC
        return next_time

    async def _extract_viral_elements(self, content: str, template: ViralContentTemplate) -> List[str]:
        """Extract viral elements used in content"""
        if template:
            return template.viral_elements
        return ["engaging_hook", "trending_topic", "call_to_action"]

    async def _extract_trending_hooks(self, content: str, trends: List[TrendItem]) -> List[str]:
        """Extract trending hooks from content"""
        hooks = []
        for trend in trends:
            if any(hashtag.replace('#', '').lower() in content.lower() for hashtag in trend.hashtags):
                hooks.append(trend.title)
        return hooks[:3]

    async def _generate_cta(self, platform: SocialPlatform, content_type: ContentType) -> str:
        """Generate call-to-action for platform"""
        ctas = {
            SocialPlatform.TIKTOK: ["Follow for more!", "Save this!", "Tag someone!"],
            SocialPlatform.INSTAGRAM: ["Save this post!", "Follow for daily tips!", "Share with friends!"],
            SocialPlatform.YOUTUBE: ["Subscribe for more!", "Like if you learned something!", "Comment your thoughts!"],
            SocialPlatform.TWITTER: ["RT to spread awareness!", "Follow for more insights!", "What are your thoughts?"]
        }
        
        platform_ctas = ctas.get(platform, ["Engage with this post!"])
        return random.choice(platform_ctas)

    async def _get_platform_tips(self, platform: SocialPlatform) -> List[str]:
        """Get platform-specific tips"""
        tips = {
            SocialPlatform.TIKTOK: [
                "Use trending audio for better reach",
                "Hook viewers in first 3 seconds",
                "Post during peak hours (6-10 PM)",
                "Use trending hashtags and effects"
            ],
            SocialPlatform.INSTAGRAM: [
                "Use high-quality visuals",
                "Post consistently at optimal times",
                "Engage with comments quickly",
                "Use relevant hashtags and location tags"
            ],
            SocialPlatform.YOUTUBE: [
                "Create eye-catching thumbnails",
                "Use strong titles with keywords",
                "Keep viewers engaged throughout",
                "Optimize for search and discovery"
            ],
            SocialPlatform.TWITTER: [
                "Tweet during peak engagement hours",
                "Use relevant trending hashtags",
                "Create engaging threads",
                "Respond to comments and mentions"
            ]
        }
        
        return tips.get(platform, ["Create engaging content!"])

    async def _adapt_content_for_platform(self, content: str, platform: SocialPlatform) -> str:
        """Adapt content for specific platform"""
        max_length = self.platform_configs[platform]["max_length"]
        
        if len(content) > max_length:
            # Truncate and add platform-specific ending
            truncated = content[:max_length-20]
            if platform == SocialPlatform.TWITTER:
                return truncated + "... (thread 🧵)"
            elif platform == SocialPlatform.TIKTOK:
                return truncated + "... 🔥"
            else:
                return truncated + "..."
        
        return content

    async def _adapt_hashtags_for_platform(self, content: str, platform: SocialPlatform) -> List[str]:
        """Adapt hashtags for specific platform"""
        base_hashtags = ["#viral", "#trending"]
        
        platform_hashtags = {
            SocialPlatform.TIKTOK: ["#fyp", "#viral", "#trending"],
            SocialPlatform.INSTAGRAM: ["#reels", "#explore", "#viral"],
            SocialPlatform.YOUTUBE: ["#shorts", "#viral", "#trending"],
            SocialPlatform.TWITTER: ["#trending", "#viral", "#news"]
        }
        
        return platform_hashtags.get(platform, base_hashtags)

    async def _get_adaptation_notes(self, original: SocialPlatform, target: SocialPlatform) -> List[str]:
        """Get notes for platform adaptation"""
        return [
            f"Adapted from {original.value} to {target.value}",
            f"Adjusted for {target.value} audience and format",
            f"Optimized for {target.value} algorithm"
        ]

    async def _get_related_hashtags(self, hashtag: str, platform: SocialPlatform) -> List[str]:
        """Get related hashtags"""
        # Mock related hashtags
        return [f"#{hashtag}tips", f"#{hashtag}hacks", f"#{hashtag}viral"]

    async def _get_hashtag_demographics(self, hashtag: str) -> Dict[str, Any]:
        """Get hashtag demographics"""
        return {
            "age_groups": {"18-24": 30, "25-34": 40, "35-44": 20, "45+": 10},
            "gender": {"male": 45, "female": 55},
            "locations": {"US": 40, "EU": 30, "Asia": 20, "Other": 10}
        }

    async def _get_top_topics(self, user_id: str) -> List[str]:
        """Get top performing topics for user"""
        # Mock top topics
        return ["Technology", "Lifestyle", "Entertainment", "Education", "Health"]

    async def _get_trending_hashtags(self) -> List[str]:
        """Get current trending hashtags"""
        return ["#viral", "#trending", "#fyp", "#explore", "#reels", "#shorts"]