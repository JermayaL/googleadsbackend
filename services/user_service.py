"""
User management service - FIXED FOR 2025 FIRESTORE API
Updated with proper timestamp handling based on 2025 API documentation
"""

from typing import Dict, Any, List, Optional
from google.cloud import firestore
from core.auth import AuthService
from fastapi import HTTPException
import datetime

class UserService:
    def __init__(self):
        self.auth_service = AuthService()
        self.db = self.auth_service.db
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                raise HTTPException(404, "User not found")
            
            return user_doc.to_dict()
            
        except Exception as e:
            raise HTTPException(500, f"Error fetching user profile: {str(e)}")
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile - FIXED for 2025 API"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            
            # Only allow certain fields to be updated
            allowed_fields = ['name', 'company', 'phone', 'preferences']
            update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
            
            # FIXED: Use datetime.datetime.now() instead of SERVER_TIMESTAMP
            update_data['updated_at'] = datetime.datetime.now()
            
            user_ref.update(update_data)
            
            # Return updated profile
            return await self.get_user_profile(user_id)
            
        except Exception as e:
            raise HTTPException(500, f"Error updating user profile: {str(e)}")
    
    async def get_user_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's API usage statistics"""
        try:
            # Get usage from the last 30 days
            usage_ref = self.db.collection('usage_stats').where('user_id', '==', user_id)
            usage_docs = usage_ref.stream()
            
            stats = {
                'api_calls': 0,
                'ai_generations': 0,
                'campaigns_analyzed': 0,
                'agents_created': 0
            }
            
            for doc in usage_docs:
                doc_data = doc.to_dict()
                for key in stats:
                    stats[key] += doc_data.get(key, 0)
            
            return stats
            
        except Exception as e:
            raise HTTPException(500, f"Error fetching usage stats: {str(e)}")
    
    async def increment_usage(self, user_id: str, usage_type: str, amount: int = 1):
        """Increment usage counter for user - FIXED for 2025 API"""
        try:
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            
            usage_ref = self.db.collection('usage_stats').document(f"{user_id}_{today}")
            
            # Use transaction to safely increment
            @firestore.transactional
            def update_usage(transaction, doc_ref):
                doc = doc_ref.get(transaction=transaction)
                
                if doc.exists:
                    current_value = doc.to_dict().get(usage_type, 0)
                    transaction.update(doc_ref, {usage_type: current_value + amount})
                else:
                    # FIXED: Use datetime.datetime.now() for timestamps
                    data = {
                        'user_id': user_id,
                        'date': today,
                        usage_type: amount,
                        'created_at': datetime.now()  # FIXED: Use datetime object
                    }
                    transaction.set(doc_ref, data)
            
            transaction = self.db.transaction()
            update_usage(transaction, usage_ref)
            
        except Exception as e:
            print(f"Error incrementing usage: {e}")