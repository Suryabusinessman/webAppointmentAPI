#!/usr/bin/env python3
import requests
import json

def test_user_creation():
    """Test the user creation endpoint"""
    url = "http://localhost:8000/api/v1/users/add-users"
    headers = {"secret-key": "88AC1A95756D9259823CCA6E17145A0"}
    
    # Test data
    data = {
        "full_name": "Test User Fix",
        "email": "testfix@example.com",
        "phone": "1234567890",
        "user_type_id": 1,
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ User creation successful!")
        elif response.status_code == 409:
            print("⚠️ Email already exists (expected behavior)")
        else:
            print("❌ User creation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_user_creation() 