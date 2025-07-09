import pytest
import asyncio
from fastapi.testclient import TestClient
from pymongo import MongoClient
from unittest.mock import Mock, patch
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_db():
    """Mock MongoDB collections for testing"""
    with patch('utils.database.users_collection') as mock_users, \
         patch('utils.database.providers_collection') as mock_providers, \
         patch('utils.database.conversations_collection') as mock_conversations, \
         patch('utils.database.generations_collection') as mock_generations, \
         patch('utils.database.image_generations_collection') as mock_image_gen, \
         patch('utils.database.video_generations_collection') as mock_video_gen:
        
        yield {
            'users': mock_users,
            'providers': mock_providers,
            'conversations': mock_conversations,
            'generations': mock_generations,
            'image_generations': mock_image_gen,
            'video_generations': mock_video_gen
        }

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application"""
    from server_new import app
    return TestClient(app)

@pytest.fixture
def mock_auth_user():
    """Mock authenticated user for testing"""
    test_user = {
        "user_id": "test-user-id",
        "username": "testuser",
        "email": "test@example.com",
        "is_admin": False,
        "created_at": "2023-01-01T00:00:00",
        "is_active": True
    }
    return test_user

@pytest.fixture
def mock_admin_user():
    """Mock admin user for testing"""
    admin_user = {
        "user_id": "admin-user-id",
        "username": "admin",
        "email": "admin@example.com",
        "is_admin": True,
        "created_at": "2023-01-01T00:00:00",
        "is_active": True
    }
    return admin_user

@pytest.fixture
def mock_provider():
    """Mock provider for testing"""
    provider = {
        "provider_id": "test-provider-id",
        "name": "test-provider",
        "description": "Test provider description",
        "base_url": "https://api.example.com",
        "headers": {"Authorization": "Bearer test-key"},
        "request_body_template": {
            "model": "{model}",
            "prompt": "{prompt}",
            "max_tokens": "{max_tokens}",
            "temperature": "{temperature}"
        },
        "response_parser": {"content_path": "choices.0.message.content"},
        "models": ["test-model-1", "test-model-2"],
        "provider_type": "text",
        "is_active": True,
        "created_at": "2023-01-01T00:00:00",
        "created_by": "admin"
    }
    return provider