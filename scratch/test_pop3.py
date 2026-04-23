
import os
import poplib
from dotenv import load_dotenv

load_dotenv()

def test_pop3():
    host = os.getenv("POP3_HOST", "pop.gmail.com")
    port = int(os.getenv("POP3_PORT", "995"))
    user = os.getenv("POP3_USER")
    password = os.getenv("POP3_PASSWORD")

    print(f"Testing POP3 connection to {host}:{port} for user {user}...")
    
    try:
        server = poplib.POP3_SSL(host, port, timeout=10)
        print("Connected to server.")
        
        server.user(user)
        server.pass_(password)
        print("Authentication successful.")
        
        msg_count, size = server.stat()
        print(f"Inbox has {msg_count} messages, total size {size} bytes.")
        
        server.quit()
        print("Connection closed.")
        return True
    except Exception as e:
        print(f"POP3 Error: {e}")
        return False

if __name__ == "__main__":
    test_pop3()
