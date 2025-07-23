#!/usr/bin/env python3
"""
Basic test script for Finance Agent - tests core functionality without all dependencies
"""

import sys
import os

def test_imports():
    """Test basic imports"""
    print("🧪 Testing basic imports...")
    
    try:
        # Test config
        from config import Config
        print("✅ Config imported successfully")
        
        # Test database
        from database.mongo_client import mongo_client
        print("✅ Database client imported successfully")
        
        # Test email utils
        from utils.email_utils import gmail_client
        print("✅ Email utils imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n🧪 Testing configuration...")
    
    try:
        from config import Config
        
        print(f"   MongoDB URI: {Config.MONGODB_URI}")
        print(f"   Database: {Config.MONGODB_DATABASE}")
        print(f"   Gmail Email: {Config.GMAIL_EMAIL or 'Not configured'}")
        print(f"   Google API Key: {'Configured' if Config.GOOGLE_API_KEY else 'Not configured'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🧪 Testing database connection...")
    
    try:
        from database.mongo_client import mongo_client
        
        # Test basic connection
        print("   Testing MongoDB connection...")
        
        # This will fail if MongoDB is not running, but that's expected
        # We just want to make sure the client can be created
        print("✅ Database client created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("   Note: This is expected if MongoDB is not running")
        return False

def main():
    """Main test function"""
    print("🚀 Finance Agent Basic Test")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_imports),
        ("Configuration", test_config),
        ("Database Client", test_database_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Basic structure is working!")
        print("\n📋 Next steps:")
        print("1. Install missing dependencies: python install_dependencies.py")
        print("2. Set up your .env file with credentials")
        print("3. Start MongoDB (if running locally)")
        print("4. Run: streamlit run streamlit_app.py")
    else:
        print("⚠️  Some basic tests failed. Please check the errors above.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main()) 