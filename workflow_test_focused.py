#!/usr/bin/env python3

import requests
import json
from datetime import datetime

# Backend URL
BACKEND_URL = "https://ac96302a-4036-4647-87cc-d83a8a8750d7.preview.emergentagent.com"

def login():
    """Login and get token"""
    login_url = f"{BACKEND_URL}/api/auth/login"
    login_data = {"username": "admin", "password": "admin123"}
    
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Login successful. Token: {token[:10]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_workflow_system():
    """Test the workflow system comprehensively"""
    token = login()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n" + "="*60)
    print("WORKFLOW SYSTEM TESTING")
    print("="*60)
    
    # 1. Test workflow templates
    print("\n1. Testing GET /api/workflows/templates")
    templates_response = requests.get(f"{BACKEND_URL}/api/workflows/templates", headers=headers)
    print(f"Status: {templates_response.status_code}")
    
    if templates_response.status_code == 200:
        templates = templates_response.json()
        print(f"✅ Found {len(templates)} templates:")
        for template in templates:
            print(f"  - {template.get('name', 'Unknown')}: {len(template.get('steps', []))} steps")
            print(f"    Variables: {list(template.get('variables', {}).keys())}")
    else:
        print(f"❌ Templates request failed: {templates_response.text}")
        return
    
    # 2. Create workflow from template
    if templates:
        template = templates[0]
        template_id = template["template_id"]
        print(f"\n2. Testing workflow creation from template: {template['name']}")
        
        # Prepare variables
        variables = {}
        for var_name, var_value in template.get("variables", {}).items():
            variables[var_name] = f"test_{var_name}_value"
        
        print(f"Variables to send: {variables}")
        
        create_response = requests.post(
            f"{BACKEND_URL}/api/workflows/from-template/{template_id}",
            json=variables,
            headers=headers
        )
        print(f"Status: {create_response.status_code}")
        
        if create_response.status_code == 200:
            workflow = create_response.json()
            workflow_id = workflow["workflow_id"]
            print(f"✅ Created workflow: {workflow['name']} (ID: {workflow_id})")
            
            # 3. Test workflow execution
            print(f"\n3. Testing workflow execution")
            execution_data = {
                "input_variables": variables,
                "run_name": f"Test execution {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            print(f"Execution data: {execution_data}")
            
            execute_response = requests.post(
                f"{BACKEND_URL}/api/workflows/{workflow_id}/execute",
                json=execution_data,
                headers=headers
            )
            print(f"Execution status: {execute_response.status_code}")
            print(f"Execution response: {execute_response.text}")
            
            if execute_response.status_code == 200:
                execution = execute_response.json()
                print(f"✅ Execution started: {execution.get('execution_id', 'Unknown')}")
            else:
                print(f"⚠️ Execution failed: {execute_response.text}")
        else:
            print(f"❌ Workflow creation failed: {create_response.text}")
    
    # 4. Test getting user workflows
    print(f"\n4. Testing GET /api/workflows/")
    workflows_response = requests.get(f"{BACKEND_URL}/api/workflows/", headers=headers)
    print(f"Status: {workflows_response.status_code}")
    
    if workflows_response.status_code == 200:
        workflows = workflows_response.json()
        print(f"✅ Found {len(workflows)} user workflows")
        for workflow in workflows:
            print(f"  - {workflow.get('name', 'Unknown')} ({workflow.get('status', 'Unknown')})")
    else:
        print(f"❌ User workflows request failed: {workflows_response.text}")
    
    # 5. Test getting executions
    print(f"\n5. Testing GET /api/workflows/executions/")
    executions_response = requests.get(f"{BACKEND_URL}/api/workflows/executions/", headers=headers)
    print(f"Status: {executions_response.status_code}")
    
    if executions_response.status_code == 200:
        executions = executions_response.json()
        print(f"✅ Found {len(executions)} executions")
        for execution in executions:
            print(f"  - {execution.get('run_name', 'Unknown')} ({execution.get('status', 'Unknown')})")
    else:
        print(f"❌ Executions request failed: {executions_response.text}")

if __name__ == "__main__":
    test_workflow_system()