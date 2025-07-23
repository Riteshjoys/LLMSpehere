#!/usr/bin/env python3
"""
Focused Authentication Testing Script
Tests the specific endpoints mentioned in the review request that were returning 401 errors
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://d4beb4cc-564e-4149-b7f0-c736467390d4.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class AuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        
    def log_test(self, endpoint: str, method: str, status: str, details: str = ""):
        """Log test results"""
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {method} {endpoint} - {status} {details}")
        
    def make_request(self, method: str, endpoint: str, data: dict = None, 
                    headers: dict = None) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{API_BASE}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
            
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
                self.log_test("/auth/login", "POST", "PASS", "Admin login successful, JWT token received")
                print(f"   Token: {self.admin_token[:50]}...")
            else:
                self.log_test("/auth/login", "POST", "FAIL", f"No token in response: {data}")
        else:
            self.log_test("/auth/login", "POST", "FAIL", f"Status: {response.status_code if response else 'No response'}")
            
        # Test JWT token validation with /auth/me
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.make_request("GET", "/auth/me", headers=headers)
            if response and response.status_code == 200:
                data = response.json()
                if "username" in data:
                    self.log_test("/auth/me", "GET", "PASS", f"JWT token valid, user: {data.get('username')}")
                else:
                    self.log_test("/auth/me", "GET", "FAIL", f"Invalid user data: {data}")
            else:
                self.log_test("/auth/me", "GET", "FAIL", f"JWT validation failed - Status: {response.status_code if response else 'No response'}")
                
    def test_code_generation_endpoints(self):
        """Test the specific code generation endpoints that were returning 401 errors"""
        print("\n=== Testing Code Generation Endpoints (Previously 401 Errors) ===")
        
        # Test public endpoints (should not require authentication)
        endpoints = [
            ("/code/providers", "GET"),
            ("/code/languages", "GET"), 
            ("/code/request-types", "GET")
        ]
        
        for endpoint, method in endpoints:
            response = self.make_request(method, endpoint)
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test(endpoint, method, "PASS", f"Public endpoint working, returned {len(data)} items")
                else:
                    self.log_test(endpoint, method, "FAIL", f"Empty or invalid response: {data}")
            elif response and response.status_code == 401:
                self.log_test(endpoint, method, "FAIL", "❌ STILL RETURNING 401 UNAUTHORIZED - AUTHENTICATION ISSUE NOT RESOLVED")
            else:
                self.log_test(endpoint, method, "FAIL", f"Status: {response.status_code if response else 'No response'}")
                
        # Test authenticated endpoints
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            auth_endpoints = [
                ("/code/history", "GET"),
            ]
            
            for endpoint, method in auth_endpoints:
                response = self.make_request(method, endpoint, headers=headers)
                if response and response.status_code == 200:
                    data = response.json()
                    self.log_test(endpoint, method, "PASS", f"Authenticated endpoint working with JWT token")
                elif response and response.status_code == 401:
                    self.log_test(endpoint, method, "FAIL", "❌ STILL RETURNING 401 UNAUTHORIZED - JWT TOKEN NOT BEING ACCEPTED")
                else:
                    self.log_test(endpoint, method, "FAIL", f"Status: {response.status_code if response else 'No response'}")
                    
    def test_fullstack_ai_endpoints(self):
        """Test the specific Full Stack AI endpoints that were returning 401 errors"""
        print("\n=== Testing Full Stack AI Assistant Endpoints (Previously 401 Errors) ===")
        
        if not self.admin_token:
            self.log_test("Full Stack AI tests", "SKIP", "SKIP", "No admin token available")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        endpoints = [
            ("/fullstack-ai/capabilities", "GET"),
            ("/fullstack-ai/projects", "GET")
        ]
        
        for endpoint, method in endpoints:
            response = self.make_request(method, endpoint, headers=headers)
            if response and response.status_code == 200:
                data = response.json()
                self.log_test(endpoint, method, "PASS", f"Endpoint working with JWT token")
            elif response and response.status_code == 401:
                self.log_test(endpoint, method, "FAIL", "❌ STILL RETURNING 401 UNAUTHORIZED - JWT TOKEN NOT BEING ACCEPTED")
            elif response and response.status_code == 403:
                self.log_test(endpoint, method, "PASS", "Endpoint accessible but requires premium subscription (expected behavior)")
            elif response and response.status_code == 500:
                self.log_test(endpoint, method, "WARN", "Internal server error - endpoint accessible but has implementation issues")
            else:
                self.log_test(endpoint, method, "FAIL", f"Status: {response.status_code if response else 'No response'}")
                
    def run_focused_tests(self):
        """Run focused authentication tests"""
        print(f"🔍 FOCUSED AUTHENTICATION TESTING")
        print(f"Testing API: {API_BASE}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Focus: Resolving 401 authentication errors in Code Generation and Full Stack AI endpoints")
        
        self.test_authentication()
        self.test_code_generation_endpoints()
        self.test_fullstack_ai_endpoints()
        
        print("\n" + "="*80)
        print("🎯 AUTHENTICATION TEST SUMMARY")
        print("="*80)
        print("✅ = Authentication working correctly")
        print("❌ = Authentication still failing (401 errors)")
        print("⚠️ = Other issues (500 errors, premium required, etc.)")

if __name__ == "__main__":
    tester = AuthTester()
    tester.run_focused_tests()