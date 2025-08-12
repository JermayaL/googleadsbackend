"""
Firebase setup script
"""

import os
import json
from google.cloud import firestore
from firebase_admin import auth

def setup_firebase_security_rules():
    """Setup Firestore security rules"""
    
    rules = """
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Agent sessions are user-specific
    match /agent_sessions/{sessionId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
    
    // Custom agents are user-specific
    match /custom_agents/{agentId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
    
    // Google Ads connections are user-specific
    match /google_ads_connections/{customerId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
    
    // Usage stats are user-specific
    match /usage_stats/{statId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
    
    // Public collections (read-only)
    match /agent_templates/{templateId} {
      allow read: if true;
      allow write: if false; // Only admins can write
    }
  }
}
"""
    
    print("Firestore security rules:")
    print(rules)
    print("\nApply these rules in the Firebase Console > Firestore > Rules")

def create_firestore_indexes():
    """Create required Firestore indexes"""
    
    indexes = [
        {
            "collectionGroup": "agent_sessions",
            "fields": [
                {"fieldPath": "user_id", "order": "ASCENDING"},
                {"fieldPath": "last_active", "order": "DESCENDING"}
            ]
        },
        {
            "collectionGroup": "usage_stats",
            "fields": [
                {"fieldPath": "user_id", "order": "ASCENDING"},
                {"fieldPath": "date", "order": "DESCENDING"}
            ]
        },
        {
            "collectionGroup": "google_ads_connections",
            "fields": [
                {"fieldPath": "user_id", "order": "ASCENDING"},
                {"fieldPath": "connected_at", "order": "DESCENDING"}
            ]
        }
    ]
    
    print("Required Firestore indexes:")
    for index in indexes:
        print(json.dumps(index, indent=2))
    
    print("\nCreate these indexes in the Firebase Console > Firestore > Indexes")

def setup_firebase_auth():
    """Setup Firebase Authentication"""
    
    print("Firebase Authentication Setup:")
    print("1. Enable Email/Password authentication")
    print("2. Enable Google Sign-In")
    print("3. Add your domain to authorized domains")
    print("4. Configure OAuth consent screen")
    
    # OAuth scopes needed
    scopes = [
        "https://www.googleapis.com/auth/adwords",
        "openid",
        "email", 
        "profile"
    ]
    
    print(f"\nRequired OAuth scopes: {scopes}")

if __name__ == "__main__":
    print("🔥 Firebase Setup Script")
    print("=" * 50)
    
    setup_firebase_security_rules()
    print("\n" + "=" * 50)
    
    create_firestore_indexes()
    print("\n" + "=" * 50)
    
    setup_firebase_auth()
    print("\n✅ Firebase setup complete!")