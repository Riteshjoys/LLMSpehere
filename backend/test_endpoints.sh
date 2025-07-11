#!/bin/bash

echo "=== ContentForge API Test ==="
echo "Testing backend endpoints..."

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s http://localhost:8001/api/health | jq . || echo "Health endpoint failed"

echo -e "\n2. Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "Login successful: $(echo $LOGIN_RESPONSE | jq -r '.token_type')"

echo -e "\n3. Testing providers endpoint..."
curl -s http://localhost:8001/api/providers -H "Authorization: Bearer $TOKEN" | jq '.providers | length' || echo "Providers endpoint failed"

echo -e "\n4. Testing dashboard statistics..."
curl -s http://localhost:8001/api/dashboard/statistics -H "Authorization: Bearer $TOKEN" | jq '.statistics' || echo "Dashboard statistics failed"

echo -e "\n5. Testing workflow monitoring..."
curl -s http://localhost:8001/api/workflow-monitoring/real-time-status -H "Authorization: Bearer $TOKEN" | jq '.timestamp' || echo "Workflow monitoring failed"

echo -e "\n6. Testing API keys status..."
curl -s http://localhost:8001/api/admin/api-keys/status -H "Authorization: Bearer $TOKEN" | jq '.api_keys_status | keys' || echo "API keys status failed"

echo -e "\n=== Test Complete ==="