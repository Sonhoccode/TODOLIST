import requests
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
LOGIN_URL = f"{BASE_URL}/auth/login/"
TASKS_URL = f"{BASE_URL}/todos/"

def test_login_and_access(username, password):
    print(f"Testing login for user: {username}")
    
    # 1. Login
    try:
        response = requests.post(LOGIN_URL, json={"username": username, "password": password})
        print(f"Login Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print("Login failed:", response.text)
            return
            
        data = response.json()
        token = data.get("key")
        
        if not token:
            print("No token key in response:", data)
            return
            
        print(f"Token received: {token[:10]}...")
        
    except Exception as e:
        print(f"Login request error: {e}")
        return

    # 2. Access Protected Resource
    print("\nTesting access to protected resource (List Tasks)...")
    headers = {
        "Authorization": f"Token {token}"
    }
    
    try:
        response = requests.get(TASKS_URL, headers=headers)
        print(f"Access Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Access successful!")
            print("Task count:", response.json().get('count', 'Unknown'))
        elif response.status_code == 401:
            print("Access denied (401). Token was rejected.")
            print("Response:", response.text)
        else:
            print(f"Unexpected status: {response.status_code}")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"Access request error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_login_token.py <username> <password>")
    else:
        test_login_and_access(sys.argv[1], sys.argv[2])
