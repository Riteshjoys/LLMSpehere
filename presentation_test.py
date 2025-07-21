#!/usr/bin/env python3

import requests
import json
import sys
import traceback
from datetime import datetime

# Configuration
BACKEND_URL = "https://5247f2b8-9d59-47e0-9a5b-c9a6f5154eec.preview.emergentagent.com/api"

def test_presentation_endpoints():
    """Test the failing presentation generator endpoints specifically"""
    
    print("=== TESTING FAILING PRESENTATION GENERATOR ENDPOINTS ===")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started at: {datetime.now()}")
    print()
    
    # First, login to get authentication token
    print("1. Authenticating...")
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Authentication failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    print()
    
    # Create a test presentation first to have data for testing
    print("2. Creating test presentation...")
    create_response = requests.post(f"{BACKEND_URL}/presentations/create", 
        json={
            "template_id": "business_pitch",
            "title": "Test Presentation",
            "data": {"test": "data"}
        },
        headers=headers
    )
    
    presentation_id = None
    if create_response.status_code == 200:
        presentation_id = create_response.json().get("presentation_id")
        print(f"✅ Test presentation created: {presentation_id}")
    else:
        print(f"❌ Failed to create test presentation: {create_response.status_code}")
        print(f"Response: {create_response.text}")
    print()
    
    # Test the failing endpoints
    failing_endpoints = [
        {
            "name": "GET /api/presentations/history",
            "method": "GET",
            "url": f"{BACKEND_URL}/presentations/history",
            "headers": headers
        },
        {
            "name": "GET /api/presentations/stats", 
            "method": "GET",
            "url": f"{BACKEND_URL}/presentations/stats",
            "headers": headers
        }
    ]
    
    # Add export endpoints if we have a presentation ID
    if presentation_id:
        export_formats = ["pptx", "pdf", "google-slides"]
        for format_type in export_formats:
            failing_endpoints.append({
                "name": f"POST /api/presentations/{presentation_id}/export/{format_type}",
                "method": "POST", 
                "url": f"{BACKEND_URL}/presentations/{presentation_id}/export/{format_type}",
                "headers": headers
            })
    
    # Test each failing endpoint
    for i, endpoint in enumerate(failing_endpoints, 3):
        print(f"{i}. Testing {endpoint['name']}...")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], headers=endpoint['headers'])
            else:
                response = requests.post(endpoint['url'], headers=endpoint['headers'])
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS")
                try:
                    data = response.json()
                    print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                except:
                    print("   Response is not JSON")
            else:
                print("   ❌ FAILED")
                print(f"   Response: {response.text}")
                
                # Try to get more detailed error information
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        print(f"   Error Detail: {error_data['detail']}")
                except:
                    pass
                    
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            print(f"   Traceback: {traceback.format_exc()}")
        
        print()
    
    print("=== TEST SUMMARY ===")
    print("Focus: Identifying root causes of 500 errors in presentation endpoints")
    print("Key findings will be reported to main agent for systematic fixes")

if __name__ == "__main__":
    test_presentation_endpoints()