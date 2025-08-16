#!/usr/bin/env python3
import requests
import json

def check_permissions():
    """Check if there are any user permissions in the database"""
    base_url = "http://localhost:8000/api/v1/users"
    headers = {"secret-key": "88AC1A95756D9259823CCA6E17145A0"}
    
    print("🔍 CHECKING USER PERMISSIONS IN DATABASE")
    print("=" * 50)
    
    # Test getting all user permissions
    print("\n1️⃣ Testing get all user permissions...")
    response = requests.get(f"{base_url}/user-permissions", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Permissions retrieved successfully!")
        print(f"📊 Total permissions: {len(data.get('data', []))}")
        
        if data.get('data'):
            print("\n📋 Sample permissions:")
            for i, perm in enumerate(data.get('data', [])[:3]):  # Show first 3
                print(f"   {i+1}. User Type ID: {perm.get('user_type_id')}")
                print(f"      Page ID: {perm.get('page_id')}")
                print(f"      Can View: {perm.get('can_view')}")
                print(f"      Can Create: {perm.get('can_create')}")
                print(f"      Can Update: {perm.get('can_update')}")
                print(f"      Can Delete: {perm.get('can_delete')}")
                print()
        else:
            print("❌ No permissions found in database")
    else:
        print(f"❌ Failed to get permissions: {response.text}")
    
    # Test getting permissions for user type 2 (Admin)
    print("\n2️⃣ Testing permissions for user type 2 (Admin)...")
    response = requests.get(f"{base_url}/user-permissions/user-type/2", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Admin permissions retrieved successfully!")
        print(f"📊 Total admin permissions: {len(data.get('data', []))}")
        
        if data.get('data'):
            print("\n📋 Admin permissions:")
            for i, perm in enumerate(data.get('data', [])):
                print(f"   {i+1}. Page ID: {perm.get('page_id')}")
                print(f"      Page Name: {perm.get('page_name', 'N/A')}")
                print(f"      Can View: {perm.get('can_view')}")
                print(f"      Can Create: {perm.get('can_create')}")
                print(f"      Can Update: {perm.get('can_update')}")
                print(f"      Can Delete: {perm.get('can_delete')}")
                print()
        else:
            print("❌ No admin permissions found")
    else:
        print(f"❌ Failed to get admin permissions: {response.text}")
    
    # Test getting permissions for user type 1 (Regular User)
    print("\n3️⃣ Testing permissions for user type 1 (Regular User)...")
    response = requests.get(f"{base_url}/user-permissions/user-type/1", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Regular user permissions retrieved successfully!")
        print(f"📊 Total regular user permissions: {len(data.get('data', []))}")
        
        if data.get('data'):
            print("\n📋 Regular user permissions:")
            for i, perm in enumerate(data.get('data', [])):
                print(f"   {i+1}. Page ID: {perm.get('page_id')}")
                print(f"      Page Name: {perm.get('page_name', 'N/A')}")
                print(f"      Can View: {perm.get('can_view')}")
                print(f"      Can Create: {perm.get('can_create')}")
                print(f"      Can Update: {perm.get('can_update')}")
                print(f"      Can Delete: {perm.get('can_delete')}")
                print()
        else:
            print("❌ No regular user permissions found")
    else:
        print(f"❌ Failed to get regular user permissions: {response.text}")
    
    print("\n" + "=" * 50)
    print("🎯 PERMISSIONS CHECK COMPLETED")
    print("\n📋 SUMMARY:")
    print("✅ If no permissions found, users will have empty permission arrays")
    print("✅ This is normal for new installations")
    print("✅ Permissions can be added through the admin interface")

if __name__ == "__main__":
    check_permissions() 