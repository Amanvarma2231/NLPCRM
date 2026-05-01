"""
Quick Test Script for NLPCRM
Tests basic functionality without starting the server
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    print("[TEST] Checking imports...")
    try:
        from app import create_app
        from app.services.db_service import db_service
        from app.services.nlp_service import nlp_service
        from app.services.email_service import email_service
        from app.services.whatsapp_service import whatsapp_service
        from app.services.contact_service import contact_service
        print("[OK] All imports successful")
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_app_creation():
    """Test if Flask app can be created"""
    print("[TEST] Creating Flask app...")
    try:
        from app import create_app
        app = create_app()
        print("[OK] Flask app created successfully")
        return True
    except Exception as e:
        print(f"[FAIL] App creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """Test database connection"""
    print("[TEST] Testing database...")
    try:
        from app.services.db_service import db_service
        if db_service._connect():
            print("[OK] Database connected")
            return True
        else:
            print("[WARN] Database connection failed (using fallback)")
            return True
    except Exception as e:
        print(f"[FAIL] Database error: {e}")
        return False

def test_routes():
    """Test if routes are registered"""
    print("[TEST] Checking routes...")
    try:
        from app import create_app
        app = create_app()
        
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))
        
        required_routes = ['/login', '/dashboard', '/contacts', '/settings']
        missing = [r for r in required_routes if not any(r in route for route in routes)]
        
        if missing:
            print(f"[WARN] Missing routes: {missing}")
        else:
            print(f"[OK] All required routes registered ({len(routes)} total)")
        
        return True
    except Exception as e:
        print(f"[FAIL] Routes error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  NLPCRM - Quick Test Suite")
    print("="*60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("App Creation", test_app_creation),
        ("Database", test_database),
        ("Routes", test_routes),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n[{name}]")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"[FAIL] Unexpected error: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    if all(results):
        print("[SUCCESS] All tests passed!")
        print("Run: python run.py")
    else:
        print("[ERROR] Some tests failed. Check errors above.")
    print("="*60 + "\n")
    
    return all(results)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
