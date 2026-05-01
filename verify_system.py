"""
NLPCRM System Verification Script
Tests all critical components before running the application
"""

import os
import sys
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("[FAIL] Python 3.9+ required. Current:", f"{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    required = [
        'flask', 'flask_cors', 'flask_wtf', 'flask_talisman', 'flask_limiter',
        'requests', 'sqlitecloud', 'dotenv', 'gunicorn'
    ]
    
    missing = []
    for package in required:
        pkg_name = package.replace('-', '_')
        if importlib.util.find_spec(pkg_name) is None:
            missing.append(package)
    
    if missing:
        print(f"[FAIL] Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("[OK] All dependencies installed")
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists('.env'):
        print("[FAIL] .env file not found")
        print("   Run: copy .env.example .env")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['SECRET_KEY', 'HF_API_KEY', 'ADMIN_EMAIL', 'ADMIN_PASSWORD']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"[WARN] Missing environment variables: {', '.join(missing)}")
        print("   Application will run with limited functionality")
    else:
        print("[OK] Environment configured")
    
    return True

def check_database():
    """Check database connectivity"""
    try:
        from app.services.db_service import db_service
        if db_service._connect():
            print("[OK] Database connected")
            return True
        else:
            print("[WARN] Database connection failed (will use local SQLite)")
            return True
    except Exception as e:
        print(f"[FAIL] Database error: {e}")
        return False

def check_ai_service():
    """Check AI/NLP service"""
    try:
        hf_key = os.getenv('HF_API_KEY')
        if not hf_key:
            print("[WARN] HF_API_KEY not set (AI features disabled)")
            return True
        
        from app.services.nlp_service import nlp_service
        print("[OK] AI service initialized")
        return True
    except Exception as e:
        print(f"[FAIL] AI service error: {e}")
        return False

def check_email_service():
    """Check email service configuration"""
    try:
        from app.services.email_service import email_service
        if email_service.is_configured():
            print("[OK] Email service configured")
        else:
            print("[WARN] Email not configured (optional)")
        return True
    except Exception as e:
        print(f"[FAIL] Email service error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  NLPCRM v3.1 - System Verification")
    print("="*60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment", check_env_file),
        ("Database", check_database),
        ("AI Service", check_ai_service),
        ("Email Service", check_email_service),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    if all(results[:4]):  # First 4 are critical
        print("[SUCCESS] System Ready! Run: python run.py")
        print("   Access: http://localhost:5000")
        print("   Login: admin@nlpcrm.com / admin@2026")
    else:
        print("[ERROR] System has critical errors. Fix them before running.")
    print("="*60 + "\n")
    
    return all(results[:4])

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
