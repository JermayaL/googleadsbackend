"""
User management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from core.auth import get_current_user
from services.user_service import UserService

router = APIRouter()

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

@router.get("/profile")
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user profile information"""
    try:
        user_service = UserService()
        profile = await user_service.get_user_profile(current_user["uid"])
        
        # Remove sensitive information
        profile.pop("google_ads_accounts", None)
        
        return profile
        
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch profile: {str(e)}")

@router.put("/profile")
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile"""
    try:
        user_service = UserService()
        updated_profile = await user_service.update_user_profile(
            current_user["uid"], 
            profile_update.dict(exclude_unset=True)
        )
        
        return updated_profile
        
    except Exception as e:
        raise HTTPException(500, f"Failed to update profile: {str(e)}")

@router.get("/usage")
async def get_user_usage_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's API usage statistics"""
    try:
        user_service = UserService()
        stats = await user_service.get_user_usage_stats(current_user["uid"])
        
        return stats
        
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch usage stats: {str(e)}")

@router.delete("/account")
async def delete_user_account(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Delete user account and all associated data"""
    try:
        user_service = UserService()
        
        # Delete all user data
        collections_to_delete = [
            'users',
            'agent_sessions', 
            'usage_stats',
            'custom_agents'
        ]
        
        for collection in collections_to_delete:
            query = user_service.db.collection(collection).where('user_id', '==', current_user["uid"])
            docs = query.stream()
            for doc in docs:
                doc.reference.delete()
        
        # Delete Google Ads connections
        user_profile = await user_service.get_user_profile(current_user["uid"])
        for customer_id in user_profile.get("google_ads_accounts", []):
            connection_ref = user_service.db.collection('google_ads_connections').document(customer_id)
            connection_ref.delete()
        
        return {"status": "account_deleted"}
        
    except Exception as e:
        raise HTTPException(500, f"Failed to delete account: {str(e)}")

@router.get("/subscription")
async def get_subscription_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's subscription information"""
    try:
        user_service = UserService()
        profile = await user_service.get_user_profile(current_user["uid"])
        
        subscription_plan = profile.get("subscription_plan", "free")
        
        plans = {
            "free": {
                "name": "Free",
                "api_calls_limit": 1000,
                "ai_generations_limit": 100,
                "agents_limit": 1,
                "support": "community"
            },
            "pro": {
                "name": "Pro", 
                "api_calls_limit": 10000,
                "ai_generations_limit": 1000,
                "agents_limit": 5,
                "support": "email"
            },
            "enterprise": {
                "name": "Enterprise",
                "api_calls_limit": -1,  # Unlimited
                "ai_generations_limit": -1,
                "agents_limit": -1,
                "support": "priority"
            }
        }
        
        current_plan = plans.get(subscription_plan, plans["free"])
        usage_stats = await user_service.get_user_usage_stats(current_user["uid"])
        
        return {
            "current_plan": current_plan,
            "usage_stats": usage_stats,
            "subscription_status": "active"
        }
        
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch subscription info: {str(e)}")