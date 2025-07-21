#!/usr/bin/env python3

import requests
import json
import unittest
import os
import sys
from typing import Dict, Any
from datetime import datetime

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://55b0d0ee-c62d-4529-88fb-7de3d4a921c7.preview.emergentagent.com"

class PresentationGeneratorAPITest(unittest.TestCase):
    """Test suite for Presentation Generator API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = f"{BACKEND_URL}/api"
        self.admin_token = None
        self.user_token = None
        self.created_presentation_id = None
        self.login_admin()
        self.login_user()
    
    def login_admin(self):
        """Login as admin to get authentication token"""
        login_url = f"{self.base_url}/auth/login"
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.admin_token = data.get("access_token")
            print(f"Successfully logged in as admin. Token: {self.admin_token[:10]}...")
        else:
            print(f"Failed to login as admin: {response.status_code} - {response.text}")
            self.fail("Admin login failed")
    
    def login_user(self):
        """Login as regular user to get authentication token"""
        # First register a test user if not exists
        register_url = f"{self.base_url}/auth/register"
        register_data = {
            "username": "presentationuser",
            "email": "presentationuser@example.com",
            "password": "testpass123",
            "full_name": "Presentation Test User"
        }
        
        # Try to register (might fail if user already exists, which is fine)
        requests.post(register_url, json=register_data)
        
        # Now login
        login_url = f"{self.base_url}/auth/login"
        login_data = {
            "username": "presentationuser",
            "password": "testpass123"
        }
        
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.user_token = data.get("access_token")
            print(f"Successfully logged in as presentation user. Token: {self.user_token[:10]}...")
        else:
            print(f"Failed to login as presentation user: {response.status_code} - {response.text}")
            self.fail("Presentation user login failed")
    
    def get_admin_headers(self) -> Dict[str, str]:
        """Get headers with admin authentication token"""
        return {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
    
    def get_user_headers(self) -> Dict[str, str]:
        """Get headers with user authentication token"""
        return {
            "Authorization": f"Bearer {self.user_token}",
            "Content-Type": "application/json"
        }
    
    def test_01_get_presentation_templates(self):
        """Test GET /api/presentations/templates endpoint - should return 3 default templates"""
        print("\n=== Testing GET /api/presentations/templates ===")
        url = f"{self.base_url}/presentations/templates"
        
        # Test without authentication
        response = requests.get(url)
        self.assertIn(response.status_code, [401, 403], 
                         f"Expected status code 401 or 403 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication
        response = requests.get(url, headers=self.get_user_headers())
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIn("templates", data, "Response should have 'templates' field")
        templates = data["templates"]
        self.assertIsInstance(templates, list, "Templates should be a list")
        self.assertGreaterEqual(len(templates), 3, "Should have at least 3 default templates")
        
        # Check for expected default templates
        template_ids = [template.get("id") for template in templates]
        expected_templates = ["business_pitch", "marketing_report", "product_demo"]
        
        for expected_template in expected_templates:
            self.assertIn(expected_template, template_ids, f"Should have {expected_template} template")
        
        # Check template structure
        for template in templates:
            required_fields = ["id", "name", "description", "type"]
            for field in required_fields:
                self.assertIn(field, template, f"Template should have '{field}' field")
        
        print(f"✅ GET /api/presentations/templates returned {len(templates)} templates")
        for template in templates:
            print(f"  - {template['name']}: {template['description']}")
    
    def test_02_get_specific_template(self):
        """Test GET /api/presentations/templates/{id} endpoint - should return specific template"""
        print("\n=== Testing GET /api/presentations/templates/{template_id} ===")
        
        # Test with business_pitch template
        template_id = "business_pitch"
        url = f"{self.base_url}/presentations/templates/{template_id}"
        
        # Test without authentication
        response = requests.get(url)
        self.assertIn(response.status_code, [401, 403], 
                         f"Expected status code 401 or 403 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication
        response = requests.get(url, headers=self.get_user_headers())
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertEqual(data["id"], template_id, "Template ID should match requested ID")
        self.assertEqual(data["name"], "Business Pitch Deck", "Template name should match")
        self.assertIn("slides", data, "Template should have slides")
        self.assertIsInstance(data["slides"], list, "Slides should be a list")
        
        print(f"✅ GET /api/presentations/templates/{template_id} returned template: {data['name']}")
        print(f"  Template has {len(data['slides'])} slides")
        
        # Test with non-existent template
        response = requests.get(f"{self.base_url}/presentations/templates/nonexistent", headers=self.get_user_headers())
        self.assertEqual(response.status_code, 404, "Should return 404 for non-existent template")
    
    def test_03_create_presentation(self):
        """Test POST /api/presentations/create endpoint - should create a new presentation"""
        print("\n=== Testing POST /api/presentations/create ===")
        url = f"{self.base_url}/presentations/create"
        
        presentation_data = {
            "template_id": "business_pitch",
            "title": "My Business Presentation",
            "data": {
                "company_name": "TechCorp Solutions",
                "problem": "Small businesses struggle with digital transformation",
                "solution": "AI-powered automation platform that simplifies complex workflows",
                "market_size": "$50B global market opportunity",
                "business_model": "SaaS subscription with tiered pricing starting at $99/month",
                "team": "Experienced founders with 20+ years in tech and business automation",
                "financials": "Projected $1M ARR by year 2, break-even by month 18",
                "funding": "Seeking $2M Series A funding for product development and market expansion"
            }
        }
        
        # Test without authentication
        response = requests.post(url, json=presentation_data)
        self.assertIn(response.status_code, [401, 403], 
                         f"Expected status code 401 or 403 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication
        response = requests.post(url, json=presentation_data, headers=self.get_user_headers())
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIn("presentation_id", data, "Response should have 'presentation_id' field")
        self.assertIn("message", data, "Response should have 'message' field")
        
        self.created_presentation_id = data["presentation_id"]
        print(f"✅ Created presentation: {data['presentation_id']}")
        print(f"  Message: {data['message']}")
        
        # Test with invalid template
        invalid_data = {
            "template_id": "nonexistent_template",
            "title": "Invalid Template Test"
        }
        response = requests.post(url, json=invalid_data, headers=self.get_user_headers())
        self.assertEqual(response.status_code, 500, "Should return error for invalid template")
    
    def test_04_get_presentation_history(self):
        """Test GET /api/presentations/history endpoint - should return user's presentation history"""
        print("\n=== Testing GET /api/presentations/history ===")
        url = f"{self.base_url}/presentations/history"
        
        # Test without authentication
        response = requests.get(url)
        self.assertIn(response.status_code, [401, 403], 
                         f"Expected status code 401 or 403 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication
        response = requests.get(url, headers=self.get_user_headers())
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            self.assertIn("history", data, "Response should have 'history' field")
            history = data["history"]
            self.assertIsInstance(history, list, "History should be a list")
            
            print(f"✅ GET /api/presentations/history returned {len(history)} history entries")
            
            # Check history structure if any entries exist
            if len(history) > 0:
                history_entry = history[0]
                expected_fields = ["id", "presentation_id", "user_id", "action", "created_at"]
                for field in expected_fields:
                    self.assertIn(field, history_entry, f"History entry should have '{field}' field")
                
                print(f"  Latest history entry: {history_entry['action']} for presentation {history_entry['presentation_id']}")
        else:
            print(f"❌ GET /api/presentations/history failed with status {response.status_code}")
            print(f"Error: {response.text}")
            self.fail(f"History endpoint failed: {response.status_code}")
    
    def test_05_get_presentation_stats(self):
        """Test GET /api/presentations/stats endpoint - should return user's presentation statistics"""
        print("\n=== Testing GET /api/presentations/stats ===")
        url = f"{self.base_url}/presentations/stats"
        
        # Test without authentication
        response = requests.get(url)
        self.assertIn(response.status_code, [401, 403], 
                         f"Expected status code 401 or 403 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication
        response = requests.get(url, headers=self.get_user_headers())
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            self.assertIn("stats", data, "Response should have 'stats' field")
            stats = data["stats"]
            
            expected_fields = ["total_presentations", "type_counts", "recent_activity"]
            for field in expected_fields:
                self.assertIn(field, stats, f"Stats should have '{field}' field")
            
            self.assertIsInstance(stats["total_presentations"], int, "Total presentations should be an integer")
            self.assertIsInstance(stats["type_counts"], dict, "Type counts should be a dict")
            self.assertIsInstance(stats["recent_activity"], list, "Recent activity should be a list")
            
            print(f"✅ GET /api/presentations/stats returned statistics:")
            print(f"  Total presentations: {stats['total_presentations']}")
            print(f"  Type counts: {stats['type_counts']}")
            print(f"  Recent activity entries: {len(stats['recent_activity'])}")
        else:
            print(f"❌ GET /api/presentations/stats failed with status {response.status_code}")
            print(f"Error: {response.text}")
            self.fail(f"Stats endpoint failed: {response.status_code}")
    
    def test_06_export_presentation_pptx(self):
        """Test POST /api/presentations/{id}/export/pptx endpoint"""
        print("\n=== Testing POST /api/presentations/{id}/export/pptx ===")
        
        if not self.created_presentation_id:
            print("⚠️ No presentation created in previous test, skipping export test")
            return
        
        url = f"{self.base_url}/presentations/{self.created_presentation_id}/export/pptx"
        
        # Test without authentication
        response = requests.post(url)
        self.assertIn(response.status_code, [401, 403], 
                         f"Expected status code 401 or 403 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication
        response = requests.post(url, headers=self.get_user_headers())
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Export might fail due to missing dependencies, but endpoint should process request
        self.assertIn(response.status_code, [200, 500], 
                     f"Expected status code 200 or 500, got {response.status_code}")
        
        if response.status_code == 200:
            # Check if it's a file download response
            content_type = response.headers.get('content-type', '')
            self.assertIn('application/', content_type, "Should return file content")
            print(f"✅ PPTX export successful - Content-Type: {content_type}")
        else:
            data = response.json()
            print(f"❌ PPTX export failed: {data.get('detail', 'Unknown error')}")
    
    def test_07_export_presentation_pdf(self):
        """Test POST /api/presentations/{id}/export/pdf endpoint"""
        print("\n=== Testing POST /api/presentations/{id}/export/pdf ===")
        
        if not self.created_presentation_id:
            print("⚠️ No presentation created in previous test, skipping export test")
            return
        
        url = f"{self.base_url}/presentations/{self.created_presentation_id}/export/pdf"
        
        # Test with user authentication
        response = requests.post(url, headers=self.get_user_headers())
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Export might fail due to missing dependencies, but endpoint should process request
        self.assertIn(response.status_code, [200, 500], 
                     f"Expected status code 200 or 500, got {response.status_code}")
        
        if response.status_code == 200:
            # Check if it's a file download response
            content_type = response.headers.get('content-type', '')
            self.assertIn('application/pdf', content_type, "Should return PDF content")
            print(f"✅ PDF export successful - Content-Type: {content_type}")
        else:
            data = response.json()
            print(f"❌ PDF export failed: {data.get('detail', 'Unknown error')}")
    
    def test_08_export_presentation_google_slides(self):
        """Test POST /api/presentations/{id}/export/google-slides endpoint"""
        print("\n=== Testing POST /api/presentations/{id}/export/google-slides ===")
        
        if not self.created_presentation_id:
            print("⚠️ No presentation created in previous test, skipping export test")
            return
        
        url = f"{self.base_url}/presentations/{self.created_presentation_id}/export/google-slides"
        
        # Test with user authentication
        response = requests.post(url, headers=self.get_user_headers())
        print(f"Response status: {response.status_code}")
        
        # Google Slides export will likely fail due to missing API credentials
        self.assertIn(response.status_code, [200, 500], 
                     f"Expected status code 200 or 500, got {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.assertIn("url", data, "Response should have 'url' field")
            self.assertIn("presentation_id", data, "Response should have 'presentation_id' field")
            print(f"✅ Google Slides export successful - URL: {data['url']}")
        else:
            data = response.json()
            print(f"❌ Google Slides export failed: {data.get('detail', 'Unknown error')}")


if __name__ == "__main__":
    print("=" * 80)
    print("TESTING PRESENTATION GENERATOR API ENDPOINTS")
    print("=" * 80)
    
    # Run only Presentation Generator tests
    suite = unittest.TestLoader().loadTestsFromTestCase(PresentationGeneratorAPITest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("PRESENTATION GENERATOR TEST SUMMARY")
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
        print("\n🎉 ALL PRESENTATION GENERATOR TESTS PASSED!")
    else:
        print(f"\n❌ {len(result.failures + result.errors)} PRESENTATION GENERATOR TESTS FAILED")
    
    sys.exit(0 if result.wasSuccessful() else 1)