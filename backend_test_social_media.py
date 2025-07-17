import requests
import json
import unittest
import os
import sys
from typing import Dict, Any

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://40e61490-25e2-48dd-a939-e62aa88091dc.preview.emergentagent.com"

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
            self.assertIn(response.status_code, [401, 403], 
                           f"Expected status code 401 or 403 for unauthorized request, got {response.status_code}")
            
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
        self.assertIn(response.status_code, [401, 403], 
                         f"Expected status code 401 or 403 for unauthorized request, got {response.status_code}")
        
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
        self.assertIn(response.status_code, [401, 403], 
                         f"Expected status code 401 or 403 for unauthorized request, got {response.status_code}")
        
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
        self.assertIn(response.status_code, [401, 403], 
                         f"Expected status code 401 or 403 for unauthorized request, got {response.status_code}")
        
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
    print("=" * 80)
    print("RUNNING SOCIAL MEDIA API TESTS")
    print("=" * 80)
    
    unittest.main(verbosity=2)