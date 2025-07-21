#!/usr/bin/env python3
"""
Comprehensive test suite for Presentation Generator API endpoints
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://613b2841-f21c-421a-84e1-5f0b9b887d0c.preview.emergentagent.com/api"

class PresentationGeneratorTest:
    """Test suite specifically for Presentation Generator API endpoints"""
    
    def __init__(self):
        self.base_url = BACKEND_URL
        self.auth_token = None
        self.created_presentation_id = None
        self.test_results = []
        
    def login(self):
        """Login to get authentication token"""
        login_url = f"{self.base_url}/auth/login"
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        try:
            response = requests.post(login_url, json=login_data, timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                print(f"✅ Successfully logged in as admin. Token: {self.auth_token[:20]}...")
                return True
            else:
                print(f"❌ Failed to login: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, data=None):
        """Run a single test and record results"""
        url = f"{self.base_url}/{endpoint}"
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.get_headers(), timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=self.get_headers(), timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=self.get_headers(), timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.get_headers(), timeout=30)
            
            success = response.status_code == expected_status
            
            if success:
                print(f"✅ {name} - PASSED (Status: {response.status_code})")
                try:
                    response_data = response.json() if response.content else {}
                    if response_data:
                        print(f"   Response keys: {list(response_data.keys())}")
                except:
                    response_data = {}
                    print(f"   Response: Binary/File content ({len(response.content)} bytes)")
            else:
                print(f"❌ {name} - FAILED (Expected {expected_status}, got {response.status_code})")
                try:
                    response_data = response.json() if response.content else {}
                    print(f"   Error: {response_data}")
                except:
                    print(f"   Raw response: {response.text[:500]}")
                response_data = {}
            
            self.test_results.append({
                'name': name,
                'success': success,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'endpoint': endpoint
            })
            
            return success, response_data
            
        except Exception as e:
            print(f"❌ {name} - ERROR: {str(e)}")
            self.test_results.append({
                'name': name,
                'success': False,
                'error': str(e),
                'endpoint': endpoint
            })
            return False, {}
    
    def test_basic_template_endpoints(self):
        """Test the basic template endpoints that should work"""
        print("\n" + "="*60)
        print("TESTING BASIC TEMPLATE ENDPOINTS")
        print("="*60)
        
        # Test GET /api/presentations/templates
        success, templates_data = self.run_test(
            "Get Presentation Templates",
            "GET",
            "presentations/templates",
            200
        )
        
        if success and templates_data:
            templates = templates_data.get("templates", [])
            print(f"   Found {len(templates)} templates")
            for template in templates:
                print(f"   - {template.get('name', 'Unknown')}: {template.get('id', 'No ID')}")
            
            # Test GET /api/presentations/templates/{id} for each template
            for template in templates[:2]:  # Test first 2 templates
                template_id = template.get('id')
                if template_id:
                    self.run_test(
                        f"Get Template {template_id}",
                        "GET",
                        f"presentations/templates/{template_id}",
                        200
                    )
        
        return success
    
    def test_presentation_creation(self):
        """Test presentation creation endpoint"""
        print("\n" + "="*60)
        print("TESTING PRESENTATION CREATION")
        print("="*60)
        
        # Create a presentation with business_pitch template
        create_data = {
            "template_id": "business_pitch",
            "title": "Test Business Pitch Presentation",
            "data": {
                "company_name": "TechCorp Solutions",
                "problem": "Small businesses struggle with digital transformation",
                "solution": "AI-powered automation platform",
                "market_size": "$50B global market",
                "business_model": "SaaS subscription with tiered pricing",
                "team": "Experienced founders with 20+ years in tech",
                "financials": "Projected $1M ARR by year 2",
                "funding": "Seeking $2M Series A funding"
            }
        }
        
        success, response_data = self.run_test(
            "Create Presentation",
            "POST",
            "presentations/create",
            200,
            create_data
        )
        
        if success and response_data:
            self.created_presentation_id = response_data.get("presentation_id")
            print(f"   Created presentation ID: {self.created_presentation_id}")
        
        return success
    
    def test_previously_failing_endpoints(self):
        """Test the endpoints that were reported as failing"""
        print("\n" + "="*60)
        print("TESTING PREVIOUSLY FAILING ENDPOINTS")
        print("="*60)
        
        # Test GET /api/presentations/history
        success1, history_data = self.run_test(
            "Get Presentation History",
            "GET",
            "presentations/history",
            200
        )
        
        if success1 and history_data:
            history = history_data.get("history", [])
            print(f"   Found {len(history)} history items")
        
        # Test GET /api/presentations/stats
        success2, stats_data = self.run_test(
            "Get Presentation Stats",
            "GET",
            "presentations/stats",
            200
        )
        
        if success2 and stats_data:
            stats = stats_data.get("stats", {})
            print(f"   Stats: {stats.get('total_presentations', 0)} presentations")
        
        # Test export endpoints if we have a presentation
        if self.created_presentation_id:
            print(f"\n   Testing export endpoints with presentation ID: {self.created_presentation_id}")
            
            # Test PPTX export
            self.run_test(
                "Export Presentation PPTX",
                "POST",
                f"presentations/{self.created_presentation_id}/export/pptx",
                200
            )
            
            # Test PDF export
            self.run_test(
                "Export Presentation PDF",
                "POST",
                f"presentations/{self.created_presentation_id}/export/pdf",
                200
            )
            
            # Test Google Slides export
            self.run_test(
                "Export Presentation Google Slides",
                "POST",
                f"presentations/{self.created_presentation_id}/export/google-slides",
                200
            )
        else:
            print("   ⚠️ No presentation ID available, skipping export tests")
        
        return success1 and success2
    
    def test_crud_operations(self):
        """Test CRUD operations on presentations"""
        print("\n" + "="*60)
        print("TESTING CRUD OPERATIONS")
        print("="*60)
        
        # Test GET all presentations
        success1, presentations_data = self.run_test(
            "Get All User Presentations",
            "GET",
            "presentations/",
            200
        )
        
        if success1 and presentations_data:
            presentations = presentations_data.get("presentations", [])
            print(f"   Found {len(presentations)} presentations")
        
        # Test GET specific presentation
        success2 = True
        if self.created_presentation_id:
            success2, _ = self.run_test(
                "Get Specific Presentation",
                "GET",
                f"presentations/{self.created_presentation_id}",
                200
            )
            
            # Test UPDATE presentation
            update_data = {
                "title": "Updated Test Presentation",
                "data": {
                    "company_name": "Updated TechCorp Solutions",
                    "problem": "Updated problem statement"
                }
            }
            
            success3, _ = self.run_test(
                "Update Presentation",
                "PUT",
                f"presentations/{self.created_presentation_id}",
                200,
                update_data
            )
            
            success2 = success2 and success3
        else:
            print("   ⚠️ No presentation ID available, skipping specific presentation tests")
        
        return success1 and success2
    
    def run_all_tests(self):
        """Run all presentation generator tests"""
        print("🚀 Starting Comprehensive Presentation Generator API Tests")
        print("="*80)
        
        # Login first
        if not self.login():
            print("❌ Authentication failed, stopping tests")
            return False
        
        # Run test suites in order
        templates_success = self.test_basic_template_endpoints()
        creation_success = self.test_presentation_creation()
        failing_success = self.test_previously_failing_endpoints()
        crud_success = self.test_crud_operations()
        
        return templates_success and creation_success and failing_success and crud_success
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("PRESENTATION GENERATOR TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Show failed tests
        failed_test_list = [test for test in self.test_results if not test['success']]
        if failed_test_list:
            print(f"\n❌ Failed Tests ({len(failed_test_list)}):")
            for test in failed_test_list:
                if 'error' in test:
                    print(f"  - {test['name']}: {test['error']}")
                else:
                    print(f"  - {test['name']}: Expected {test['expected_status']}, got {test['status_code']}")
                print(f"    Endpoint: {test['endpoint']}")
        
        # Show passed tests
        passed_test_list = [test for test in self.test_results if test['success']]
        if passed_test_list:
            print(f"\n✅ Passed Tests ({len(passed_test_list)}):")
            for test in passed_test_list:
                print(f"  - {test['name']}")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    tester = PresentationGeneratorTest()
    
    try:
        success = tester.run_all_tests()
        tester.print_summary()
        
        if success:
            print("\n🎉 ALL PRESENTATION TESTS PASSED!")
            return 0
        else:
            print(f"\n⚠️ Some presentation tests failed")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())