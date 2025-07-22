import requests
import json
import unittest
import os
import sys
from typing import Dict, Any
from datetime import datetime

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://84a312aa-ca0e-453e-8c3d-7d809f4d1c5f.preview.emergentagent.com"

class FocusedUserManagementAndAnalyticsTest(unittest.TestCase):
    """Focused test suite for new User Management and Analytics API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = f"{BACKEND_URL}/api"
        self.admin_token = None
        self.user_token = None
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
            print(f"✅ Successfully logged in as admin. Token: {self.admin_token[:10]}...")
        else:
            print(f"❌ Failed to login as admin: {response.status_code} - {response.text}")
            self.fail("Admin login failed")
    
    def login_user(self):
        """Login as regular user to get authentication token"""
        # First register a test user if not exists
        register_url = f"{self.base_url}/auth/register"
        register_data = {
            "username": "focusedtestuser",
            "email": "focusedtestuser@example.com",
            "password": "testpass123",
            "full_name": "Focused Test User"
        }
        
        # Try to register (might fail if user already exists, which is fine)
        requests.post(register_url, json=register_data)
        
        # Now login
        login_url = f"{self.base_url}/auth/login"
        login_data = {
            "username": "focusedtestuser",
            "password": "testpass123"
        }
        
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.user_token = data.get("access_token")
            print(f"✅ Successfully logged in as regular user. Token: {self.user_token[:10]}...")
        else:
            print(f"❌ Failed to login as user: {response.status_code} - {response.text}")
            self.fail("User login failed")
    
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
    
    # USER MANAGEMENT API TESTS
    
    def test_01_get_user_profile(self):
        """Test GET /api/user/profile endpoint"""
        print("\n=== Testing GET /api/user/profile ===")
        url = f"{self.base_url}/user/profile"
        
        # Test without authentication
        response = requests.get(url)
        self.assertIn(response.status_code, [401, 403], 
                     f"Expected status code 401 or 403 for unauthorized request, got {response.status_code}")
        
        # Test with admin authentication
        response = requests.get(url, headers=self.get_admin_headers())
        print(f"Admin profile response: {response.status_code}")
        if response.status_code == 200:
            admin_data = response.json()
            required_fields = ["user_id", "username", "email", "created_at"]
            for field in required_fields:
                if field in admin_data:
                    print(f"  ✅ Admin profile has '{field}': {admin_data[field]}")
                else:
                    print(f"  ⚠️ Admin profile missing '{field}' field")
            
            # Check if user is admin (either by role or is_admin flag)
            is_admin = admin_data.get("is_admin", False) or admin_data.get("role") == "admin"
            if is_admin:
                print(f"✅ Admin user confirmed (is_admin: {admin_data.get('is_admin', False)})")
            else:
                print(f"⚠️ Admin user not properly identified")
            print(f"✅ Admin profile retrieved successfully")
        else:
            print(f"❌ Admin profile failed: {response.status_code} - {response.text}")
        
        # Test with regular user authentication
        response = requests.get(url, headers=self.get_user_headers())
        print(f"User profile response: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User profile retrieved: {user_data.get('username', 'Unknown')} ({user_data.get('role', 'Unknown')})")
        else:
            print(f"❌ User profile failed: {response.status_code} - {response.text}")
    
    def test_02_update_user_profile(self):
        """Test PUT /api/user/profile endpoint"""
        print("\n=== Testing PUT /api/user/profile ===")
        url = f"{self.base_url}/user/profile"
        
        update_data = {
            "full_name": "Updated Focused Test User",
            "bio": "This is my updated bio for focused testing",
            "location": "Test City, TC",
            "website": "https://focusedtest.example.com"
        }
        
        # Test without authentication
        response = requests.put(url, json=update_data)
        self.assertIn(response.status_code, [401, 403], 
                     f"Expected status code 401 or 403 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication
        response = requests.put(url, json=update_data, headers=self.get_user_headers())
        print(f"Profile update response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profile updated: {data.get('message', 'Success')}")
        else:
            print(f"❌ Profile update failed: {response.status_code} - {response.text}")
    
    def test_03_update_user_preferences(self):
        """Test PUT /api/user/preferences endpoint"""
        print("\n=== Testing PUT /api/user/preferences ===")
        url = f"{self.base_url}/user/preferences"
        
        preferences_data = {
            "theme": "dark",
            "language": "en",
            "notifications": {
                "email": True,
                "push": False,
                "sms": False
            },
            "privacy": {
                "profile_visibility": "public",
                "activity_visibility": "friends"
            }
        }
        
        # Test with user authentication
        response = requests.put(url, json=preferences_data, headers=self.get_user_headers())
        print(f"Preferences update response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Preferences updated: {data.get('message', 'Success')}")
        else:
            print(f"❌ Preferences update failed: {response.status_code} - {response.text}")
    
    def test_04_get_user_usage_stats(self):
        """Test GET /api/user/usage-stats endpoint"""
        print("\n=== Testing GET /api/user/usage-stats ===")
        url = f"{self.base_url}/user/usage-stats"
        
        # Test with user authentication
        response = requests.get(url, headers=self.get_user_headers())
        print(f"Usage stats response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            expected_fields = ["total_generations", "text_generations", "image_generations", "video_generations", 
                              "code_generations", "social_media_generations", "total_tokens_used", "total_cost"]
            
            print(f"✅ Usage stats retrieved:")
            for field in expected_fields:
                if field in data:
                    print(f"  {field}: {data[field]}")
                else:
                    print(f"  ⚠️ Missing field: {field}")
        else:
            print(f"❌ Usage stats failed: {response.status_code} - {response.text}")
    
    def test_05_get_user_activity_logs(self):
        """Test GET /api/user/activity-logs endpoint"""
        print("\n=== Testing GET /api/user/activity-logs ===")
        url = f"{self.base_url}/user/activity-logs"
        
        # Test with user authentication
        response = requests.get(url, headers=self.get_user_headers())
        print(f"Activity logs response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Activity logs retrieved: {len(data)} entries")
            
            if len(data) > 0:
                log_entry = data[0]
                print(f"  Latest activity: {log_entry.get('activity_type', 'Unknown')} - {log_entry.get('description', 'No description')}")
        else:
            print(f"❌ Activity logs failed: {response.status_code} - {response.text}")
    
    def test_06_get_user_analytics(self):
        """Test GET /api/user/analytics endpoint"""
        print("\n=== Testing GET /api/user/analytics ===")
        url = f"{self.base_url}/user/analytics"
        
        # Test with user authentication (default 30 days)
        response = requests.get(url, headers=self.get_user_headers())
        print(f"User analytics response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User analytics retrieved:")
            print(f"  Period: {data.get('period_days', 'Unknown')} days")
            print(f"  Total activity: {data.get('total_activity', 'Unknown')}")
            print(f"  Daily breakdown entries: {len(data.get('daily_breakdown', {}))}")
            print(f"  Feature usage entries: {len(data.get('feature_usage', {}))}")
        else:
            print(f"❌ User analytics failed: {response.status_code} - {response.text}")
    
    # ENHANCED ANALYTICS API TESTS
    
    def test_07_get_enhanced_dashboard_analytics(self):
        """Test GET /api/analytics/dashboard/enhanced endpoint"""
        print("\n=== Testing GET /api/analytics/dashboard/enhanced ===")
        url = f"{self.base_url}/analytics/dashboard/enhanced"
        
        # Test with user authentication (default 30 days)
        response = requests.get(url, headers=self.get_user_headers())
        print(f"Enhanced dashboard analytics response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            required_sections = ["summary", "daily_activity", "generation_breakdown", "provider_usage", 
                               "feature_usage", "performance_metrics", "date_range"]
            
            print(f"✅ Enhanced dashboard analytics retrieved:")
            for section in required_sections:
                if section in data:
                    if section == "summary":
                        summary = data[section]
                        print(f"  Summary - Total generations: {summary.get('total_generations', 'Unknown')}")
                        print(f"  Summary - Success rate: {summary.get('success_rate', 'Unknown')}%")
                        print(f"  Summary - Avg response time: {summary.get('avg_response_time', 'Unknown')}s")
                        print(f"  Summary - Estimated cost: ${summary.get('estimated_cost', 'Unknown')}")
                    elif section == "daily_activity":
                        print(f"  Daily activity entries: {len(data[section])}")
                    elif section == "generation_breakdown":
                        breakdown = data[section]
                        print(f"  Generation breakdown - Text: {breakdown.get('text', 0)}, Image: {breakdown.get('image', 0)}, Video: {breakdown.get('video', 0)}")
                    else:
                        print(f"  ✅ {section}: Present")
                else:
                    print(f"  ⚠️ Missing section: {section}")
        else:
            print(f"❌ Enhanced dashboard analytics failed: {response.status_code} - {response.text}")
        
        # Test with custom period
        response = requests.get(f"{url}?days=7", headers=self.get_user_headers())
        print(f"Enhanced analytics (7 days) response: {response.status_code}")
        if response.status_code == 200:
            weekly_data = response.json()
            print(f"✅ 7-day analytics: {weekly_data['summary']['total_generations']} total generations")
        else:
            print(f"❌ 7-day analytics failed: {response.status_code} - {response.text}")
    
    def test_08_get_usage_trends(self):
        """Test GET /api/analytics/usage-trends endpoint"""
        print("\n=== Testing GET /api/analytics/usage-trends ===")
        url = f"{self.base_url}/analytics/usage-trends"
        
        # Test different periods
        periods = ["day", "week", "month"]
        
        for period in periods:
            print(f"\n  Testing {period} period...")
            response = requests.get(f"{url}?period={period}", headers=self.get_user_headers())
            print(f"  Usage trends ({period}) response: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"    ✅ {period} trends retrieved")
                print(f"    Period: {data.get('period', 'Unknown')}")
                trends = data.get('trends', {})
                print(f"    Text trend data points: {len(trends.get('text', []))}")
                print(f"    Image trend data points: {len(trends.get('image', []))}")
            else:
                print(f"    ❌ {period} trends failed: {response.status_code} - {response.text}")
    
    def test_09_export_analytics(self):
        """Test GET /api/analytics/export endpoint"""
        print("\n=== Testing GET /api/analytics/export ===")
        url = f"{self.base_url}/analytics/export"
        
        # Test JSON export (default)
        response = requests.get(url, headers=self.get_user_headers())
        print(f"Analytics export response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            required_fields = ["export_format", "generated_at", "user_id", "data"]
            print(f"✅ Analytics export successful:")
            for field in required_fields:
                if field in data:
                    if field == "data":
                        analytics_data = data[field]
                        print(f"  {field}: {len(analytics_data)} sections")
                    else:
                        print(f"  {field}: {data[field]}")
                else:
                    print(f"  ⚠️ Missing field: {field}")
        else:
            print(f"❌ Analytics export failed: {response.status_code} - {response.text}")
    
    def test_10_get_analytics_insights(self):
        """Test GET /api/analytics/insights endpoint"""
        print("\n=== Testing GET /api/analytics/insights ===")
        url = f"{self.base_url}/analytics/insights"
        
        # Test with user authentication
        response = requests.get(url, headers=self.get_user_headers())
        print(f"Analytics insights response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            insights = data.get("insights", [])
            print(f"✅ Analytics insights retrieved: {len(insights)} insights")
            
            if len(insights) > 0:
                insight = insights[0]
                print(f"  Sample insight: {insight.get('title', 'No title')}")
                print(f"  Description: {insight.get('description', 'No description')}")
                print(f"  Type: {insight.get('type', 'Unknown')}, Trend: {insight.get('trend', 'Unknown')}")
            else:
                print("  No insights generated (normal for users with limited activity)")
        else:
            print(f"❌ Analytics insights failed: {response.status_code} - {response.text}")


if __name__ == "__main__":
    print("=" * 80)
    print("FOCUSED TEST: USER MANAGEMENT & ANALYTICS APIs")
    print("=" * 80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add focused tests
    suite.addTests(loader.loadTestsFromTestCase(FocusedUserManagementAndAnalyticsTest))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("FOCUSED TEST SUMMARY")
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
        print("\n🎉 ALL FOCUSED TESTS PASSED!")
    else:
        print(f"\n❌ {len(result.failures + result.errors)} FOCUSED TESTS FAILED")
    
    sys.exit(0 if result.wasSuccessful() else 1)