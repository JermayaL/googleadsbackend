#!/usr/bin/env python3
"""
Firebase Connection Test Script
Tests Firebase Admin SDK and Firestore connectivity
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

def test_imports():
    """Test if required packages can be imported."""
    print("🔍 Testing package imports...")
    
    try:
        import firebase_admin
        print("✅ firebase_admin imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import firebase_admin: {e}")
        print("💡 Install with: pip install firebase-admin")
        return False
    
    try:
        from firebase_admin import credentials, firestore
        print("✅ firebase_admin.credentials and firestore imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import firebase_admin modules: {e}")
        return False
    
    try:
        from google.cloud import firestore as firestore_client
        print("✅ google.cloud.firestore imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import google.cloud.firestore: {e}")
        print("💡 Install with: pip install google-cloud-firestore")
        return False
    
    return True

def check_service_account_file():
    """Check if service account file exists and is valid."""
    print("\n🔍 Checking service account file...")
    
    service_account_path = "firebase-service-account.json"
    
    if not os.path.exists(service_account_path):
        print(f"❌ Service account file not found: {service_account_path}")
        print("💡 Run the GCP setup script to create it")
        return False, None
    
    try:
        with open(service_account_path, 'r') as f:
            service_account_data = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in service_account_data]
        
        if missing_fields:
            print(f"❌ Service account file missing required fields: {missing_fields}")
            return False, None
        
        project_id = service_account_data.get('project_id')
        client_email = service_account_data.get('client_email')
        
        print(f"✅ Service account file is valid")
        print(f"   Project ID: {project_id}")
        print(f"   Client Email: {client_email}")
        
        return True, service_account_data
        
    except json.JSONDecodeError as e:
        print(f"❌ Service account file is not valid JSON: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Error reading service account file: {e}")
        return False, None

def test_firebase_admin_initialization(service_account_data: Dict[str, Any]) -> bool:
    """Test Firebase Admin SDK initialization."""
    print("\n🔍 Testing Firebase Admin SDK initialization...")
    
    try:
        import firebase_admin
        from firebase_admin import credentials
        
        # Clean up any existing apps first
        try:
            for app in firebase_admin._apps.values():
                firebase_admin.delete_app(app)
        except:
            pass
        
        # Initialize with service account
        cred = credentials.Certificate(service_account_data)
        app = firebase_admin.initialize_app(cred, {
            'projectId': service_account_data['project_id']
        })
        
        print("✅ Firebase Admin SDK initialized successfully")
        print(f"   App name: {app.name}")
        print(f"   Project ID: {app.project_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase Admin SDK initialization failed: {e}")
        return False

def test_firestore_connection(project_id: str) -> bool:
    """Test Firestore database connection."""
    print("\n🔍 Testing Firestore database connection...")
    
    try:
        from google.cloud import firestore
        
        # Initialize Firestore client
        db = firestore.Client(project=project_id)
        
        print("✅ Firestore client initialized successfully")
        
        # Test database access by trying to create a test document
        test_doc_ref = db.collection('health_check').document('connection_test')
        
        test_data = {
            'test': True,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'message': 'Firebase connection test successful',
            'python_version': sys.version,
            'created_by': 'test_firebase.py'
        }
        
        # Write test document
        test_doc_ref.set(test_data)
        print("✅ Test document written successfully")
        
        # Read test document back
        doc = test_doc_ref.get()
        if doc.exists:
            doc_data = doc.to_dict()
            print("✅ Test document read successfully")
            print(f"   Document ID: {doc.id}")
            print(f"   Test field: {doc_data.get('test')}")
            print(f"   Message: {doc_data.get('message')}")
        else:
            print("❌ Test document was not found after writing")
            return False
        
        # Clean up test document
        test_doc_ref.delete()
        print("✅ Test document cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Firestore connection test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Provide specific troubleshooting for common errors
        error_str = str(e).lower()
        if "does not exist" in error_str and "database" in error_str:
            print("💡 This error suggests the Firestore database doesn't exist")
            print("💡 Run the GCP setup script to create the database")
        elif "permission denied" in error_str:
            print("💡 This error suggests insufficient permissions")
            print("💡 Check IAM roles for your service account")
        elif "not found" in error_str:
            print("💡 This error suggests the project or resource doesn't exist")
            print("💡 Verify your project ID and setup")
        
        return False

def test_firestore_collections(project_id: str) -> bool:
    """Test Firestore collections access."""
    print("\n🔍 Testing Firestore collections access...")
    
    try:
        from google.cloud import firestore
        
        db = firestore.Client(project=project_id)
        
        # Try to list collections
        collections = list(db.collections())
        print(f"✅ Successfully accessed Firestore collections")
        print(f"   Found {len(collections)} collections")
        
        if collections:
            for collection in collections[:5]:  # Show first 5
                print(f"   - {collection.id}")
            if len(collections) > 5:
                print(f"   ... and {len(collections) - 5} more")
        else:
            print("   No collections found (this is normal for a new database)")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to access Firestore collections: {e}")
        return False

def test_authentication_flow(project_id: str) -> bool:
    """Test the authentication flow similar to what the main app uses."""
    print("\n🔍 Testing authentication flow (similar to main app)...")
    
    try:
        # This mimics the AuthService initialization
        import firebase_admin
        from firebase_admin import auth, credentials
        from google.cloud import firestore
        
        # Initialize Firestore (should already be done, but test independently)
        db = firestore.Client(project=project_id)
        
        print("✅ Authentication components initialized")
        
        # Test creating a mock user document
        test_user_id = "test_user_12345"
        user_ref = db.collection('users').document(test_user_id)
        
        user_data = {
            'uid': test_user_id,
            'email': 'test@example.com',
            'name': 'Test User',
            'created_at': firestore.SERVER_TIMESTAMP,
            'subscription_plan': 'free',
            'google_ads_accounts': []
        }
        
        # Write test user
        user_ref.set(user_data)
        print("✅ Test user document created")
        
        # Read test user back
        user_doc = user_ref.get()
        if user_doc.exists:
            print("✅ Test user document retrieved")
            retrieved_data = user_doc.to_dict()
            print(f"   User ID: {retrieved_data.get('uid')}")
            print(f"   Email: {retrieved_data.get('email')}")
        else:
            print("❌ Test user document not found")
            return False
        
        # Clean up test user
        user_ref.delete()
        print("✅ Test user document cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication flow test failed: {e}")
        return False

def check_environment_variables():
    """Check relevant environment variables."""
    print("\n🔍 Checking environment variables...")
    
    env_vars = {
        'FIREBASE_PROJECT_ID': os.getenv('FIREBASE_PROJECT_ID'),
        'GOOGLE_APPLICATION_CREDENTIALS': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
    }
    
    for var_name, var_value in env_vars.items():
        if var_value:
            if var_name == 'GEMINI_API_KEY':
                # Mask API key for security
                masked_value = var_value[:10] + '...' + var_value[-5:] if len(var_value) > 15 else '***'
                print(f"✅ {var_name}: {masked_value}")
            else:
                print(f"✅ {var_name}: {var_value}")
        else:
            print(f"⚠️ {var_name}: Not set")
    
    return True

def main():
    """Main test function."""
    print("🧪 Firebase Connection Test Script")
    print("==================================")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Track test results
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Package imports
    total_tests += 1
    if test_imports():
        tests_passed += 1
    else:
        print("\n❌ Package import test failed. Cannot continue.")
        return False
    
    # Test 2: Environment variables
    total_tests += 1
    if check_environment_variables():
        tests_passed += 1
    
    # Test 3: Service account file
    total_tests += 1
    file_valid, service_account_data = check_service_account_file()
    if file_valid:
        tests_passed += 1
        project_id = service_account_data['project_id']
    else:
        print("\n❌ Service account file test failed. Cannot continue.")
        return False
    
    # Test 4: Firebase Admin initialization
    total_tests += 1
    if test_firebase_admin_initialization(service_account_data):
        tests_passed += 1
    else:
        print("\n❌ Firebase Admin initialization failed. Cannot continue.")
        return False
    
    # Test 5: Firestore connection
    total_tests += 1
    if test_firestore_connection(project_id):
        tests_passed += 1
    else:
        print("\n❌ Firestore connection test failed.")
        return False
    
    # Test 6: Firestore collections
    total_tests += 1
    if test_firestore_collections(project_id):
        tests_passed += 1
    
    # Test 7: Authentication flow
    total_tests += 1
    if test_authentication_flow(project_id):
        tests_passed += 1
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    print(f"Success rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed! Firebase connection is working correctly.")
        print("\n✅ Your application should now be able to connect to Firebase/Firestore.")
        print("\n🚀 Next steps:")
        print("1. Start your main application: python main.py")
        print("2. Test the health endpoint: curl http://localhost:8000/health")
        print("3. Check authentication: curl http://localhost:8000/api/auth/status")
        return True
    else:
        print(f"\n❌ {total_tests - tests_passed} test(s) failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)