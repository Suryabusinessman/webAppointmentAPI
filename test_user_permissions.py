import requests
import json

def test_user_permissions_endpoint():
    """Test the user permissions endpoint to verify it returns page names and user type names"""
    
    url = "http://127.0.0.1:8000/api/v1/user-permissions/all-user-permissions"
    
    headers = {
        "Content-Type": "application/json",
        "secret-key": "88AC1A95756D9259823CCA6E17145A0"
    }
    
    print(f"Testing endpoint: {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success! Response:")
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            
            if 'data' in data and data['data']:
                print(f"\n📋 Sample User Permission Data:")
                sample_permission = data['data'][0]
                
                # Print all fields to verify the structure
                print(json.dumps(sample_permission, indent=2))
                
                # Verify that the required fields are present
                required_fields = ['user_type_name', 'page_name', 'page_display_text']
                missing_fields = [field for field in required_fields if not sample_permission.get(field)]
                
                if missing_fields:
                    print(f"\n❌ Missing required fields: {missing_fields}")
                else:
                    print(f"\n✅ All required fields are present!")
                    
            else:
                print(f"\n⚠️ No data returned")
                
        else:
            print(f"\n❌ Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_user_permissions_endpoint()
