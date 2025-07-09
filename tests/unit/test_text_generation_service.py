import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from services.text_generation_service import TextGenerationService
from models.generation_models import TextGenerationRequest

class TestTextGenerationService:
    
    @pytest.mark.asyncio
    async def test_generate_text_with_groq_success(self, mock_db):
        """Test successful text generation with Groq"""
        request = TextGenerationRequest(
            provider_name="groq",
            model="llama3-8b-8192",
            prompt="Hello, how are you?",
            max_tokens=100,
            temperature=0.7
        )
        
        # Mock existing conversation
        mock_db['conversations'].find_one.return_value = {
            "session_id": "test-session",
            "user_id": "testuser",
            "messages": []
        }
        
        mock_db['conversations'].update_one.return_value = Mock()
        mock_db['generations'].insert_one.return_value = Mock()
        
        with patch('services.text_generation_service.GROQ_API_KEY', 'test-key'), \
             patch('services.text_generation_service.Groq') as mock_groq:
            
            mock_client = Mock()
            mock_groq.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Hello! I'm doing well, thank you for asking."))]
            mock_client.chat.completions.create.return_value = mock_response
            
            result = await TextGenerationService.generate_text(request, "testuser")
            
            assert result["generated_content"] == "Hello! I'm doing well, thank you for asking."
            assert result["provider"] == "groq"
            assert result["model"] == "llama3-8b-8192"
            assert "session_id" in result
    
    @pytest.mark.asyncio
    async def test_generate_text_with_custom_provider_success(self, mock_db):
        """Test successful text generation with custom provider"""
        request = TextGenerationRequest(
            provider_name="custom-provider",
            model="custom-model",
            prompt="Hello, how are you?",
            max_tokens=100,
            temperature=0.7
        )
        
        # Mock provider configuration
        mock_provider = {
            "name": "custom-provider",
            "base_url": "https://api.custom.com",
            "headers": {"Authorization": "Bearer custom-key"},
            "request_body_template": {
                "model": "{model}",
                "messages": [{"role": "user", "content": "{prompt}"}],
                "max_tokens": "{max_tokens}",
                "temperature": "{temperature}"
            },
            "response_parser": {"content_path": "choices.0.message.content"},
            "models": ["custom-model"],
            "is_active": True
        }
        
        mock_db['providers'].find_one.return_value = mock_provider
        mock_db['conversations'].find_one.return_value = {
            "session_id": "test-session",
            "user_id": "testuser",
            "messages": []
        }
        mock_db['conversations'].update_one.return_value = Mock()
        mock_db['generations'].insert_one.return_value = Mock()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Hello! I'm doing well, thank you for asking."}}]
            }
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await TextGenerationService.generate_text(request, "testuser")
            
            assert result["generated_content"] == "Hello! I'm doing well, thank you for asking."
            assert result["provider"] == "custom-provider"
            assert result["model"] == "custom-model"
    
    @pytest.mark.asyncio
    async def test_generate_text_provider_not_found(self, mock_db):
        """Test text generation with non-existent provider"""
        request = TextGenerationRequest(
            provider_name="nonexistent-provider",
            model="some-model",
            prompt="Hello, how are you?",
            max_tokens=100,
            temperature=0.7
        )
        
        mock_db['providers'].find_one.return_value = None
        mock_db['conversations'].find_one.return_value = {
            "session_id": "test-session",
            "user_id": "testuser",
            "messages": []
        }
        
        with patch('services.text_generation_service.GROQ_API_KEY', ''):
            with pytest.raises(HTTPException) as exc_info:
                await TextGenerationService.generate_text(request, "testuser")
            
            assert exc_info.value.status_code == 404
            assert "Provider not found or inactive" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_generate_text_model_not_supported(self, mock_db):
        """Test text generation with unsupported model"""
        request = TextGenerationRequest(
            provider_name="custom-provider",
            model="unsupported-model",
            prompt="Hello, how are you?",
            max_tokens=100,
            temperature=0.7
        )
        
        mock_provider = {
            "name": "custom-provider",
            "models": ["supported-model"],
            "is_active": True
        }
        
        mock_db['providers'].find_one.return_value = mock_provider
        mock_db['conversations'].find_one.return_value = {
            "session_id": "test-session",
            "user_id": "testuser",
            "messages": []
        }
        
        with patch('services.text_generation_service.GROQ_API_KEY', ''):
            with pytest.raises(HTTPException) as exc_info:
                await TextGenerationService.generate_text(request, "testuser")
            
            assert exc_info.value.status_code == 400
            assert "Model not supported by this provider" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_conversation_success(self, mock_db):
        """Test successful conversation retrieval"""
        mock_conversation = {
            "session_id": "test-session",
            "user_id": "testuser",
            "messages": [
                {"role": "user", "content": "Hello", "timestamp": "2023-01-01T00:00:00"},
                {"role": "assistant", "content": "Hi there!", "timestamp": "2023-01-01T00:00:01"}
            ]
        }
        
        mock_db['conversations'].find_one.return_value = mock_conversation
        
        result = await TextGenerationService.get_conversation("test-session", "testuser")
        
        assert result["session_id"] == "test-session"
        assert len(result["messages"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_conversation_not_found(self, mock_db):
        """Test conversation retrieval when not found"""
        mock_db['conversations'].find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await TextGenerationService.get_conversation("nonexistent-session", "testuser")
        
        assert exc_info.value.status_code == 404
        assert "Conversation not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_user_conversations(self, mock_db):
        """Test getting user conversations"""
        mock_conversations = [
            {"session_id": "session1", "created_at": "2023-01-01T00:00:00"},
            {"session_id": "session2", "created_at": "2023-01-02T00:00:00"}
        ]
        
        mock_db['conversations'].find.return_value.sort.return_value = mock_conversations
        
        result = await TextGenerationService.get_user_conversations("testuser")
        
        assert len(result["conversations"]) == 2
        assert result["conversations"][0]["session_id"] == "session1"
    
    @pytest.mark.asyncio
    async def test_get_user_generations(self, mock_db):
        """Test getting user generations"""
        mock_generations = [
            {"generation_id": "gen1", "prompt": "Hello", "generated_content": "Hi there!"},
            {"generation_id": "gen2", "prompt": "How are you?", "generated_content": "I'm doing well!"}
        ]
        
        mock_db['generations'].find.return_value.sort.return_value.limit.return_value = mock_generations
        
        result = await TextGenerationService.get_user_generations("testuser")
        
        assert len(result["generations"]) == 2
        assert result["generations"][0]["generation_id"] == "gen1"