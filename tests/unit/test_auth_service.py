import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from services.auth_service import AuthService
from models.user_models import UserCreate, UserLogin

class TestAuthService:
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, mock_db):
        """Test successful user registration"""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        # Mock database queries
        mock_db['users'].find_one.return_value = None  # No existing user
        mock_db['users'].insert_one.return_value = Mock()
        
        with patch('services.auth_service.create_access_token') as mock_token:
            mock_token.return_value = "test-token"
            
            result = await AuthService.register_user(user_data)
            
            assert result["access_token"] == "test-token"
            assert result["token_type"] == "bearer"
            mock_db['users'].insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_user_username_exists(self, mock_db):
        """Test registration with existing username"""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        # Mock existing user
        mock_db['users'].find_one.return_value = {"username": "testuser"}
        
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.register_user(user_data)
        
        assert exc_info.value.status_code == 400
        assert "Username already registered" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_login_user_success(self, mock_db):
        """Test successful user login"""
        user_data = UserLogin(username="testuser", password="password123")
        
        # Mock user in database
        mock_db['users'].find_one.return_value = {
            "username": "testuser",
            "hashed_password": "hashed_password"
        }
        
        with patch('services.auth_service.verify_password') as mock_verify, \
             patch('services.auth_service.create_access_token') as mock_token:
            mock_verify.return_value = True
            mock_token.return_value = "test-token"
            
            result = await AuthService.login_user(user_data)
            
            assert result["access_token"] == "test-token"
            assert result["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_user_invalid_credentials(self, mock_db):
        """Test login with invalid credentials"""
        user_data = UserLogin(username="testuser", password="wrongpassword")
        
        # Mock user in database
        mock_db['users'].find_one.return_value = {
            "username": "testuser",
            "hashed_password": "hashed_password"
        }
        
        with patch('services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = False
            
            with pytest.raises(HTTPException) as exc_info:
                await AuthService.login_user(user_data)
            
            assert exc_info.value.status_code == 401
            assert "Incorrect username or password" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_current_user_info_success(self, mock_db, mock_auth_user):
        """Test getting current user info"""
        mock_db['users'].find_one.return_value = mock_auth_user
        
        result = await AuthService.get_current_user_info("testuser")
        
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        assert result.is_admin == False
    
    @pytest.mark.asyncio
    async def test_get_current_user_info_not_found(self, mock_db):
        """Test getting current user info when user not found"""
        mock_db['users'].find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.get_current_user_info("nonexistent")
        
        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)
    
    def test_is_admin_true(self, mock_db, mock_admin_user):
        """Test is_admin returns True for admin user"""
        mock_db['users'].find_one.return_value = mock_admin_user
        
        result = AuthService.is_admin("admin")
        
        assert result == True
    
    def test_is_admin_false(self, mock_db, mock_auth_user):
        """Test is_admin returns False for regular user"""
        mock_db['users'].find_one.return_value = mock_auth_user
        
        result = AuthService.is_admin("testuser")
        
        assert result == False
    
    def test_is_admin_user_not_found(self, mock_db):
        """Test is_admin returns False when user not found"""
        mock_db['users'].find_one.return_value = None
        
        result = AuthService.is_admin("nonexistent")
        
        assert result == False