#!/usr/bin/env python3
import requests
import json

def test_users_api():
    """Test the users API functionality"""
    base_url = "http://localhost:8000/api/v1/users"
    headers = {"secret-key": "88AC1A95756D9259823CCA6E17145A0"}
    
    # Test 1: Get all users
    print("=== Testing GET all users ===")
    response = requests.get(f"{base_url}/all-users", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        users = data.get('data', [])
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  User ID: {user['user_id']}, Name: {user['full_name']}, Email: {user['email']}")
        
        # Test 2: Update the first user
        if users:
            first_user = users[0]
            user_id = first_user['user_id']
            print(f"\n=== Testing UPDATE user {user_id} ===")
            
            update_data = {
                'full_name': 'Updated Test User',
                'email': 'updated@example.com'
            }
            
            response = requests.put(f"{base_url}/update-user/{user_id}", 
                                 headers=headers, 
                                 data=update_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    
    # Test 3: Create a new user
    print(f"\n=== Testing CREATE new user ===")
    create_data = {
        'full_name': 'API Test User',
        'email': 'apitest@example.com',
        'phone': '5551234567',
        'user_type_id': 1,
        'password': 'testpassword123'
    }
    
    response = requests.post(f"{base_url}/add-users", 
                           headers=headers, 
                           data=create_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_users_api() 