import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

class TestAPIEndpoints:
    
    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_root_endpoint(self, test_client):
        """Test root endpoint"""
        response = test_client.get("/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "ContentForge AI API"
        assert data["version"] == "1.0.0"
    
    @patch('utils.database.users_collection')
    def test_register_endpoint(self, mock_users_collection, test_client):
        """Test user registration endpoint"""
        mock_users_collection.find_one.return_value = None
        mock_users_collection.insert_one.return_value = Mock()
        
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        
        with patch('services.auth_service.create_access_token') as mock_token:
            mock_token.return_value = "test-token"
            
            response = test_client.post("/api/auth/register", json=user_data)
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "test-token"
            assert data["token_type"] == "bearer"
    
    @patch('utils.database.users_collection')
    def test_login_endpoint(self, mock_users_collection, test_client):
        """Test user login endpoint"""
        mock_users_collection.find_one.return_value = {
            "username": "testuser",
            "hashed_password": "hashed_password"
        }
        
        user_data = {
            "username": "testuser",
            "password": "password123"
        }
        
        with patch('services.auth_service.verify_password') as mock_verify, \
             patch('services.auth_service.create_access_token') as mock_token:
            mock_verify.return_value = True
            mock_token.return_value = "test-token"
            
            response = test_client.post("/api/auth/login", json=user_data)
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "test-token"
            assert data["token_type"] == "bearer"
    
    @patch('utils.database.users_collection')
    def test_get_current_user_endpoint(self, mock_users_collection, test_client):
        """Test get current user endpoint"""
        mock_users_collection.find_one.return_value = {
            "user_id": "test-user-id",
            "username": "testuser",
            "email": "test@example.com",
            "is_admin": False,
            "created_at": "2023-01-01T00:00:00"
        }
        
        with patch('utils.auth_utils.get_current_user') as mock_get_user:
            mock_get_user.return_value = "testuser"
            
            response = test_client.get("/api/auth/me", headers={"Authorization": "Bearer test-token"})
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "testuser"
            assert data["email"] == "test@example.com"
    
    @patch('utils.database.providers_collection')
    def test_get_active_providers_endpoint(self, mock_providers_collection, test_client):
        """Test get active providers endpoint"""
        mock_providers_collection.find.return_value = [
            {
                "provider_id": "test-provider-id",
                "name": "test-provider",
                "description": "Test provider",
                "models": ["test-model"],
                "provider_type": "text"
            }
        ]
        
        with patch('utils.auth_utils.get_current_user') as mock_get_user:
            mock_get_user.return_value = "testuser"
            
            response = test_client.get("/api/providers", headers={"Authorization": "Bearer test-token"})
            assert response.status_code == 200
            data = response.json()
            assert len(data["providers"]) == 1
            assert data["providers"][0]["name"] == "test-provider"
    
    @patch('utils.database.providers_collection')
    def test_get_text_providers_endpoint(self, mock_providers_collection, test_client):
        """Test get text providers endpoint"""
        mock_providers_collection.find.return_value = [
            {
                "provider_id": "test-provider-id",
                "name": "test-provider",
                "description": "Test provider",
                "models": ["test-model"]
            }
        ]
        
        with patch('utils.auth_utils.get_current_user') as mock_get_user:
            mock_get_user.return_value = "testuser"
            
            response = test_client.get("/api/providers/text", headers={"Authorization": "Bearer test-token"})
            assert response.status_code == 200
            data = response.json()
            assert len(data["providers"]) == 1
            assert data["providers"][0]["name"] == "test-provider"
    
    @patch('utils.database.providers_collection')
    @patch('utils.database.users_collection')
    def test_admin_add_provider_endpoint(self, mock_users_collection, mock_providers_collection, test_client):
        """Test admin add provider endpoint"""
        mock_users_collection.find_one.return_value = {
            "username": "admin",
            "is_admin": True
        }
        mock_providers_collection.insert_one.return_value = Mock()
        
        provider_data = {
            "name": "test-provider",
            "description": "Test provider",
            "base_url": "https://api.test.com",
            "headers": {"Authorization": "Bearer test-key"},
            "request_body_template": {"model": "{model}", "prompt": "{prompt}"},
            "response_parser": {"content_path": "choices.0.message.content"},
            "models": ["test-model"],
            "provider_type": "text",
            "is_active": True
        }
        
        with patch('utils.auth_utils.get_current_user') as mock_get_user:
            mock_get_user.return_value = "admin"
            
            response = test_client.post("/api/admin/providers", json=provider_data, headers={"Authorization": "Bearer admin-token"})
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Provider added successfully"
            assert "provider_id" in data
    
    @patch('utils.database.providers_collection')
    @patch('utils.database.users_collection')
    def test_admin_get_all_providers_endpoint(self, mock_users_collection, mock_providers_collection, test_client):
        """Test admin get all providers endpoint"""
        mock_users_collection.find_one.return_value = {
            "username": "admin",
            "is_admin": True
        }
        mock_providers_collection.find.return_value = [
            {
                "provider_id": "test-provider-id",
                "name": "test-provider",
                "description": "Test provider",
                "models": ["test-model"],
                "provider_type": "text"
            }
        ]
        
        with patch('utils.auth_utils.get_current_user') as mock_get_user:
            mock_get_user.return_value = "admin"
            
            response = test_client.get("/api/admin/providers", headers={"Authorization": "Bearer admin-token"})
            assert response.status_code == 200
            data = response.json()
            assert len(data["providers"]) == 1
            assert data["providers"][0]["name"] == "test-provider"
    
    @patch('utils.database.users_collection')
    def test_non_admin_access_admin_endpoint(self, mock_users_collection, test_client):
        """Test non-admin user accessing admin endpoint"""
        mock_users_collection.find_one.return_value = {
            "username": "testuser",
            "is_admin": False
        }
        
        with patch('utils.auth_utils.get_current_user') as mock_get_user:
            mock_get_user.return_value = "testuser"
            
            response = test_client.get("/api/admin/providers", headers={"Authorization": "Bearer test-token"})
            assert response.status_code == 403
            data = response.json()
            assert "Admin access required" in data["detail"]