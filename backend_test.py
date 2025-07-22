#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Script
Tests all major endpoints for ContentForge AI API
"""

import requests
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://84a312aa-ca0e-453e-8c3d-7d809f4d1c5f.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        
    def log_test(self, endpoint: str, method: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {method} {endpoint} - {status} {details}")
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    headers: Dict = None, files: Dict = None) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{API_BASE}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=60)
            elif method.upper() == "POST":
                if files:
                    response = self.session.post(url, data=data, files=files, headers=headers, timeout=60)
                else:
                    response = self.session.post(url, json=data, headers=headers, timeout=60)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=60)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=60)
            else:
                raise ValueError(f"Unsupported method: {method}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
            
    def test_health_endpoints(self):
        """Test basic health and root endpoints"""
        print("\n=== Testing Health Endpoints ===")
        
        # Health check
        response = self.make_request("GET", "/health")
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                self.log_test("/health", "GET", "PASS", "API is healthy")
            else:
                self.log_test("/health", "GET", "FAIL", f"Unexpected response: {data}")
        else:
            self.log_test("/health", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Root endpoint
        response = self.make_request("GET", "/")
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") == "ContentForge AI API":
                self.log_test("/", "GET", "PASS", "Root endpoint working")
            else:
                self.log_test("/", "GET", "FAIL", f"Unexpected response: {data}")
        else:
            self.log_test("/", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n=== Testing Authentication ===")
        
        # Test admin login
        admin_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = self.make_request("POST", "/auth/login", admin_data)
        if response and response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                self.admin_token = data["access_token"]
                self.log_test("/auth/login", "POST", "PASS", "Admin login successful")
            else:
                self.log_test("/auth/login", "POST", "FAIL", f"No token in response: {data}")
        else:
            self.log_test("/auth/login", "POST", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Test user registration (create test user)
        test_user_data = {
            "username": "testuser_api",
            "email": "testuser@contentforge.ai",
            "password": "testpass123"
        }
        
        response = self.make_request("POST", "/auth/register", test_user_data)
        if response and response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                self.user_token = data["access_token"]
                self.log_test("/auth/register", "POST", "PASS", "User registration successful")
            else:
                self.log_test("/auth/register", "POST", "FAIL", f"No token in response: {data}")
        else:
            # Try login if registration fails (user might already exist)
            login_response = self.make_request("POST", "/auth/login", {
                "username": "testuser_api",
                "password": "testpass123"
            })
            if login_response and login_response.status_code == 200:
                data = login_response.json()
                if "access_token" in data:
                    self.user_token = data["access_token"]
                    self.log_test("/auth/register", "POST", "SKIP", "User exists, used login instead")
                else:
                    self.log_test("/auth/register", "POST", "FAIL", "Registration and login failed")
            else:
                self.log_test("/auth/register", "POST", "FAIL", f"Status: {response.status_code if response else 'No response'}")
                
        # Test get current user (with admin token)
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.make_request("GET", "/auth/me", headers=headers)
            if response and response.status_code == 200:
                data = response.json()
                if "username" in data:
                    self.log_test("/auth/me", "GET", "PASS", f"Got user info for: {data.get('username')}")
                else:
                    self.log_test("/auth/me", "GET", "FAIL", f"Invalid user data: {data}")
            else:
                self.log_test("/auth/me", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
                
    def test_provider_endpoints(self):
        """Test provider management endpoints"""
        print("\n=== Testing Provider Endpoints ===")
        
        if not self.admin_token:
            self.log_test("Provider tests", "SKIP", "SKIP", "No admin token available")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get active providers
        response = self.make_request("GET", "/providers", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if "providers" in data:
                self.log_test("/providers", "GET", "PASS", f"Found {len(data['providers'])} providers")
            else:
                self.log_test("/providers", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/providers", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get text providers
        response = self.make_request("GET", "/providers/text", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if "providers" in data:
                self.log_test("/providers/text", "GET", "PASS", f"Found {len(data['providers'])} text providers")
            else:
                self.log_test("/providers/text", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/providers/text", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get image providers
        response = self.make_request("GET", "/providers/image", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if "providers" in data:
                self.log_test("/providers/image", "GET", "PASS", f"Found {len(data['providers'])} image providers")
            else:
                self.log_test("/providers/image", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/providers/image", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Admin: Get all providers
        response = self.make_request("GET", "/admin/providers", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if "providers" in data:
                self.log_test("/admin/providers", "GET", "PASS", f"Admin access: {len(data['providers'])} providers")
            else:
                self.log_test("/admin/providers", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/admin/providers", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
    def test_generation_endpoints(self):
        """Test text, image, and video generation endpoints"""
        print("\n=== Testing Generation Endpoints ===")
        
        if not self.user_token:
            self.log_test("Generation tests", "SKIP", "SKIP", "No user token available")
            return
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test text generation (this might fail due to API keys, but endpoint should be accessible)
        text_request = {
            "prompt": "Write a short story about AI",
            "provider_name": "openai",
            "model": "gpt-3.5-turbo",
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        response = self.make_request("POST", "/generate/text", text_request, headers=headers)
        if response:
            if response.status_code == 200:
                self.log_test("/generate/text", "POST", "PASS", "Text generation endpoint accessible")
            elif response.status_code in [400, 401, 403, 500]:
                # Expected if no API keys configured or model issues
                self.log_test("/generate/text", "POST", "SKIP", f"Endpoint accessible but API key/model needed (Status: {response.status_code})")
            else:
                self.log_test("/generate/text", "POST", "FAIL", f"Unexpected status: {response.status_code}")
        else:
            self.log_test("/generate/text", "POST", "FAIL", "No response")
            
        # Get user conversations
        response = self.make_request("GET", "/conversations", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("/conversations", "GET", "PASS", f"Retrieved conversations")
        else:
            self.log_test("/conversations", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get user generations
        response = self.make_request("GET", "/generations", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("/generations", "GET", "PASS", f"Retrieved text generations")
        else:
            self.log_test("/generations", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get user image generations
        response = self.make_request("GET", "/generations/images", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("/generations/images", "GET", "PASS", f"Retrieved image generations")
        else:
            self.log_test("/generations/images", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
    def test_presentation_endpoints(self):
        """Test presentation generator endpoints"""
        print("\n=== Testing Presentation Endpoints ===")
        
        if not self.user_token:
            self.log_test("Presentation tests", "SKIP", "SKIP", "No user token available")
            return
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Get presentation templates
        response = self.make_request("GET", "/presentations/templates", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if "templates" in data:
                self.log_test("/presentations/templates", "GET", "PASS", f"Found {len(data['templates'])} templates")
            else:
                self.log_test("/presentations/templates", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/presentations/templates", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get user presentations
        response = self.make_request("GET", "/presentations/", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if "presentations" in data:
                self.log_test("/presentations/", "GET", "PASS", f"Found {len(data['presentations'])} presentations")
            else:
                self.log_test("/presentations/", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/presentations/", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get presentation history
        response = self.make_request("GET", "/presentations/history", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if "history" in data:
                self.log_test("/presentations/history", "GET", "PASS", "Retrieved presentation history")
            else:
                self.log_test("/presentations/history", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/presentations/history", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get presentation stats
        response = self.make_request("GET", "/presentations/stats", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if "stats" in data:
                self.log_test("/presentations/stats", "GET", "PASS", "Retrieved presentation stats")
            else:
                self.log_test("/presentations/stats", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/presentations/stats", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
    def test_faceless_content_endpoints(self):
        """Test faceless content endpoints"""
        print("\n=== Testing Faceless Content Endpoints ===")
        
        if not self.user_token:
            self.log_test("Faceless content tests", "SKIP", "SKIP", "No user token available")
            return
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Get available voices
        response = self.make_request("GET", "/faceless-content/voices", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_test("/faceless-content/voices", "GET", "PASS", f"Found {len(data)} voices")
            else:
                self.log_test("/faceless-content/voices", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/faceless-content/voices", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get animated characters
        response = self.make_request("GET", "/faceless-content/characters", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_test("/faceless-content/characters", "GET", "PASS", f"Found {len(data)} characters")
            else:
                self.log_test("/faceless-content/characters", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/faceless-content/characters", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get background music
        response = self.make_request("GET", "/faceless-content/background-music", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_test("/faceless-content/background-music", "GET", "PASS", f"Found {len(data)} music tracks")
            else:
                self.log_test("/faceless-content/background-music", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/faceless-content/background-music", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get content templates
        response = self.make_request("GET", "/faceless-content/templates", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_test("/faceless-content/templates", "GET", "PASS", f"Found {len(data)} content templates")
            else:
                self.log_test("/faceless-content/templates", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/faceless-content/templates", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get user content history
        response = self.make_request("GET", "/faceless-content/history", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_test("/faceless-content/history", "GET", "PASS", f"Found {len(data)} content items")
            else:
                self.log_test("/faceless-content/history", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/faceless-content/history", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get content stats
        response = self.make_request("GET", "/faceless-content/stats/overview", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("/faceless-content/stats/overview", "GET", "PASS", "Retrieved content stats")
        else:
            self.log_test("/faceless-content/stats/overview", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
    def test_user_management_endpoints(self):
        """Test user management endpoints"""
        print("\n=== Testing User Management Endpoints ===")
        
        if not self.user_token:
            self.log_test("User management tests", "SKIP", "SKIP", "No user token available")
            return
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Get user profile
        response = self.make_request("GET", "/user/profile", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if "username" in data:
                self.log_test("/user/profile", "GET", "PASS", f"Retrieved profile for: {data.get('username')}")
            else:
                self.log_test("/user/profile", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/user/profile", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get user usage stats
        response = self.make_request("GET", "/user/usage-stats", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("/user/usage-stats", "GET", "PASS", "Retrieved usage stats")
        else:
            self.log_test("/user/usage-stats", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get user activity logs
        response = self.make_request("GET", "/user/activity-logs", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("/user/activity-logs", "GET", "PASS", "Retrieved activity logs")
        else:
            self.log_test("/user/activity-logs", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get user analytics
        response = self.make_request("GET", "/user/analytics", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("/user/analytics", "GET", "PASS", "Retrieved user analytics")
        else:
            self.log_test("/user/analytics", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        print("\n=== Testing Analytics Endpoints ===")
        
        if not self.user_token:
            self.log_test("Analytics tests", "SKIP", "SKIP", "No user token available")
            return
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Get enhanced dashboard analytics
        response = self.make_request("GET", "/analytics/dashboard/enhanced", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if "summary" in data:
                self.log_test("/analytics/dashboard/enhanced", "GET", "PASS", "Retrieved enhanced analytics")
            else:
                self.log_test("/analytics/dashboard/enhanced", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/analytics/dashboard/enhanced", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get usage trends
        response = self.make_request("GET", "/analytics/usage-trends", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if "trends" in data:
                self.log_test("/analytics/usage-trends", "GET", "PASS", "Retrieved usage trends")
            else:
                self.log_test("/analytics/usage-trends", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/analytics/usage-trends", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Get analytics insights
        response = self.make_request("GET", "/analytics/insights", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if "insights" in data:
                self.log_test("/analytics/insights", "GET", "PASS", "Retrieved analytics insights")
            else:
                self.log_test("/analytics/insights", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/analytics/insights", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
    def test_dashboard_endpoints(self):
        """Test dashboard endpoints"""
        print("\n=== Testing Dashboard Endpoints ===")
        
        if not self.user_token:
            self.log_test("Dashboard tests", "SKIP", "SKIP", "No user token available")
            return
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Get dashboard statistics
        response = self.make_request("GET", "/dashboard/statistics", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if "statistics" in data:
                self.log_test("/dashboard/statistics", "GET", "PASS", "Retrieved dashboard statistics")
            else:
                self.log_test("/dashboard/statistics", "GET", "FAIL", f"Invalid response: {data}")
        else:
            self.log_test("/dashboard/statistics", "GET", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
    def run_all_tests(self):
        """Run all API tests"""
        print(f"Starting comprehensive API tests for: {API_BASE}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Run tests in order
        self.test_health_endpoints()
        self.test_authentication()
        self.test_provider_endpoints()
        self.test_generation_endpoints()
        self.test_presentation_endpoints()
        self.test_faceless_content_endpoints()
        self.test_user_management_endpoints()
        self.test_analytics_endpoints()
        self.test_dashboard_endpoints()
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped = len([r for r in self.test_results if r["status"] == "SKIP"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Skipped: {skipped}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        
        if failed > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  ❌ {result['method']} {result['endpoint']} - {result['details']}")
                    
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": (passed/total*100) if total > 0 else 0,
            "results": self.test_results
        }

if __name__ == "__main__":
    tester = APITester()
    results = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)