"""
Authentication service - separate from core auth - FIXED FOR 2025 FIRESTORE API
Updated with proper timestamp handling based on 2025 API documentation
"""

from typing import Dict, Any, Optional
from core.auth import AuthService as CoreAuthService
from core.database import FirestoreDB
from fastapi import HTTPException
import datetime

class AuthService:
    """High-level authentication service"""
    
    def __init__(self):
        self.core_auth = CoreAuthService()
        self.db = FirestoreDB()
    
    async def authenticate_extension_user(
        self, 
        google_token: str, 
        user_info: Dict[str, Any], 
        extension_id: str
    ) -> Dict[str, Any]:
        """Authenticate user from Chrome extension - FIXED for 2025 API"""
        try:
            # Verify token and get/create user
            verified_user = await self.core_auth.verify_firebase_token(google_token)
            user_data = await self.core_auth.get_or_create_user(verified_user)
            
            # FIXED: Use datetime.datetime.now() for timestamps
            current_time = datetime.datetime.now()
            
            # Create extension session
            session_data = {
                "user_id": user_data["uid"],
                "extension_id": extension_id,
                "created_at": current_time,  # FIXED: Use datetime object
                "last_active": current_time   # FIXED: Use datetime object
            }
            
            session_id = await self.db.create_document(
                "extension_sessions", 
                f"{user_data['uid']}_{extension_id}", 
                session_data
            )
            
            # Get user's Google Ads accounts
            accounts = user_data.get("google_ads_accounts", [])
            
            return {
                "session_id": session_id,
                "user": user_data,
                "google_ads_accounts": accounts,
                "status": "authenticated"
            }
            
        except Exception as e:
            raise HTTPException(401, f"Extension authentication failed: {str(e)}")
    
    async def refresh_user_session(self, user_id: str, extension_id: str) -> Dict[str, Any]:
        """Refresh user session - FIXED for 2025 API"""
        try:
            session_doc = await self.db.get_document(
                "extension_sessions", 
                f"{user_id}_{extension_id}"
            )
            
            if not session_doc:
                raise HTTPException(404, "Session not found")
            
            # FIXED: Update last active with datetime object
            await self.db.update_document(
                "extension_sessions",
                f"{user_id}_{extension_id}",
                {"last_active": datetime.datetime.now()}  # FIXED: Use datetime object
            )
            
            return {"status": "session_refreshed"}
            
        except Exception as e:
            raise HTTPException(500, f"Failed to refresh session: {str(e)}")
    
    async def validate_api_access(self, user_id: str, endpoint: str) -> bool:
        """Validate user's access to specific API endpoint"""
        try:
            user_doc = await self.db.get_document("users", user_id)
            if not user_doc:
                return False
            
            subscription_plan = user_doc.get("subscription_plan", "free")
            
            # Define access rules
            access_rules = {
                "free": [
                    "/ai/generate-ad-copy",
                    "/google-ads/campaigns",
                    "/agents/available"
                ],
                "pro": [
                    "/ai/*",
                    "/google-ads/*",
                    "/agents/*",
                    "/data/export"
                ],
                "enterprise": ["*"]  # Full access
            }
            
            allowed_endpoints = access_rules.get(subscription_plan, [])
            
            if "*" in allowed_endpoints:
                return True
            
            for allowed in allowed_endpoints:
                if allowed.endswith("*"):
                    if endpoint.startswith(allowed[:-1]):
                        return True
                elif endpoint == allowed:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error validating API access: {e}")
            return False