import requests
import json
import unittest
import os
import sys
from typing import Dict, Any

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://aad38467-9efd-4d4d-b55d-870032e69899.preview.emergentagent.com"

class CodeGenerationAPITest(unittest.TestCase):
    """Test suite for Code Generation API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = f"{BACKEND_URL}/api"
        self.auth_token = None
        self.login()
    
    def login(self):
        """Login to get authentication token"""
        login_url = f"{self.base_url}/auth/login"
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access_token")
            print(f"Successfully logged in as admin. Token: {self.auth_token[:10]}...")
        else:
            print(f"Failed to login: {response.status_code} - {response.text}")
            self.fail("Login failed")
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_01_get_providers(self):
        """Test GET /api/code/providers endpoint"""
        print("\n=== Testing GET /api/code/providers ===")
        url = f"{self.base_url}/code/providers"
        response = requests.get(url)
        
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list")
        self.assertGreaterEqual(len(data), 3, "Should return at least 3 providers")
        
        # Check for required providers
        provider_names = [provider["provider"] for provider in data]
        self.assertIn("openai", provider_names, "OpenAI provider should be available")
        self.assertIn("anthropic", provider_names, "Anthropic provider should be available")
        self.assertIn("gemini", provider_names, "Gemini provider should be available")
        
        # Check provider structure
        for provider in data:
            self.assertIn("provider", provider, "Provider should have 'provider' field")
            self.assertIn("name", provider, "Provider should have 'name' field")
            self.assertIn("models", provider, "Provider should have 'models' field")
            self.assertIsInstance(provider["models"], list, "Models should be a list")
            
            # Check model structure
            for model in provider["models"]:
                self.assertIn("id", model, "Model should have 'id' field")
                self.assertIn("name", model, "Model should have 'name' field")
                self.assertIn("description", model, "Model should have 'description' field")
        
        print(f"✅ GET /api/code/providers returned {len(data)} providers")
        for provider in data:
            print(f"  - {provider['name']} with {len(provider['models'])} models")
    
    def test_02_get_languages(self):
        """Test GET /api/code/languages endpoint"""
        print("\n=== Testing GET /api/code/languages ===")
        url = f"{self.base_url}/code/languages"
        response = requests.get(url)
        
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list")
        self.assertGreaterEqual(len(data), 20, "Should return at least 20 programming languages")
        
        # Check language structure
        for language in data:
            self.assertIn("id", language, "Language should have 'id' field")
            self.assertIn("name", language, "Language should have 'name' field")
            self.assertIn("extension", language, "Language should have 'extension' field")
        
        # Check for common languages
        language_ids = [lang["id"] for lang in data]
        common_languages = ["python", "javascript", "java", "cpp", "csharp"]
        for lang in common_languages:
            self.assertIn(lang, language_ids, f"{lang} should be in the supported languages")
        
        print(f"✅ GET /api/code/languages returned {len(data)} languages")
        print(f"  Languages include: {', '.join([lang['name'] for lang in data[:5]])} and more...")
    
    def test_03_get_request_types(self):
        """Test GET /api/code/request-types endpoint"""
        print("\n=== Testing GET /api/code/request-types ===")
        url = f"{self.base_url}/code/request-types"
        response = requests.get(url)
        
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list")
        
        # Check for required request types
        expected_types = ["generate", "debug", "optimize", "refactor", "review", 
                         "documentation", "test", "explain", "architecture"]
        
        request_type_ids = [rt["id"] for rt in data]
        for req_type in expected_types:
            self.assertIn(req_type, request_type_ids, f"{req_type} should be in the request types")
        
        # Check request type structure
        for req_type in data:
            self.assertIn("id", req_type, "Request type should have 'id' field")
            self.assertIn("name", req_type, "Request type should have 'name' field")
            self.assertIn("description", req_type, "Request type should have 'description' field")
        
        print(f"✅ GET /api/code/request-types returned {len(data)} request types")
        for rt in data:
            print(f"  - {rt['name']}: {rt['description']}")
    
    def test_04_generate_code(self):
        """Test POST /api/code/generate endpoint"""
        print("\n=== Testing POST /api/code/generate ===")
        url = f"{self.base_url}/code/generate"
        
        # Test data
        request_data = {
            "provider": "openai",
            "model": "gpt-4o",
            "request_type": "generate",
            "language": "python",
            "prompt": "Write a function to calculate the Fibonacci sequence up to n terms",
            "max_tokens": 1000
        }
        
        # Test without authentication
        response = requests.post(url, json=request_data)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.post(url, json=request_data, headers=self.get_headers())
        
        # Note: In a test environment, the actual code generation might fail due to missing API keys
        # We're just checking that the endpoint processes the request correctly
        self.assertIn(response.status_code, [200, 500], 
                     f"Expected status code 200 or 500 (if API key missing), got {response.status_code}")
        
        data = response.json()
        
        if response.status_code == 200:
            # If successful, check response structure
            self.assertIn("id", data, "Response should have 'id' field")
            self.assertIn("session_id", data, "Response should have 'session_id' field")
            self.assertIn("provider", data, "Response should have 'provider' field")
            self.assertIn("model", data, "Response should have 'model' field")
            self.assertIn("request_type", data, "Response should have 'request_type' field")
            self.assertIn("language", data, "Response should have 'language' field")
            self.assertIn("prompt", data, "Response should have 'prompt' field")
            self.assertIn("response", data, "Response should have 'response' field")
            self.assertIn("status", data, "Response should have 'status' field")
            
            print(f"✅ POST /api/code/generate successful")
            print(f"  Generated code with ID: {data['id']}")
            print(f"  Session ID: {data['session_id']}")
            print(f"  Status: {data['status']}")
        else:
            # If failed due to missing API key, that's expected in test environment
            print(f"⚠️ POST /api/code/generate returned error (likely due to missing API key in test environment)")
            print(f"  Error: {data.get('detail', 'Unknown error')}")
            # Don't fail the test if it's just missing API key
            if "API key not configured" in str(data):
                print("  This is expected in test environment without real API keys")
            else:
                self.fail(f"Unexpected error: {data}")
    
    def test_05_get_history(self):
        """Test GET /api/code/history endpoint"""
        print("\n=== Testing GET /api/code/history ===")
        url = f"{self.base_url}/code/history"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.get(url, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list")
        
        print(f"✅ GET /api/code/history returned {len(data)} items")
        if len(data) > 0:
            print(f"  First history item: {data[0].get('id', 'Unknown ID')}")
            print(f"  Language: {data[0].get('language', 'Unknown')}")
            print(f"  Request type: {data[0].get('request_type', 'Unknown')}")
        else:
            print("  No history items found (this is normal if no code has been generated yet)")

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)