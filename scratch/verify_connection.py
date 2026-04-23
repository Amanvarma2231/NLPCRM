import requests

def test_email_connection():
    login_url = "http://127.0.0.1:5000/login"
    test_url = "http://127.0.0.1:5000/email/test-connection"
    
    session = requests.Session()
    
    # Get CSRF token
    print("Fetching login page for CSRF token...")
    login_page = session.get(login_url)
    import re
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text)
    if not csrf_match:
        # Try different quote style or order
        csrf_match = re.search(r'value="([^"]+)" name="csrf_token"', login_page.text)
    
    if csrf_match:
        csrf_token = csrf_match.group(1)
        print(f"CSRF Token found: {csrf_token[:10]}...")
    else:
        print("CSRF Token NOT found in login page.")
        print(login_page.text[:500])
        return

    # Login
    print("Logging in...")
    login_data = {
        "email": "admin@nlpcrm.com",
        "password": "admin@2026",
        "csrf_token": csrf_token
    }
    headers = {
        "X-CSRFToken": csrf_token,
        "Referer": login_url
    }
    login_resp = session.post(login_url, data=login_data, headers=headers, allow_redirects=True)
    
    if login_resp.status_code == 200:
        print(f"Login request finished. Final URL: {login_resp.url}")
        if "dashboard" in login_resp.url.lower() or "Dashboard" in login_resp.text:
            print("Login successful!")
        else:
            print("Login failed: Dashboard not reached.")
            error_match = re.search(r'class="alert-error"[^>]*>.*?</i>\s*(.*?)\s*</div>', login_resp.text, re.DOTALL)
            if error_match:
                print(f"Error message on page: {error_match.group(1).strip()}")
            else:
                print("No specific error message found on page.")
            return
    else:
        print(f"Login failed: {login_resp.status_code}")
        return

    # Test Connection
    print("Testing SMTP/POP3 connection...")
    test_resp = session.post(test_url)
    
    if test_resp.status_code == 200:
        print("Response received:")
        print(test_resp.json())
    else:
        print(f"Test failed with status code: {test_resp.status_code}")
        try:
            print(test_resp.json())
        except:
            print(test_resp.text[:500])

if __name__ == "__main__":
    test_email_connection()
