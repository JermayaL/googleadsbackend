"""
Firebase-specific configuration
"""

import os
from typing import Dict, Any

class FirebaseConfig:
    """Firebase configuration management"""
    
    @staticmethod
    def get_firebase_config() -> Dict[str, Any]:
        """Get Firebase configuration from environment"""
        return {
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
        }
    
    @staticmethod
    def get_firestore_settings() -> Dict[str, Any]:
        """Get Firestore-specific settings"""
        return {
            "collection_names": {
                "users": "users",
                "agent_sessions": "agent_sessions",
                "custom_agents": "custom_agents",
                "google_ads_connections": "google_ads_connections",
                "usage_stats": "usage_stats"
            },
            "security_rules_file": "firestore.rules",
            "indexes_file": "firestore.indexes.json"
        }