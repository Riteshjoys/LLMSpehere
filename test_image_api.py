import requests
import json

# Configuration
BASE_URL = "https://84a312aa-ca0e-453e-8c3d-7d809f4d1c5f.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Test image generation functionality
def test_image_generation():
    print("Testing Image Generation API")
    
    # 1. Login as admin
    login_payload = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    if login_response.status_code != 200:
        print(f"Failed to login: {login_response.status_code} - {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test image providers endpoint
    providers_response = requests.get(f"{BASE_URL}/providers/image", headers=headers)
    if providers_response.status_code != 200:
        print(f"Failed to get image providers: {providers_response.status_code} - {providers_response.text}")
    else:
        providers = providers_response.json().get("providers", [])
        print(f"Found {len(providers)} image providers:")
        for provider in providers:
            print(f"  - {provider.get('name')}: {provider.get('description')}")
    
    # 3. Test OpenAI image generation (expect failure due to missing API key)
    openai_payload = {
        "provider_name": "openai",
        "model": "gpt-image-1",
        "prompt": "A futuristic city with flying cars",
        "number_of_images": 1
    }
    
    openai_response = requests.post(f"{BASE_URL}/generate/image", json=openai_payload, headers=headers)
    print(f"OpenAI image generation response: {openai_response.status_code}")
    print(f"Response text: {openai_response.text}")
    
    # 4. Test fal.ai image generation (expect failure due to missing API key)
    fal_payload = {
        "provider_name": "fal",
        "model": "flux-dev",
        "prompt": "A cyberpunk street scene at night",
        "number_of_images": 1
    }
    
    fal_response = requests.post(f"{BASE_URL}/generate/image", json=fal_payload, headers=headers)
    print(f"fal.ai image generation response: {fal_response.status_code}")
    print(f"Response text: {fal_response.text}")
    
    # 5. Test image history endpoint
    history_response = requests.get(f"{BASE_URL}/generations/images", headers=headers)
    if history_response.status_code != 200:
        print(f"Failed to get image history: {history_response.status_code} - {history_response.text}")
    else:
        generations = history_response.json().get("generations", [])
        print(f"Found {len(generations)} image generations in history")

if __name__ == "__main__":
    test_image_generation()