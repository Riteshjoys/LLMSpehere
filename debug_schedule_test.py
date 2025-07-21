#!/usr/bin/env python3

import requests
import json

# Backend URL
BACKEND_URL = "https://55b0d0ee-c62d-4529-88fb-7de3d4a921c7.preview.emergentagent.com"

def login():
    """Login and get token"""
    login_url = f"{BACKEND_URL}/api/auth/login"
    login_data = {"username": "admin", "password": "admin123"}
    
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_schedule_creation():
    """Test workflow schedule creation with detailed error reporting"""
    token = login()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("=== Testing Workflow Schedule Creation ===")
    
    # First get workflows
    print("\n1. Getting workflows...")
    workflows_response = requests.get(f"{BACKEND_URL}/api/workflows/", headers=headers)
    print(f"Workflows response: {workflows_response.status_code}")
    
    if workflows_response.status_code != 200:
        print(f"Failed to get workflows: {workflows_response.text}")
        return
    
    workflows = workflows_response.json()
    print(f"Found {len(workflows)} workflows")
    
    if len(workflows) == 0:
        print("No workflows found, creating one from template...")
        
        # Get templates
        templates_response = requests.get(f"{BACKEND_URL}/api/workflows/templates", headers=headers)
        if templates_response.status_code == 200:
            templates = templates_response.json()
            if len(templates) > 0:
                template = templates[0]
                print(f"Using template: {template['name']}")
                
                # Create workflow from template
                variables = {}
                for var_name in template.get("variables", {}):
                    variables[var_name] = f"test_value_for_{var_name}"
                
                create_response = requests.post(
                    f"{BACKEND_URL}/api/workflows/from-template/{template['template_id']}", 
                    json=variables, 
                    headers=headers
                )
                
                if create_response.status_code == 200:
                    workflow_data = create_response.json()
                    workflow_id = workflow_data["workflow_id"]
                    print(f"Created workflow: {workflow_data['name']} (ID: {workflow_id})")
                else:
                    print(f"Failed to create workflow: {create_response.status_code} - {create_response.text}")
                    return
            else:
                print("No templates available")
                return
        else:
            print(f"Failed to get templates: {templates_response.status_code} - {templates_response.text}")
            return
    else:
        workflow_id = workflows[0]["workflow_id"]
        print(f"Using existing workflow: {workflows[0]['name']} (ID: {workflow_id})")
    
    # Now test schedule creation
    print(f"\n2. Creating schedule for workflow {workflow_id}...")
    
    schedule_data = {
        "workflow_id": workflow_id,
        "name": "Debug Test Schedule",
        "description": "Test schedule for debugging",
        "cron_expression": "0 9 * * *",
        "timezone": "UTC",
        "input_variables": {},
        "max_runs": 10
    }
    
    print(f"Schedule data: {json.dumps(schedule_data, indent=2)}")
    
    response = requests.post(f"{BACKEND_URL}/api/workflow-schedules/", json=schedule_data, headers=headers)
    print(f"Schedule creation response: {response.status_code}")
    
    if response.status_code == 200:
        schedule = response.json()
        print(f"✅ Successfully created schedule: {schedule['name']} (ID: {schedule['schedule_id']})")
        print(f"Schedule details: {json.dumps(schedule, indent=2)}")
    else:
        print(f"❌ Failed to create schedule: {response.text}")
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            pass
    
    # Test cron validation
    print(f"\n3. Testing cron validation...")
    cron_response = requests.get(f"{BACKEND_URL}/api/workflow-schedules/validate/cron?expression=0 9 * * *", headers=headers)
    print(f"Cron validation response: {cron_response.status_code}")
    if cron_response.status_code == 200:
        cron_data = cron_response.json()
        print(f"Cron validation result: {json.dumps(cron_data, indent=2)}")
    else:
        print(f"Cron validation failed: {cron_response.text}")

if __name__ == "__main__":
    test_schedule_creation()