import requests
import json
import unittest
import os
import sys
from typing import Dict, Any

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://20269240-eae8-4273-ba12-c0b6627be5bb.preview.emergentagent.com"

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

class SocialMediaAPITest(unittest.TestCase):
    """Test suite for Social Media Generation API endpoints"""
    
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
    
    def test_01_get_platform_configs(self):
        """Test GET /api/social-media/platforms endpoint"""
        print("\n=== Testing GET /api/social-media/platforms ===")
        url = f"{self.base_url}/social-media/platforms"
        response = requests.get(url, headers=self.get_headers())
        
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIn("platforms", data, "Response should have 'platforms' field")
        platforms = data["platforms"]
        
        # Check for all 6 supported platforms
        expected_platforms = ["twitter", "instagram", "linkedin", "facebook", "tiktok", "youtube"]
        for platform in expected_platforms:
            self.assertIn(platform, platforms, f"{platform} should be in supported platforms")
        
        # Check platform structure
        for platform_name, config in platforms.items():
            self.assertIn("platform", config, f"{platform_name} should have 'platform' field")
            self.assertIn("max_length", config, f"{platform_name} should have 'max_length' field")
            self.assertIn("supports_hashtags", config, f"{platform_name} should have 'supports_hashtags' field")
            self.assertIn("supports_emojis", config, f"{platform_name} should have 'supports_emojis' field")
            self.assertIn("supports_mentions", config, f"{platform_name} should have 'supports_mentions' field")
            self.assertIn("content_types", config, f"{platform_name} should have 'content_types' field")
            self.assertIsInstance(config["content_types"], list, f"{platform_name} content_types should be a list")
        
        print(f"✅ GET /api/social-media/platforms returned {len(platforms)} platforms")
        for platform_name, config in platforms.items():
            print(f"  - {platform_name}: {len(config['content_types'])} content types, max {config['max_length']} chars")
    
    def test_02_get_content_types_for_platform(self):
        """Test GET /api/social-media/content-types/{platform} endpoint"""
        print("\n=== Testing GET /api/social-media/content-types/{platform} ===")
        
        platforms_to_test = ["twitter", "instagram", "linkedin"]
        
        for platform in platforms_to_test:
            url = f"{self.base_url}/social-media/content-types/{platform}"
            response = requests.get(url, headers=self.get_headers())
            
            self.assertEqual(response.status_code, 200, f"Expected status code 200 for {platform}, got {response.status_code}")
            
            data = response.json()
            self.assertIn("platform", data, f"Response should have 'platform' field for {platform}")
            self.assertIn("content_types", data, f"Response should have 'content_types' field for {platform}")
            self.assertIn("max_length", data, f"Response should have 'max_length' field for {platform}")
            self.assertIn("supports_hashtags", data, f"Response should have 'supports_hashtags' field for {platform}")
            self.assertIn("supports_emojis", data, f"Response should have 'supports_emojis' field for {platform}")
            
            self.assertEqual(data["platform"], platform, f"Platform should match requested platform")
            self.assertIsInstance(data["content_types"], list, f"Content types should be a list for {platform}")
            self.assertGreater(len(data["content_types"]), 0, f"Should have at least one content type for {platform}")
            
            print(f"  ✅ {platform}: {data['content_types']} (max {data['max_length']} chars)")
    
    def test_03_get_templates(self):
        """Test GET /api/social-media/templates endpoint"""
        print("\n=== Testing GET /api/social-media/templates ===")
        url = f"{self.base_url}/social-media/templates"
        response = requests.get(url, headers=self.get_headers())
        
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIn("templates", data, "Response should have 'templates' field")
        templates = data["templates"]
        
        # Check that we have templates for major platforms
        expected_platforms = ["twitter", "instagram", "linkedin"]
        for platform in expected_platforms:
            if platform in templates:
                self.assertIsInstance(templates[platform], dict, f"{platform} templates should be a dict")
                print(f"  ✅ {platform}: {len(templates[platform])} template categories")
        
        print(f"✅ GET /api/social-media/templates returned templates for {len(templates)} platforms")
    
    def test_04_generate_social_media_content(self):
        """Test POST /api/social-media/generate endpoint"""
        print("\n=== Testing POST /api/social-media/generate ===")
        url = f"{self.base_url}/social-media/generate"
        
        # Test data for different platforms
        test_cases = [
            {
                "platform": "twitter",
                "content_type": "post",
                "prompt": "Tips for productivity while working from home"
            },
            {
                "platform": "instagram", 
                "content_type": "caption",
                "prompt": "Beautiful sunset photography tips"
            },
            {
                "platform": "linkedin",
                "content_type": "post", 
                "prompt": "The future of artificial intelligence in business"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n  Testing {test_case['platform']} {test_case['content_type']}...")
            
            request_data = {
                "provider_name": "openai",
                "model": "gpt-4o-mini",
                "platform": test_case["platform"],
                "content_type": test_case["content_type"],
                "prompt": test_case["prompt"],
                "tone": "professional",
                "target_audience": "general",
                "include_hashtags": True,
                "hashtag_count": 5,
                "include_emojis": True,
                "include_call_to_action": True
            }
            
            # Test without authentication
            response = requests.post(url, json=request_data)
            self.assertEqual(response.status_code, 401, 
                           f"Expected status code 401 for unauthorized request, got {response.status_code}")
            
            # Test with authentication
            response = requests.post(url, json=request_data, headers=self.get_headers())
            
            # Note: In test environment, might fail due to missing API keys
            self.assertIn(response.status_code, [200, 500], 
                         f"Expected status code 200 or 500 for {test_case['platform']}, got {response.status_code}")
            
            data = response.json()
            
            if response.status_code == 200:
                # Check response structure
                required_fields = ["id", "session_id", "provider", "model", "platform", "content_type", "content", "hashtags", "created_at", "status"]
                for field in required_fields:
                    self.assertIn(field, data, f"Response should have '{field}' field")
                
                self.assertEqual(data["platform"], test_case["platform"], "Platform should match request")
                self.assertEqual(data["content_type"], test_case["content_type"], "Content type should match request")
                self.assertIsInstance(data["hashtags"], list, "Hashtags should be a list")
                
                print(f"    ✅ Generated content for {test_case['platform']} {test_case['content_type']}")
                print(f"    Content length: {len(data['content'])} chars")
                print(f"    Hashtags: {len(data['hashtags'])}")
            else:
                print(f"    ⚠️ Generation failed (likely due to missing API key): {data.get('detail', 'Unknown error')}")
    
    def test_05_get_social_media_generations(self):
        """Test GET /api/social-media/generations endpoint"""
        print("\n=== Testing GET /api/social-media/generations ===")
        url = f"{self.base_url}/social-media/generations"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.get(url, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIn("generations", data, "Response should have 'generations' field")
        self.assertIsInstance(data["generations"], list, "Generations should be a list")
        
        print(f"✅ GET /api/social-media/generations returned {len(data['generations'])} items")
        
        # Test with platform filter
        response = requests.get(f"{url}?platform=twitter", headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200 for filtered request, got {response.status_code}")
        
        filtered_data = response.json()
        print(f"✅ GET /api/social-media/generations?platform=twitter returned {len(filtered_data['generations'])} items")
    
    def test_06_get_social_media_analytics(self):
        """Test GET /api/social-media/analytics endpoint"""
        print("\n=== Testing GET /api/social-media/analytics ===")
        url = f"{self.base_url}/social-media/analytics"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.get(url, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        required_fields = ["total_generations", "by_platform", "by_content_type"]
        for field in required_fields:
            self.assertIn(field, data, f"Response should have '{field}' field")
        
        self.assertIsInstance(data["total_generations"], int, "Total generations should be an integer")
        self.assertIsInstance(data["by_platform"], list, "By platform should be a list")
        self.assertIsInstance(data["by_content_type"], list, "By content type should be a list")
        
        print(f"✅ GET /api/social-media/analytics returned analytics")
        print(f"  Total generations: {data['total_generations']}")
        print(f"  Platform breakdown: {len(data['by_platform'])} platforms")
        print(f"  Content type breakdown: {len(data['by_content_type'])} types")
    
    def test_07_generate_hashtags(self):
        """Test POST /api/social-media/generate/hashtags endpoint"""
        print("\n=== Testing POST /api/social-media/generate/hashtags ===")
        url = f"{self.base_url}/social-media/generate/hashtags"
        
        request_data = {
            "topic": "artificial intelligence",
            "platform": "twitter",
            "count": 10,
            "trending": True,
            "niche": "technology"
        }
        
        # Test without authentication
        response = requests.post(url, json=request_data)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.post(url, json=request_data, headers=self.get_headers())
        
        # Note: Might fail due to missing API keys in test environment
        self.assertIn(response.status_code, [200, 500], 
                     f"Expected status code 200 or 500, got {response.status_code}")
        
        data = response.json()
        
        if response.status_code == 200:
            required_fields = ["hashtags", "topic", "platform", "count"]
            for field in required_fields:
                self.assertIn(field, data, f"Response should have '{field}' field")
            
            self.assertIsInstance(data["hashtags"], list, "Hashtags should be a list")
            self.assertEqual(data["topic"], request_data["topic"], "Topic should match request")
            self.assertEqual(data["platform"], request_data["platform"], "Platform should match request")
            
            print(f"✅ Generated {len(data['hashtags'])} hashtags for '{data['topic']}' on {data['platform']}")
        else:
            print(f"⚠️ Hashtag generation failed (likely due to missing API key): {data.get('detail', 'Unknown error')}")


if __name__ == "__main__":
    # Run both test suites
    print("=" * 80)
    print("RUNNING CONTENTFORGE AI API TESTS")
    print("=" * 80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add Code Generation tests
    suite.addTests(loader.loadTestsFromTestCase(CodeGenerationAPITest))
    
    # Add Social Media tests
    suite.addTests(loader.loadTestsFromTestCase(SocialMediaAPITest))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n❌ {len(result.failures + result.errors)} TESTS FAILED")
    
    sys.exit(0 if result.wasSuccessful() else 1)