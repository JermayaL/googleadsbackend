"""
Base Infrastructure Agent for ADK Integration
Provides Google Ads and AI services as tools for client agents
"""

from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.tools import tool
from core.gemini_client import GeminiClient
from core.google_ads_client import GoogleAdsClient
from core.auth import AuthService

class BaseInfrastructureAgent:
    """Base class for infrastructure agents that provide services to client agents"""
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.google_ads_client = GoogleAdsClient()
        self.auth_service = AuthService()
    
    @tool
    async def get_user_google_ads_campaigns(
        self, 
        user_context: Dict[str, Any], 
        customer_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Tool: Get Google Ads campaigns for authenticated user"""
        try:
            # Get user's connected accounts
            if not customer_id:
                user_doc = self.auth_service.db.collection('users').document(user_context["user_id"]).get()
                accounts = user_doc.to_dict().get("google_ads_accounts", [])
                if not accounts:
                    return {"error": "No Google Ads accounts connected"}
                customer_id = accounts[0]  # Use first account
            
            # Get access token for this customer
            connection_doc = self.auth_service.db.collection('google_ads_connections').document(customer_id).get()
            if not connection_doc.exists:
                return {"error": "Google Ads account not properly connected"}
            
            access_token = connection_doc.to_dict().get("access_token")
            
            # Fetch campaigns
            campaigns = await self.google_ads_client.get_campaigns(customer_id, access_token)
            return campaigns
            
        except Exception as e:
            return {"error": f"Failed to fetch campaigns: {str(e)}"}
    
    @tool
    async def get_campaign_performance(
        self,
        user_context: Dict[str, Any],
        campaign_id: str,
        customer_id: Optional[str] = None,
        date_range: str = "LAST_30_DAYS"
    ) -> Dict[str, Any]:
        """Tool: Get campaign performance data"""
        try:
            if not customer_id:
                user_doc = self.auth_service.db.collection('users').document(user_context["user_id"]).get()
                accounts = user_doc.to_dict().get("google_ads_accounts", [])
                if not accounts:
                    return {"error": "No Google Ads accounts connected"}
                customer_id = accounts[0]
            
            performance = await self.google_ads_client.get_campaign_performance(
                customer_id, campaign_id, date_range
            )
            return performance
            
        except Exception as e:
            return {"error": f"Failed to fetch performance: {str(e)}"}
    
    @tool
    async def generate_ad_copy_with_ai(
        self,
        user_context: Dict[str, Any],
        product_info: Dict[str, Any],
        target_audience: str,
        campaign_goal: str
    ) -> Dict[str, Any]:
        """Tool: Generate ad copy using Gemini AI"""
        try:
            ad_copy = await self.gemini_client.generate_ad_copy(
                product_info, target_audience, campaign_goal
            )
            return ad_copy
            
        except Exception as e:
            return {"error": f"Failed to generate ad copy: {str(e)}"}
    
    @tool
    async def analyze_campaign_performance_with_ai(
        self,
        user_context: Dict[str, Any],
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Tool: Analyze campaign performance using Gemini AI"""
        try:
            analysis = await self.gemini_client.analyze_performance(performance_data)
            return analysis
            
        except Exception as e:
            return {"error": f"Failed to analyze performance: {str(e)}"}
    
    @tool
    async def create_new_campaign(
        self,
        user_context: Dict[str, Any],
        campaign_data: Dict[str, Any],
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Tool: Create a new Google Ads campaign"""
        try:
            if not customer_id:
                user_doc = self.auth_service.db.collection('users').document(user_context["user_id"]).get()
                accounts = user_doc.to_dict().get("google_ads_accounts", [])
                if not accounts:
                    return {"error": "No Google Ads accounts connected"}
                customer_id = accounts[0]
            
            result = await self.google_ads_client.create_campaign(customer_id, campaign_data)
            return result
            
        except Exception as e:
            return {"error": f"Failed to create campaign: {str(e)}"}

# Create infrastructure agent instance
infrastructure_agent = BaseInfrastructureAgent()

# Export tools for use by client agents
INFRASTRUCTURE_TOOLS = [
    infrastructure_agent.get_user_google_ads_campaigns,
    infrastructure_agent.get_campaign_performance,
    infrastructure_agent.generate_ad_copy_with_ai,
    infrastructure_agent.analyze_campaign_performance_with_ai,
    infrastructure_agent.create_new_campaign
]