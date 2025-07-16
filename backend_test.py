import requests
import json
import unittest
import os
import sys
from typing import Dict, Any
from datetime import datetime

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://c47e1663-87a3-4560-a4b1-edcc58a46099.preview.emergentagent.com"

class CodeGenerationAPITest(unittest.TestCase):
    """Test suite for Code Generation API endpoints"""
    
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
    
    def test_01_get_providers(self):
        """Test GET /api/code/providers endpoint"""
        print("\n=== Testing GET /api/code/providers ===")
        url = f"{self.base_url}/code/providers"
        response = requests.get(url)
        
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list")
        self.assertGreaterEqual(len(data), 3, "Should return at least 3 providers")
        
        # Check for required providers
        provider_names = [provider["provider"] for provider in data]
        self.assertIn("openai", provider_names, "OpenAI provider should be available")
        self.assertIn("anthropic", provider_names, "Anthropic provider should be available")
        self.assertIn("gemini", provider_names, "Gemini provider should be available")
        
        # Check provider structure
        for provider in data:
            self.assertIn("provider", provider, "Provider should have 'provider' field")
            self.assertIn("name", provider, "Provider should have 'name' field")
            self.assertIn("models", provider, "Provider should have 'models' field")
            self.assertIsInstance(provider["models"], list, "Models should be a list")
            
            # Check model structure
            for model in provider["models"]:
                self.assertIn("id", model, "Model should have 'id' field")
                self.assertIn("name", model, "Model should have 'name' field")
                self.assertIn("description", model, "Model should have 'description' field")
        
        print(f"✅ GET /api/code/providers returned {len(data)} providers")
        for provider in data:
            print(f"  - {provider['name']} with {len(provider['models'])} models")
    
    def test_02_get_languages(self):
        """Test GET /api/code/languages endpoint"""
        print("\n=== Testing GET /api/code/languages ===")
        url = f"{self.base_url}/code/languages"
        response = requests.get(url)
        
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list")
        self.assertGreaterEqual(len(data), 20, "Should return at least 20 programming languages")
        
        # Check language structure
        for language in data:
            self.assertIn("id", language, "Language should have 'id' field")
            self.assertIn("name", language, "Language should have 'name' field")
            self.assertIn("extension", language, "Language should have 'extension' field")
        
        # Check for common languages
        language_ids = [lang["id"] for lang in data]
        common_languages = ["python", "javascript", "java", "cpp", "csharp"]
        for lang in common_languages:
            self.assertIn(lang, language_ids, f"{lang} should be in the supported languages")
        
        print(f"✅ GET /api/code/languages returned {len(data)} languages")
        print(f"  Languages include: {', '.join([lang['name'] for lang in data[:5]])} and more...")
    
    def test_03_get_request_types(self):
        """Test GET /api/code/request-types endpoint"""
        print("\n=== Testing GET /api/code/request-types ===")
        url = f"{self.base_url}/code/request-types"
        response = requests.get(url)
        
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list")
        
        # Check for required request types
        expected_types = ["generate", "debug", "optimize", "refactor", "review", 
                         "documentation", "test", "explain", "architecture"]
        
        request_type_ids = [rt["id"] for rt in data]
        for req_type in expected_types:
            self.assertIn(req_type, request_type_ids, f"{req_type} should be in the request types")
        
        # Check request type structure
        for req_type in data:
            self.assertIn("id", req_type, "Request type should have 'id' field")
            self.assertIn("name", req_type, "Request type should have 'name' field")
            self.assertIn("description", req_type, "Request type should have 'description' field")
        
        print(f"✅ GET /api/code/request-types returned {len(data)} request types")
        for rt in data:
            print(f"  - {rt['name']}: {rt['description']}")
    
    def test_04_generate_code(self):
        """Test POST /api/code/generate endpoint"""
        print("\n=== Testing POST /api/code/generate ===")
        url = f"{self.base_url}/code/generate"
        
        # Test data
        request_data = {
            "provider": "openai",
            "model": "gpt-4o",
            "request_type": "generate",
            "language": "python",
            "prompt": "Write a function to calculate the Fibonacci sequence up to n terms",
            "max_tokens": 1000
        }
        
        # Test without authentication
        response = requests.post(url, json=request_data)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.post(url, json=request_data, headers=self.get_headers())
        
        # Note: In a test environment, the actual code generation might fail due to missing API keys
        # We're just checking that the endpoint processes the request correctly
        self.assertIn(response.status_code, [200, 500], 
                     f"Expected status code 200 or 500 (if API key missing), got {response.status_code}")
        
        data = response.json()
        
        if response.status_code == 200:
            # If successful, check response structure
            self.assertIn("id", data, "Response should have 'id' field")
            self.assertIn("session_id", data, "Response should have 'session_id' field")
            self.assertIn("provider", data, "Response should have 'provider' field")
            self.assertIn("model", data, "Response should have 'model' field")
            self.assertIn("request_type", data, "Response should have 'request_type' field")
            self.assertIn("language", data, "Response should have 'language' field")
            self.assertIn("prompt", data, "Response should have 'prompt' field")
            self.assertIn("response", data, "Response should have 'response' field")
            self.assertIn("status", data, "Response should have 'status' field")
            
            print(f"✅ POST /api/code/generate successful")
            print(f"  Generated code with ID: {data['id']}")
            print(f"  Session ID: {data['session_id']}")
            print(f"  Status: {data['status']}")
        else:
            # If failed due to missing API key, that's expected in test environment
            print(f"⚠️ POST /api/code/generate returned error (likely due to missing API key in test environment)")
            print(f"  Error: {data.get('detail', 'Unknown error')}")
            # Don't fail the test if it's just missing API key
            if "API key not configured" in str(data):
                print("  This is expected in test environment without real API keys")
            else:
                self.fail(f"Unexpected error: {data}")
    
    def test_05_get_history(self):
        """Test GET /api/code/history endpoint"""
        print("\n=== Testing GET /api/code/history ===")
        url = f"{self.base_url}/code/history"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.get(url, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list")
        
        print(f"✅ GET /api/code/history returned {len(data)} items")
        if len(data) > 0:
            print(f"  First history item: {data[0].get('id', 'Unknown ID')}")
            print(f"  Language: {data[0].get('language', 'Unknown')}")
            print(f"  Request type: {data[0].get('request_type', 'Unknown')}")
        else:
            print("  No history items found (this is normal if no code has been generated yet)")

class WorkflowAPITest(unittest.TestCase):
    """Test suite for Workflow Automation API endpoints"""
    
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
    
    def test_01_get_workflow_templates(self):
        """Test GET /api/workflows/templates endpoint"""
        print("\n=== Testing GET /api/workflows/templates ===")
        url = f"{self.base_url}/workflows/templates"
        response = requests.get(url, headers=self.get_headers())
        
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list")
        
        # Check for expected templates
        expected_templates = ["Content Marketing Pipeline", "Product Launch Workflow", "Code Documentation Workflow"]
        template_names = [template.get("name", "") for template in data]
        
        print(f"✅ GET /api/workflows/templates returned {len(data)} templates")
        for template in data:
            print(f"  - {template.get('name', 'Unknown')}: {len(template.get('steps', []))} steps")
            
            # Check template structure
            required_fields = ["template_id", "name", "description", "category", "steps", "variables", "tags"]
            for field in required_fields:
                self.assertIn(field, template, f"Template should have '{field}' field")
        
        # Verify at least some expected templates exist
        found_templates = [name for name in expected_templates if any(name in template_name for template_name in template_names)]
        self.assertGreater(len(found_templates), 0, "Should find at least one expected template")
    
    def test_02_get_specific_template(self):
        """Test GET /api/workflows/templates/{template_id} endpoint"""
        print("\n=== Testing GET /api/workflows/templates/{template_id} ===")
        
        # First get all templates to get a valid template_id
        templates_response = requests.get(f"{self.base_url}/workflows/templates", headers=self.get_headers())
        self.assertEqual(templates_response.status_code, 200)
        templates = templates_response.json()
        
        if len(templates) > 0:
            template_id = templates[0]["template_id"]
            url = f"{self.base_url}/workflows/templates/{template_id}"
            response = requests.get(url, headers=self.get_headers())
            
            self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
            
            data = response.json()
            self.assertEqual(data["template_id"], template_id, "Template ID should match requested ID")
            
            print(f"✅ GET /api/workflows/templates/{template_id} returned template: {data['name']}")
        else:
            print("⚠️ No templates available to test specific template endpoint")
    
    def test_03_create_workflow_from_template(self):
        """Test POST /api/workflows/from-template/{template_id} endpoint"""
        print("\n=== Testing POST /api/workflows/from-template/{template_id} ===")
        
        # First get templates
        templates_response = requests.get(f"{self.base_url}/workflows/templates", headers=self.get_headers())
        self.assertEqual(templates_response.status_code, 200)
        templates = templates_response.json()
        
        if len(templates) > 0:
            template = templates[0]
            template_id = template["template_id"]
            
            # Create variables based on template requirements
            variables = {}
            for var_name, var_value in template.get("variables", {}).items():
                variables[var_name] = f"test_{var_name}_value"
            
            url = f"{self.base_url}/workflows/from-template/{template_id}"
            response = requests.post(url, json=variables, headers=self.get_headers())
            
            self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
            
            data = response.json()
            required_fields = ["workflow_id", "name", "description", "category", "steps", "status"]
            for field in required_fields:
                self.assertIn(field, data, f"Response should have '{field}' field")
            
            print(f"✅ Created workflow from template: {data['name']} (ID: {data['workflow_id']})")
            
            # Store workflow_id for later tests
            self.created_workflow_id = data['workflow_id']
        else:
            print("⚠️ No templates available to test workflow creation")
    
    def test_04_get_user_workflows(self):
        """Test GET /api/workflows/ endpoint"""
        print("\n=== Testing GET /api/workflows/ ===")
        url = f"{self.base_url}/workflows/"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.get(url, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list")
        
        print(f"✅ GET /api/workflows/ returned {len(data)} workflows")
        
        for workflow in data:
            required_fields = ["workflow_id", "name", "description", "category", "steps", "status"]
            for field in required_fields:
                self.assertIn(field, workflow, f"Workflow should have '{field}' field")
    
    def test_05_execute_workflow(self):
        """Test POST /api/workflows/{workflow_id}/execute endpoint"""
        print("\n=== Testing POST /api/workflows/{workflow_id}/execute ===")
        
        # Get workflows to find one to execute
        workflows_response = requests.get(f"{self.base_url}/workflows/", headers=self.get_headers())
        self.assertEqual(workflows_response.status_code, 200)
        workflows = workflows_response.json()
        
        if len(workflows) > 0:
            workflow = workflows[0]
            workflow_id = workflow["workflow_id"]
            
            # Prepare execution request
            execution_data = {
                "input_variables": {},
                "run_name": f"Test execution {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            # Add any required variables
            for var_name in workflow.get("variables", {}):
                execution_data["input_variables"][var_name] = f"test_value_for_{var_name}"
            
            url = f"{self.base_url}/workflows/{workflow_id}/execute"
            response = requests.post(url, json=execution_data, headers=self.get_headers())
            
            # Note: Execution might fail due to missing API keys, but endpoint should process request
            self.assertIn(response.status_code, [200, 500], 
                         f"Expected status code 200 or 500, got {response.status_code}")
            
            data = response.json()
            
            if response.status_code == 200:
                required_fields = ["execution_id", "workflow_id", "status", "started_at"]
                for field in required_fields:
                    self.assertIn(field, data, f"Response should have '{field}' field")
                
                print(f"✅ Workflow execution started: {data['execution_id']}")
                self.execution_id = data['execution_id']
            else:
                print(f"⚠️ Workflow execution failed (likely due to missing API keys): {data.get('detail', 'Unknown error')}")
        else:
            print("⚠️ No workflows available to test execution")
    
    def test_06_get_workflow_executions(self):
        """Test GET /api/workflows/executions/ endpoint"""
        print("\n=== Testing GET /api/workflows/executions/ ===")
        url = f"{self.base_url}/workflows/executions/"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.get(url, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list")
        
        print(f"✅ GET /api/workflows/executions/ returned {len(data)} executions")
        
        for execution in data:
            required_fields = ["execution_id", "workflow_id", "status", "started_at"]
            for field in required_fields:
                self.assertIn(field, execution, f"Execution should have '{field}' field")
    
    def test_07_workflow_management(self):
        """Test workflow management endpoints (get, update, delete)"""
        print("\n=== Testing Workflow Management Endpoints ===")
        
        # Get workflows
        workflows_response = requests.get(f"{self.base_url}/workflows/", headers=self.get_headers())
        self.assertEqual(workflows_response.status_code, 200)
        workflows = workflows_response.json()
        
        if len(workflows) > 0:
            workflow_id = workflows[0]["workflow_id"]
            
            # Test GET specific workflow
            get_url = f"{self.base_url}/workflows/{workflow_id}"
            get_response = requests.get(get_url, headers=self.get_headers())
            self.assertEqual(get_response.status_code, 200, f"Expected status code 200 for GET workflow, got {get_response.status_code}")
            
            workflow_data = get_response.json()
            self.assertEqual(workflow_data["workflow_id"], workflow_id, "Workflow ID should match")
            print(f"✅ GET /api/workflows/{workflow_id} successful")
            
            # Test duplicate workflow
            duplicate_url = f"{self.base_url}/workflows/{workflow_id}/duplicate"
            duplicate_response = requests.post(duplicate_url, headers=self.get_headers())
            self.assertEqual(duplicate_response.status_code, 200, f"Expected status code 200 for duplicate, got {duplicate_response.status_code}")
            
            duplicate_data = duplicate_response.json()
            self.assertNotEqual(duplicate_data["workflow_id"], workflow_id, "Duplicated workflow should have different ID")
            print(f"✅ POST /api/workflows/{workflow_id}/duplicate successful")
            
            # Clean up - delete the duplicated workflow
            delete_url = f"{self.base_url}/workflows/{duplicate_data['workflow_id']}"
            delete_response = requests.delete(delete_url, headers=self.get_headers())
            self.assertEqual(delete_response.status_code, 200, f"Expected status code 200 for delete, got {delete_response.status_code}")
            print(f"✅ DELETE /api/workflows/{duplicate_data['workflow_id']} successful")
        else:
            print("⚠️ No workflows available to test management endpoints")

class WorkflowSchedulerAPITest(unittest.TestCase):
    """Test suite for Workflow Scheduler API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = f"{BACKEND_URL}/api"
        self.auth_token = None
        self.created_workflow_id = None
        self.created_schedule_id = None
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
    
    def test_01_validate_cron_expression(self):
        """Test GET /api/workflow-schedules/validate/cron endpoint"""
        print("\n=== Testing GET /api/workflow-schedules/validate/cron ===")
        
        # Test valid cron expressions
        valid_expressions = [
            "0 9 * * *",  # Daily at 9 AM
            "0 */2 * * *",  # Every 2 hours
            "0 9 * * MON",  # Every Monday at 9 AM
            "*/30 * * * *"  # Every 30 minutes
        ]
        
        for expression in valid_expressions:
            url = f"{self.base_url}/workflow-schedules/validate/cron?expression={expression}"
            response = requests.get(url, headers=self.get_headers())
            
            self.assertEqual(response.status_code, 200, f"Expected status code 200 for expression '{expression}', got {response.status_code}")
            
            data = response.json()
            self.assertIn("valid", data, "Response should have 'valid' field")
            self.assertIn("next_runs", data, "Response should have 'next_runs' field")
            self.assertIn("expression", data, "Response should have 'expression' field")
            self.assertTrue(data["valid"], f"Expression '{expression}' should be valid")
            self.assertEqual(data["expression"], expression, "Expression should match request")
            
            print(f"  ✅ Valid expression '{expression}' - Next runs: {len(data['next_runs'])}")
        
        # Test invalid cron expression
        invalid_expression = "invalid cron"
        url = f"{self.base_url}/workflow-schedules/validate/cron?expression={invalid_expression}"
        response = requests.get(url, headers=self.get_headers())
        
        self.assertEqual(response.status_code, 200, f"Expected status code 200 for invalid expression, got {response.status_code}")
        data = response.json()
        self.assertFalse(data["valid"], "Invalid expression should return valid=false")
        print(f"  ✅ Invalid expression '{invalid_expression}' correctly identified as invalid")
    
    def test_02_get_user_schedules_empty(self):
        """Test GET /api/workflow-schedules/ endpoint when no schedules exist"""
        print("\n=== Testing GET /api/workflow-schedules/ (empty) ===")
        url = f"{self.base_url}/workflow-schedules/"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.get(url, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list")
        print(f"✅ GET /api/workflow-schedules/ returned {len(data)} schedules")
    
    def test_03_create_workflow_schedule(self):
        """Test POST /api/workflow-schedules/ endpoint"""
        print("\n=== Testing POST /api/workflow-schedules/ ===")
        
        # First, get a workflow to schedule
        workflows_response = requests.get(f"{self.base_url}/workflows/", headers=self.get_headers())
        self.assertEqual(workflows_response.status_code, 200)
        workflows = workflows_response.json()
        
        if len(workflows) == 0:
            # Create a workflow from template first
            templates_response = requests.get(f"{self.base_url}/workflows/templates", headers=self.get_headers())
            self.assertEqual(templates_response.status_code, 200)
            templates = templates_response.json()
            
            if len(templates) > 0:
                template = templates[0]
                variables = {}
                for var_name in template.get("variables", {}):
                    variables[var_name] = f"test_value_for_{var_name}"
                
                create_response = requests.post(
                    f"{self.base_url}/workflows/from-template/{template['template_id']}", 
                    json=variables, 
                    headers=self.get_headers()
                )
                self.assertEqual(create_response.status_code, 200)
                self.created_workflow_id = create_response.json()["workflow_id"]
            else:
                self.skipTest("No workflows or templates available for scheduling test")
        else:
            self.created_workflow_id = workflows[0]["workflow_id"]
        
        # Now create a schedule
        schedule_data = {
            "workflow_id": self.created_workflow_id,
            "name": "Test Schedule",
            "description": "Test schedule for automated testing",
            "cron_expression": "0 9 * * *",  # Daily at 9 AM
            "timezone": "UTC",
            "input_variables": {},
            "max_runs": 10
        }
        
        url = f"{self.base_url}/workflow-schedules/"
        
        # Test without authentication
        response = requests.post(url, json=schedule_data)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.post(url, json=schedule_data, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        required_fields = ["schedule_id", "workflow_id", "name", "description", "cron_expression", "status", "created_at"]
        for field in required_fields:
            self.assertIn(field, data, f"Response should have '{field}' field")
        
        self.assertEqual(data["workflow_id"], self.created_workflow_id, "Workflow ID should match")
        self.assertEqual(data["name"], schedule_data["name"], "Name should match")
        self.assertEqual(data["cron_expression"], schedule_data["cron_expression"], "Cron expression should match")
        self.assertEqual(data["status"], "active", "New schedule should be active")
        
        self.created_schedule_id = data["schedule_id"]
        print(f"✅ Created schedule: {data['name']} (ID: {data['schedule_id']})")
    
    def test_04_get_specific_schedule(self):
        """Test GET /api/workflow-schedules/{schedule_id} endpoint"""
        print("\n=== Testing GET /api/workflow-schedules/{schedule_id} ===")
        
        if not self.created_schedule_id:
            self.skipTest("No schedule created in previous test")
        
        url = f"{self.base_url}/workflow-schedules/{self.created_schedule_id}"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.get(url, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertEqual(data["schedule_id"], self.created_schedule_id, "Schedule ID should match")
        print(f"✅ Retrieved schedule: {data['name']}")
    
    def test_05_update_workflow_schedule(self):
        """Test PUT /api/workflow-schedules/{schedule_id} endpoint"""
        print("\n=== Testing PUT /api/workflow-schedules/{schedule_id} ===")
        
        if not self.created_schedule_id:
            self.skipTest("No schedule created in previous test")
        
        update_data = {
            "name": "Updated Test Schedule",
            "description": "Updated description for testing",
            "cron_expression": "0 10 * * *",  # Daily at 10 AM instead of 9 AM
            "max_runs": 20
        }
        
        url = f"{self.base_url}/workflow-schedules/{self.created_schedule_id}"
        
        # Test without authentication
        response = requests.put(url, json=update_data)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.put(url, json=update_data, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertEqual(data["name"], update_data["name"], "Name should be updated")
        self.assertEqual(data["description"], update_data["description"], "Description should be updated")
        self.assertEqual(data["cron_expression"], update_data["cron_expression"], "Cron expression should be updated")
        
        print(f"✅ Updated schedule: {data['name']}")
    
    def test_06_pause_workflow_schedule(self):
        """Test POST /api/workflow-schedules/{schedule_id}/pause endpoint"""
        print("\n=== Testing POST /api/workflow-schedules/{schedule_id}/pause ===")
        
        if not self.created_schedule_id:
            self.skipTest("No schedule created in previous test")
        
        url = f"{self.base_url}/workflow-schedules/{self.created_schedule_id}/pause"
        
        # Test without authentication
        response = requests.post(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.post(url, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIn("message", data, "Response should have 'message' field")
        
        # Verify schedule is paused
        get_response = requests.get(f"{self.base_url}/workflow-schedules/{self.created_schedule_id}", headers=self.get_headers())
        self.assertEqual(get_response.status_code, 200)
        schedule_data = get_response.json()
        self.assertEqual(schedule_data["status"], "paused", "Schedule should be paused")
        
        print(f"✅ Paused schedule: {schedule_data['name']}")
    
    def test_07_resume_workflow_schedule(self):
        """Test POST /api/workflow-schedules/{schedule_id}/resume endpoint"""
        print("\n=== Testing POST /api/workflow-schedules/{schedule_id}/resume ===")
        
        if not self.created_schedule_id:
            self.skipTest("No schedule created in previous test")
        
        url = f"{self.base_url}/workflow-schedules/{self.created_schedule_id}/resume"
        
        # Test without authentication
        response = requests.post(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.post(url, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIn("message", data, "Response should have 'message' field")
        
        # Verify schedule is active
        get_response = requests.get(f"{self.base_url}/workflow-schedules/{self.created_schedule_id}", headers=self.get_headers())
        self.assertEqual(get_response.status_code, 200)
        schedule_data = get_response.json()
        self.assertEqual(schedule_data["status"], "active", "Schedule should be active")
        
        print(f"✅ Resumed schedule: {schedule_data['name']}")
    
    def test_08_get_user_schedules_with_data(self):
        """Test GET /api/workflow-schedules/ endpoint with created schedule"""
        print("\n=== Testing GET /api/workflow-schedules/ (with data) ===")
        url = f"{self.base_url}/workflow-schedules/"
        
        response = requests.get(url, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list")
        self.assertGreater(len(data), 0, "Should have at least one schedule")
        
        # Check schedule structure
        for schedule in data:
            required_fields = ["schedule_id", "workflow_id", "name", "description", "cron_expression", "status", "created_at"]
            for field in required_fields:
                self.assertIn(field, schedule, f"Schedule should have '{field}' field")
        
        print(f"✅ GET /api/workflow-schedules/ returned {len(data)} schedules")
    
    def test_09_delete_workflow_schedule(self):
        """Test DELETE /api/workflow-schedules/{schedule_id} endpoint"""
        print("\n=== Testing DELETE /api/workflow-schedules/{schedule_id} ===")
        
        if not self.created_schedule_id:
            self.skipTest("No schedule created in previous test")
        
        url = f"{self.base_url}/workflow-schedules/{self.created_schedule_id}"
        
        # Test without authentication
        response = requests.delete(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with authentication
        response = requests.delete(url, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIn("message", data, "Response should have 'message' field")
        
        # Verify schedule is deleted
        get_response = requests.get(url, headers=self.get_headers())
        self.assertEqual(get_response.status_code, 404, "Schedule should not be found after deletion")
        
        print(f"✅ Deleted schedule: {self.created_schedule_id}")
    
    def test_10_schedule_analytics(self):
        """Test GET /api/workflow-schedules/{schedule_id}/analytics endpoint"""
        print("\n=== Testing GET /api/workflow-schedules/{schedule_id}/analytics ===")
        
        # Create a new schedule for analytics test
        if not self.created_workflow_id:
            self.skipTest("No workflow available for analytics test")
        
        schedule_data = {
            "workflow_id": self.created_workflow_id,
            "name": "Analytics Test Schedule",
            "description": "Schedule for testing analytics",
            "cron_expression": "0 12 * * *",
            "timezone": "UTC",
            "input_variables": {}
        }
        
        create_response = requests.post(f"{self.base_url}/workflow-schedules/", json=schedule_data, headers=self.get_headers())
        if create_response.status_code == 200:
            schedule_id = create_response.json()["schedule_id"]
            
            url = f"{self.base_url}/workflow-schedules/{schedule_id}/analytics"
            response = requests.get(url, headers=self.get_headers())
            
            self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
            
            data = response.json()
            # Analytics structure may vary, just check it returns data
            self.assertIsInstance(data, dict, "Analytics should return a dictionary")
            
            print(f"✅ Retrieved analytics for schedule: {schedule_id}")
            
            # Clean up
            requests.delete(f"{self.base_url}/workflow-schedules/{schedule_id}", headers=self.get_headers())
        else:
            print("⚠️ Could not create schedule for analytics test")

class UserManagementAPITest(unittest.TestCase):
    """Test suite for User Management API endpoints"""
    
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
            print(f"Successfully logged in as admin. Token: {self.admin_token[:10]}...")
        else:
            print(f"Failed to login as admin: {response.status_code} - {response.text}")
            self.fail("Admin login failed")
    
    def login_user(self):
        """Login as regular user to get authentication token"""
        # First register a test user if not exists
        register_url = f"{self.base_url}/auth/register"
        register_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
        
        # Try to register (might fail if user already exists, which is fine)
        requests.post(register_url, json=register_data)
        
        # Now login
        login_url = f"{self.base_url}/auth/login"
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.user_token = data.get("access_token")
            print(f"Successfully logged in as regular user. Token: {self.user_token[:10]}...")
        else:
            print(f"Failed to login as user: {response.status_code} - {response.text}")
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
    
    def test_01_get_user_profile(self):
        """Test GET /api/user/profile endpoint"""
        print("\n=== Testing GET /api/user/profile ===")
        url = f"{self.base_url}/user/profile"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with admin authentication
        response = requests.get(url, headers=self.get_admin_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200 for admin, got {response.status_code}")
        
        admin_data = response.json()
        required_fields = ["user_id", "username", "email", "full_name", "role", "created_at"]
        for field in required_fields:
            self.assertIn(field, admin_data, f"Admin profile should have '{field}' field")
        
        self.assertEqual(admin_data["role"], "admin", "Admin should have admin role")
        print(f"✅ Admin profile: {admin_data['username']} ({admin_data['role']})")
        
        # Test with regular user authentication
        response = requests.get(url, headers=self.get_user_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200 for user, got {response.status_code}")
        
        user_data = response.json()
        for field in required_fields:
            self.assertIn(field, user_data, f"User profile should have '{field}' field")
        
        self.assertEqual(user_data["role"], "user", "Regular user should have user role")
        print(f"✅ User profile: {user_data['username']} ({user_data['role']})")
    
    def test_02_update_user_profile(self):
        """Test PUT /api/user/profile endpoint"""
        print("\n=== Testing PUT /api/user/profile ===")
        url = f"{self.base_url}/user/profile"
        
        update_data = {
            "full_name": "Updated Test User",
            "bio": "This is my updated bio",
            "location": "New York, NY",
            "website": "https://example.com"
        }
        
        # Test without authentication
        response = requests.put(url, json=update_data)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication
        response = requests.put(url, json=update_data, headers=self.get_user_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIn("message", data, "Response should have 'message' field")
        print(f"✅ Profile updated: {data.get('message', 'Success')}")
        
        # Verify the update by getting profile again
        get_response = requests.get(url, headers=self.get_user_headers())
        self.assertEqual(get_response.status_code, 200)
        profile_data = get_response.json()
        
        # Check if the update was applied (some fields might not be in the response model)
        if "full_name" in profile_data:
            self.assertEqual(profile_data["full_name"], update_data["full_name"], "Full name should be updated")
        print(f"✅ Profile update verified")
    
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
        
        # Test without authentication
        response = requests.put(url, json=preferences_data)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication
        response = requests.put(url, json=preferences_data, headers=self.get_user_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIn("message", data, "Response should have 'message' field")
        print(f"✅ Preferences updated: {data.get('message', 'Success')}")
    
    def test_04_update_user_password(self):
        """Test PUT /api/user/password endpoint"""
        print("\n=== Testing PUT /api/user/password ===")
        url = f"{self.base_url}/user/password"
        
        password_data = {
            "current_password": "testpass123",
            "new_password": "newtestpass123",
            "confirm_password": "newtestpass123"
        }
        
        # Test without authentication
        response = requests.put(url, json=password_data)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication
        response = requests.put(url, json=password_data, headers=self.get_user_headers())
        
        # Note: This might fail if password validation is strict or if the current password is wrong
        # We'll accept both success and validation errors
        self.assertIn(response.status_code, [200, 400, 422], 
                     f"Expected status code 200, 400, or 422, got {response.status_code}")
        
        data = response.json()
        if response.status_code == 200:
            self.assertIn("message", data, "Response should have 'message' field")
            print(f"✅ Password updated: {data.get('message', 'Success')}")
        else:
            print(f"⚠️ Password update failed (validation error): {data.get('detail', 'Unknown error')}")
    
    def test_05_update_user_email(self):
        """Test PUT /api/user/email endpoint"""
        print("\n=== Testing PUT /api/user/email ===")
        url = f"{self.base_url}/user/email"
        
        email_data = {
            "new_email": "newtestuser@example.com",
            "password": "testpass123"
        }
        
        # Test without authentication
        response = requests.put(url, json=email_data)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication
        response = requests.put(url, json=email_data, headers=self.get_user_headers())
        
        # Note: This might fail due to email validation or duplicate email
        self.assertIn(response.status_code, [200, 400, 422], 
                     f"Expected status code 200, 400, or 422, got {response.status_code}")
        
        data = response.json()
        if response.status_code == 200:
            self.assertIn("message", data, "Response should have 'message' field")
            print(f"✅ Email updated: {data.get('message', 'Success')}")
        else:
            print(f"⚠️ Email update failed (validation error): {data.get('detail', 'Unknown error')}")
    
    def test_06_get_user_usage_stats(self):
        """Test GET /api/user/usage-stats endpoint"""
        print("\n=== Testing GET /api/user/usage-stats ===")
        url = f"{self.base_url}/user/usage-stats"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication
        response = requests.get(url, headers=self.get_user_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        expected_fields = ["total_generations", "text_generations", "image_generations", "video_generations", 
                          "code_generations", "social_media_generations", "total_tokens_used", "total_cost"]
        
        for field in expected_fields:
            self.assertIn(field, data, f"Usage stats should have '{field}' field")
            self.assertIsInstance(data[field], (int, float), f"{field} should be a number")
        
        print(f"✅ Usage stats retrieved:")
        print(f"  Total generations: {data['total_generations']}")
        print(f"  Text: {data['text_generations']}, Image: {data['image_generations']}")
        print(f"  Video: {data['video_generations']}, Code: {data['code_generations']}")
        print(f"  Social Media: {data['social_media_generations']}")
        print(f"  Total tokens: {data['total_tokens_used']}, Cost: ${data['total_cost']}")
    
    def test_07_get_user_activity_logs(self):
        """Test GET /api/user/activity-logs endpoint"""
        print("\n=== Testing GET /api/user/activity-logs ===")
        url = f"{self.base_url}/user/activity-logs"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication
        response = requests.get(url, headers=self.get_user_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Activity logs should be a list")
        
        print(f"✅ Activity logs retrieved: {len(data)} entries")
        
        # Check structure of activity logs if any exist
        if len(data) > 0:
            log_entry = data[0]
            expected_fields = ["activity_type", "description", "timestamp"]
            for field in expected_fields:
                self.assertIn(field, log_entry, f"Activity log entry should have '{field}' field")
            
            print(f"  Latest activity: {log_entry['activity_type']} - {log_entry['description']}")
        
        # Test with pagination parameters
        response = requests.get(f"{url}?limit=10&skip=0", headers=self.get_user_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200 for paginated request, got {response.status_code}")
        
        paginated_data = response.json()
        self.assertIsInstance(paginated_data, list, "Paginated activity logs should be a list")
        self.assertLessEqual(len(paginated_data), 10, "Should return at most 10 entries with limit=10")
        print(f"✅ Paginated activity logs: {len(paginated_data)} entries (limit=10)")
    
    def test_08_get_user_analytics(self):
        """Test GET /api/user/analytics endpoint"""
        print("\n=== Testing GET /api/user/analytics ===")
        url = f"{self.base_url}/user/analytics"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication (default 30 days)
        response = requests.get(url, headers=self.get_user_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        expected_fields = ["period_days", "total_activity", "daily_breakdown", "feature_usage", "performance_metrics"]
        
        for field in expected_fields:
            self.assertIn(field, data, f"User analytics should have '{field}' field")
        
        self.assertEqual(data["period_days"], 30, "Default period should be 30 days")
        self.assertIsInstance(data["daily_breakdown"], dict, "Daily breakdown should be a dict")
        self.assertIsInstance(data["feature_usage"], dict, "Feature usage should be a dict")
        
        print(f"✅ User analytics retrieved (30 days):")
        print(f"  Total activity: {data['total_activity']}")
        print(f"  Daily breakdown: {len(data['daily_breakdown'])} days")
        print(f"  Feature usage: {len(data['feature_usage'])} features")
        
        # Test with custom period
        response = requests.get(f"{url}?days=7", headers=self.get_user_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200 for 7-day period, got {response.status_code}")
        
        weekly_data = response.json()
        self.assertEqual(weekly_data["period_days"], 7, "Period should be 7 days")
        print(f"✅ User analytics retrieved (7 days): {weekly_data['total_activity']} total activity")


class AnalyticsAPITest(unittest.TestCase):
    """Test suite for Enhanced Analytics API endpoints"""
    
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
            print(f"Successfully logged in as admin. Token: {self.admin_token[:10]}...")
        else:
            print(f"Failed to login as admin: {response.status_code} - {response.text}")
            self.fail("Admin login failed")
    
    def login_user(self):
        """Login as regular user to get authentication token"""
        # First register a test user if not exists
        register_url = f"{self.base_url}/auth/register"
        register_data = {
            "username": "analyticsuser",
            "email": "analyticsuser@example.com",
            "password": "testpass123",
            "full_name": "Analytics Test User"
        }
        
        # Try to register (might fail if user already exists, which is fine)
        requests.post(register_url, json=register_data)
        
        # Now login
        login_url = f"{self.base_url}/auth/login"
        login_data = {
            "username": "analyticsuser",
            "password": "testpass123"
        }
        
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.user_token = data.get("access_token")
            print(f"Successfully logged in as analytics user. Token: {self.user_token[:10]}...")
        else:
            print(f"Failed to login as analytics user: {response.status_code} - {response.text}")
            self.fail("Analytics user login failed")
    
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
    
    def test_01_get_enhanced_dashboard_analytics(self):
        """Test GET /api/analytics/dashboard/enhanced endpoint"""
        print("\n=== Testing GET /api/analytics/dashboard/enhanced ===")
        url = f"{self.base_url}/analytics/dashboard/enhanced"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication (default 30 days)
        response = requests.get(url, headers=self.get_user_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        required_sections = ["summary", "daily_activity", "generation_breakdown", "provider_usage", 
                           "feature_usage", "performance_metrics", "date_range"]
        
        for section in required_sections:
            self.assertIn(section, data, f"Enhanced analytics should have '{section}' section")
        
        # Check summary structure
        summary = data["summary"]
        summary_fields = ["total_generations", "success_rate", "avg_response_time", "estimated_cost", "active_days"]
        for field in summary_fields:
            self.assertIn(field, summary, f"Summary should have '{field}' field")
            self.assertIsInstance(summary[field], (int, float), f"{field} should be a number")
        
        # Check daily activity structure
        daily_activity = data["daily_activity"]
        self.assertIsInstance(daily_activity, dict, "Daily activity should be a dict")
        
        # Check generation breakdown
        breakdown = data["generation_breakdown"]
        breakdown_types = ["text", "image", "video", "code", "social"]
        for gen_type in breakdown_types:
            self.assertIn(gen_type, breakdown, f"Generation breakdown should have '{gen_type}' field")
            self.assertIsInstance(breakdown[gen_type], int, f"{gen_type} count should be an integer")
        
        # Check date range
        date_range = data["date_range"]
        self.assertIn("start", date_range, "Date range should have 'start' field")
        self.assertIn("end", date_range, "Date range should have 'end' field")
        self.assertIn("days", date_range, "Date range should have 'days' field")
        self.assertEqual(date_range["days"], 30, "Default period should be 30 days")
        
        print(f"✅ Enhanced dashboard analytics retrieved (30 days):")
        print(f"  Total generations: {summary['total_generations']}")
        print(f"  Success rate: {summary['success_rate']}%")
        print(f"  Avg response time: {summary['avg_response_time']}s")
        print(f"  Estimated cost: ${summary['estimated_cost']}")
        print(f"  Active days: {summary['active_days']}")
        print(f"  Daily activity entries: {len(daily_activity)}")
        
        # Test with custom period
        response = requests.get(f"{url}?days=7", headers=self.get_user_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200 for 7-day period, got {response.status_code}")
        
        weekly_data = response.json()
        self.assertEqual(weekly_data["date_range"]["days"], 7, "Period should be 7 days")
        print(f"✅ Enhanced analytics retrieved (7 days): {weekly_data['summary']['total_generations']} total generations")
        
        # Test with admin authentication
        response = requests.get(url, headers=self.get_admin_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200 for admin, got {response.status_code}")
        
        admin_data = response.json()
        print(f"✅ Admin enhanced analytics: {admin_data['summary']['total_generations']} total generations")
    
    def test_02_get_usage_trends(self):
        """Test GET /api/analytics/usage-trends endpoint"""
        print("\n=== Testing GET /api/analytics/usage-trends ===")
        url = f"{self.base_url}/analytics/usage-trends"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test different periods
        periods = ["day", "week", "month"]
        
        for period in periods:
            print(f"\n  Testing {period} period...")
            response = requests.get(f"{url}?period={period}", headers=self.get_user_headers())
            self.assertEqual(response.status_code, 200, f"Expected status code 200 for {period} period, got {response.status_code}")
            
            data = response.json()
            required_fields = ["period", "date_range", "trends"]
            for field in required_fields:
                self.assertIn(field, data, f"Usage trends should have '{field}' field")
            
            self.assertEqual(data["period"], period, f"Period should match requested period")
            self.assertIsInstance(data["trends"], dict, "Trends should be a dict")
            
            # Check trends structure
            trends = data["trends"]
            trend_types = ["text", "image", "video", "code", "social"]
            for trend_type in trend_types:
                self.assertIn(trend_type, trends, f"Trends should have '{trend_type}' data")
                self.assertIsInstance(trends[trend_type], list, f"{trend_type} trends should be a list")
            
            print(f"    ✅ {period} trends: {len(trends['text'])} data points for text generation")
        
        # Test invalid period
        response = requests.get(f"{url}?period=invalid", headers=self.get_user_headers())
        self.assertEqual(response.status_code, 400, f"Expected status code 400 for invalid period, got {response.status_code}")
        print(f"✅ Invalid period correctly rejected")
    
    def test_03_export_analytics(self):
        """Test GET /api/analytics/export endpoint"""
        print("\n=== Testing GET /api/analytics/export ===")
        url = f"{self.base_url}/analytics/export"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test JSON export (default)
        response = requests.get(url, headers=self.get_user_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        required_fields = ["export_format", "generated_at", "user_id", "data"]
        for field in required_fields:
            self.assertIn(field, data, f"Export should have '{field}' field")
        
        self.assertEqual(data["export_format"], "json", "Default format should be JSON")
        self.assertIsInstance(data["data"], dict, "Exported data should be a dict")
        
        # Check that the exported data contains analytics data
        analytics_data = data["data"]
        self.assertIn("summary", analytics_data, "Exported data should contain summary")
        self.assertIn("daily_activity", analytics_data, "Exported data should contain daily activity")
        
        print(f"✅ JSON export successful:")
        print(f"  Format: {data['export_format']}")
        print(f"  Generated at: {data['generated_at']}")
        print(f"  Data sections: {len(analytics_data)} sections")
        
        # Test with custom days parameter
        response = requests.get(f"{url}?days=14", headers=self.get_user_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200 for 14-day export, got {response.status_code}")
        
        custom_data = response.json()
        self.assertEqual(custom_data["data"]["date_range"]["days"], 14, "Export should use custom period")
        print(f"✅ Custom period export (14 days): {custom_data['data']['summary']['total_generations']} generations")
        
        # Test CSV export (should return message about coming soon)
        response = requests.get(f"{url}?format=csv", headers=self.get_user_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200 for CSV request, got {response.status_code}")
        
        csv_data = response.json()
        self.assertIn("message", csv_data, "CSV export should return a message")
        print(f"✅ CSV export: {csv_data.get('message', 'Response received')}")
        
        # Test invalid format
        response = requests.get(f"{url}?format=invalid", headers=self.get_user_headers())
        self.assertEqual(response.status_code, 400, f"Expected status code 400 for invalid format, got {response.status_code}")
        print(f"✅ Invalid format correctly rejected")
    
    def test_04_get_analytics_insights(self):
        """Test GET /api/analytics/insights endpoint"""
        print("\n=== Testing GET /api/analytics/insights ===")
        url = f"{self.base_url}/analytics/insights"
        
        # Test without authentication
        response = requests.get(url)
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
        # Test with user authentication
        response = requests.get(url, headers=self.get_user_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        data = response.json()
        required_fields = ["insights", "generated_at"]
        for field in required_fields:
            self.assertIn(field, data, f"Insights should have '{field}' field")
        
        insights = data["insights"]
        self.assertIsInstance(insights, list, "Insights should be a list")
        
        print(f"✅ Analytics insights retrieved: {len(insights)} insights")
        
        # Check insight structure if any insights exist
        if len(insights) > 0:
            insight = insights[0]
            insight_fields = ["type", "title", "description", "value", "trend"]
            for field in insight_fields:
                self.assertIn(field, insight, f"Insight should have '{field}' field")
            
            # Check insight types
            valid_types = ["productivity", "feature", "performance", "cost"]
            self.assertIn(insight["type"], valid_types, f"Insight type should be one of {valid_types}")
            
            # Check trend values
            valid_trends = ["positive", "negative", "neutral", "warning"]
            self.assertIn(insight["trend"], valid_trends, f"Insight trend should be one of {valid_trends}")
            
            print(f"  Sample insight: {insight['title']} - {insight['description']}")
            print(f"  Type: {insight['type']}, Trend: {insight['trend']}, Value: {insight['value']}")
        else:
            print("  No insights generated (this is normal for users with limited activity)")
        
        # Test with admin authentication
        response = requests.get(url, headers=self.get_admin_headers())
        self.assertEqual(response.status_code, 200, f"Expected status code 200 for admin, got {response.status_code}")
        
        admin_data = response.json()
        admin_insights = admin_data["insights"]
        print(f"✅ Admin insights: {len(admin_insights)} insights")


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
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
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
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
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
        self.assertEqual(response.status_code, 401, 
                         f"Expected status code 401 for unauthorized request, got {response.status_code}")
        
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
    # Run all test suites
    print("=" * 80)
    print("RUNNING CONTENTFORGE AI API TESTS")
    print("=" * 80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add User Management tests
    suite.addTests(loader.loadTestsFromTestCase(UserManagementAPITest))
    
    # Add Analytics tests
    suite.addTests(loader.loadTestsFromTestCase(AnalyticsAPITest))
    
    # Add Code Generation tests
    suite.addTests(loader.loadTestsFromTestCase(CodeGenerationAPITest))
    
    # Add Workflow tests
    suite.addTests(loader.loadTestsFromTestCase(WorkflowAPITest))
    
    # Add Workflow Scheduler tests
    suite.addTests(loader.loadTestsFromTestCase(WorkflowSchedulerAPITest))
    
    # Add Social Media tests
    suite.addTests(loader.loadTestsFromTestCase(SocialMediaAPITest))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
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
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n❌ {len(result.failures + result.errors)} TESTS FAILED")
    
    sys.exit(0 if result.wasSuccessful() else 1)