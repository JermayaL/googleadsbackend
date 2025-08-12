"""
Firebase Authentication Service - FIXED FOR 2025 FIRESTORE API
Updated with proper timestamp handling based on 2025 API documentation
"""

import firebase_admin
from firebase_admin import auth, credentials
from google.cloud import firestore
from fastapi import HTTPException, Depends, Header
from typing import Optional, Dict, Any
from config.settings import settings
import datetime

class AuthService:
    def __init__(self):
        self.app = None
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK using 2025 best practices"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
                self.app = firebase_admin.initialize_app(cred, {
                    'projectId': settings.FIREBASE_PROJECT_ID
                })
            else:
                self.app = firebase_admin.get_app()
            
            # Initialize Firestore client - Updated for 2025
            self.db = firestore.Client(project=settings.FIREBASE_PROJECT_ID)
            print("✅ Firebase initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Firebase: {e}")
            raise
    
    async def verify_firebase_token(self, id_token: str) -> Dict[str, Any]:
        """Verify Firebase ID token"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return {
                "uid": decoded_token["uid"],
                "email": decoded_token.get("email"),
                "email_verified": decoded_token.get("email_verified", False),
                "name": decoded_token.get("name"),
                "picture": decoded_token.get("picture")
            }
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid Firebase token: {str(e)}"
            )
    
    async def get_or_create_user(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get existing user or create new one - FIXED for 2025 API"""
        try:
            user_ref = self.db.collection('users').document(user_info["uid"])
            user_doc = user_ref.get()
            
            # FIXED: Use datetime.datetime.now() for all timestamps
            current_time = datetime.datetime.now()
            
            if user_doc.exists:
                # Update last login using current datetime
                user_ref.update({
                    "last_login": current_time  # FIXED: Use datetime object
                })
                user_data = user_doc.to_dict()
            else:
                # Create new user with current datetime for all timestamps
                user_data = {
                    "uid": user_info["uid"],
                    "email": user_info["email"],
                    "email_verified": user_info.get("email_verified", False),
                    "name": user_info.get("name", ""),
                    "picture": user_info.get("picture", ""),
                    "created_at": current_time,  # FIXED: Use datetime object
                    "last_login": current_time,  # FIXED: Use datetime object
                    "subscription_plan": "free",
                    "usage_stats": {},
                    "google_ads_accounts": []
                }
                user_ref.set(user_data)
            
            return user_data
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error managing user: {str(e)}"
            )
    
    async def store_google_ads_connection(
        self,
        user_id: str,
        customer_id: str,
        access_token: str,
        refresh_token: str
    ) -> Dict[str, Any]:
        """Store Google Ads account connection - FIXED for 2025 API"""
        try:
            # FIXED: Use datetime.datetime.now() for timestamp
            current_time = datetime.datetime.now()
            
            connection_data = {
                "customer_id": customer_id,
                "access_token": access_token,  # In production, encrypt this
                "refresh_token": refresh_token,  # In production, encrypt this
                "connected_at": current_time,  # FIXED: Use datetime object
                "user_id": user_id
            }
            
            # Store connection
            connection_ref = self.db.collection('google_ads_connections').document(customer_id)
            connection_ref.set(connection_data)
            
            # Update user's connected accounts using array union
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                "google_ads_accounts": firestore.ArrayUnion([customer_id])
            })
            
            return {"status": "connected", "customer_id": customer_id}
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error storing Google Ads connection: {str(e)}"
            )
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            return user_doc.to_dict() if user_doc.exists else None
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting user: {str(e)}"
            )
    
    async def update_user_last_active(self, user_id: str) -> None:
        """Update user's last active timestamp - FIXED for 2025 API"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                "last_active": datetime.datetime.now()  # FIXED: Use datetime object
            })
        except Exception as e:
            # Don't raise error for this non-critical operation
            print(f"Warning: Failed to update last active for user {user_id}: {e}")

# Dependency for getting current user
async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Get current authenticated user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    
    # Get auth service instance
    auth_service = AuthService()
    user_info = await auth_service.verify_firebase_token(token)
    user_data = await auth_service.get_or_create_user(user_info)
    
    # Update last active (non-blocking)
    try:
        await auth_service.update_user_last_active(user_data["uid"])
    except Exception:
        pass  # Don't fail the request if this fails
    
    return user_data

# Alternative dependency for optional authentication
async def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Get current authenticated user (optional - returns None if not authenticated)"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None