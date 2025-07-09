import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from services.provider_service import ProviderService
from models.provider_models import LLMProvider, CurlProvider

class TestProviderService:
    
    @pytest.mark.asyncio
    async def test_add_provider_success(self, mock_db):
        """Test successful provider addition"""
        provider_data = LLMProvider(
            name="test-provider",
            description="Test provider",
            base_url="https://api.test.com",
            headers={"Authorization": "Bearer test-key"},
            request_body_template={"model": "{model}", "prompt": "{prompt}"},
            response_parser={"content_path": "choices.0.message.content"},
            models=["test-model"],
            provider_type="text",
            is_active=True
        )
        
        mock_db['providers'].insert_one.return_value = Mock()
        
        result = await ProviderService.add_provider(provider_data, "admin")
        
        assert result["message"] == "Provider added successfully"
        assert "provider_id" in result
        mock_db['providers'].insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_provider_from_curl_success(self, mock_db):
        """Test successful provider addition from curl command"""
        provider_data = CurlProvider(
            name="test-provider",
            description="Test provider",
            curl_command='curl -X POST "https://api.test.com" -H "Authorization: Bearer test-key" -d \'{"model": "test-model", "prompt": "test"}\'',
            models=["test-model"],
            provider_type="text",
            is_active=True
        )
        
        mock_db['providers'].insert_one.return_value = Mock()
        
        with patch('services.provider_service.parse_curl_command') as mock_parse:
            mock_parse.return_value = {
                "base_url": "https://api.test.com",
                "headers": {"Authorization": "Bearer test-key"},
                "request_body_template": {"model": "{model}", "prompt": "{prompt}"},
                "response_parser": {"content_path": "choices.0.message.content"}
            }
            
            result = await ProviderService.add_provider_from_curl(provider_data, "admin")
            
            assert result["message"] == "Provider added successfully from curl command"
            assert "provider_id" in result
            mock_db['providers'].insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_providers(self, mock_db, mock_provider):
        """Test getting all providers"""
        mock_db['providers'].find.return_value = [mock_provider]
        
        result = await ProviderService.get_all_providers()
        
        assert len(result) == 1
        assert result[0]["name"] == "test-provider"
    
    @pytest.mark.asyncio
    async def test_get_active_providers(self, mock_db, mock_provider):
        """Test getting active providers"""
        mock_db['providers'].find.return_value = [mock_provider]
        
        result = await ProviderService.get_active_providers()
        
        assert len(result) == 1
        assert result[0]["name"] == "test-provider"
    
    @pytest.mark.asyncio
    async def test_get_providers_by_type(self, mock_db, mock_provider):
        """Test getting providers by type"""
        mock_db['providers'].find.return_value = [mock_provider]
        
        result = await ProviderService.get_providers_by_type("text")
        
        assert len(result) == 1
        assert result[0]["name"] == "test-provider"
    
    @pytest.mark.asyncio
    async def test_update_provider_success(self, mock_db):
        """Test successful provider update"""
        provider_data = LLMProvider(
            name="updated-provider",
            description="Updated provider",
            base_url="https://api.updated.com",
            headers={"Authorization": "Bearer updated-key"},
            request_body_template={"model": "{model}", "prompt": "{prompt}"},
            response_parser={"content_path": "choices.0.message.content"},
            models=["updated-model"],
            provider_type="text",
            is_active=True
        )
        
        mock_db['providers'].update_one.return_value = Mock(matched_count=1)
        
        result = await ProviderService.update_provider("test-provider-id", provider_data)
        
        assert result["message"] == "Provider updated successfully"
        mock_db['providers'].update_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_provider_not_found(self, mock_db):
        """Test updating non-existent provider"""
        provider_data = LLMProvider(
            name="updated-provider",
            description="Updated provider",
            base_url="https://api.updated.com",
            headers={"Authorization": "Bearer updated-key"},
            request_body_template={"model": "{model}", "prompt": "{prompt}"},
            response_parser={"content_path": "choices.0.message.content"},
            models=["updated-model"],
            provider_type="text",
            is_active=True
        )
        
        mock_db['providers'].update_one.return_value = Mock(matched_count=0)
        
        with pytest.raises(HTTPException) as exc_info:
            await ProviderService.update_provider("nonexistent-id", provider_data)
        
        assert exc_info.value.status_code == 404
        assert "Provider not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_delete_provider_success(self, mock_db):
        """Test successful provider deletion"""
        mock_db['providers'].delete_one.return_value = Mock(deleted_count=1)
        
        result = await ProviderService.delete_provider("test-provider-id")
        
        assert result["message"] == "Provider deleted successfully"
        mock_db['providers'].delete_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_provider_not_found(self, mock_db):
        """Test deleting non-existent provider"""
        mock_db['providers'].delete_one.return_value = Mock(deleted_count=0)
        
        with pytest.raises(HTTPException) as exc_info:
            await ProviderService.delete_provider("nonexistent-id")
        
        assert exc_info.value.status_code == 404
        assert "Provider not found" in str(exc_info.value.detail)
    
    def test_get_provider_by_name(self, mock_db, mock_provider):
        """Test getting provider by name"""
        mock_db['providers'].find_one.return_value = mock_provider
        
        result = ProviderService.get_provider_by_name("test-provider")
        
        assert result["name"] == "test-provider"
        mock_db['providers'].find_one.assert_called_once_with({"name": "test-provider", "is_active": True})