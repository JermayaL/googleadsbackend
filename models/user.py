"""
User data models and schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Dict, Any, List, Optional
from datetime import datetime

class User(BaseModel):
    uid: str
    email: EmailStr
    email_verified: bool = False
    name: Optional[str] = None
    picture: Optional[str] = None
    created_at: datetime
    last_login: datetime
    subscription_plan: str = "free"
    usage_stats: Dict[str, Any] = {}
    google_ads_accounts: List[str] = []
    preferences: Dict[str, Any] = {}

class GoogleAdsConnection(BaseModel):
    customer_id: str
    user_id: str
    access_token: str  # Should be encrypted in production
    refresh_token: str  # Should be encrypted in production
    connected_at: datetime
    account_name: Optional[str] = None
    currency: Optional[str] = None
    time_zone: Optional[str] = None
    status: str = "active"

class UserSession(BaseModel):
    session_id: str
    user_id: str
    agent_id: Optional[str] = None
    selected_account_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {}
    created_at: datetime
    expires_at: datetime
    last_active: datetime

class UsageStats(BaseModel):
    user_id: str
    date: str  # YYYY-MM-DD format
    api_calls: int = 0
    ai_generations: int = 0
    campaigns_analyzed: int = 0
    agents_created: int = 0
    created_at: datetime