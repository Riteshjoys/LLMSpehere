#!/usr/bin/env python3

import requests
import json
import sys
import traceback
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://55b0d0ee-c62d-4529-88fb-7de3d4a921c7.preview.emergentagent.com/api"

def test_single_endpoint(endpoint_name, method, url, headers, data=None):
    """Test a single endpoint and capture detailed error information"""
    print(f"\n=== TESTING {endpoint_name} ===")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=30)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            response = requests.request(method, url, headers=headers, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS")
            try:
                data = response.json()
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                if isinstance(data, dict) and len(str(data)) < 500:
                    print(f"Response data: {data}")
            except:
                print("Response is not JSON")
                print(f"Response text: {response.text[:200]}...")
        else:
            print("❌ FAILED")
            print(f"Response text: {response.text}")
            
            # Try to get more detailed error information
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    print(f"Error Detail: {error_data['detail']}")
            except:
                pass
                
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")

def main():
    print("=== DETAILED PRESENTATION ENDPOINT TESTING ===")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started at: {datetime.now()}")
    
    # First, login to get authentication token
    print("\n1. Authenticating...")
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
    
    # Create a test presentation first to have data for testing
    print("\n2. Creating test presentation...")
    create_response = requests.post(f"{BACKEND_URL}/presentations/create", 
        json={
            "template_id": "business_pitch",
            "title": "Test Presentation for Debugging",
            "data": {"test": "data", "debug": True}
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
        # Continue anyway to test other endpoints
    
    # Test each failing endpoint individually with detailed logging
    test_single_endpoint(
        "GET /api/presentations/history",
        "GET",
        f"{BACKEND_URL}/presentations/history",
        headers
    )
    
    test_single_endpoint(
        "GET /api/presentations/stats", 
        "GET",
        f"{BACKEND_URL}/presentations/stats",
        headers
    )
    
    if presentation_id:
        test_single_endpoint(
            f"POST /api/presentations/{presentation_id}/export/pptx",
            "POST",
            f"{BACKEND_URL}/presentations/{presentation_id}/export/pptx",
            headers
        )
        
        test_single_endpoint(
            f"POST /api/presentations/{presentation_id}/export/pdf",
            "POST", 
            f"{BACKEND_URL}/presentations/{presentation_id}/export/pdf",
            headers
        )
        
        test_single_endpoint(
            f"POST /api/presentations/{presentation_id}/export/google-slides",
            "POST",
            f"{BACKEND_URL}/presentations/{presentation_id}/export/google-slides", 
            headers
        )
    
    print("\n=== SUMMARY ===")
    print("All tested endpoints are returning 500 errors.")
    print("The issue appears to be in the presentation service implementation.")
    print("Check backend logs for detailed stack traces.")

if __name__ == "__main__":
    main()