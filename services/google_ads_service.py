"""
Google Ads service - high-level business logic
"""

from typing import Dict, Any, List, Optional
from core.google_ads_client import GoogleAdsClient
from core.database import FirestoreDB
from fastapi import HTTPException
import asyncio

class GoogleAdsService:
    """High-level Google Ads service"""
    
    def __init__(self):
        self.ads_client = GoogleAdsClient()
        self.db = FirestoreDB()
    
    async def get_user_campaigns_with_insights(
        self, 
        user_id: str, 
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get campaigns with AI-generated insights"""
        try:
            # Get user's access token
            if not customer_id:
                user_doc = await self.db.get_document("users", user_id)
                accounts = user_doc.get("google_ads_accounts", [])
                if not accounts:
                    raise HTTPException(404, "No Google Ads accounts connected")
                customer_id = accounts[0]
            
            connection_doc = await self.db.get_document("google_ads_connections", customer_id)
            if not connection_doc:
                raise HTTPException(404, "Google Ads account not properly connected")
            
            access_token = connection_doc.get("access_token")
            
            # Get campaigns
            campaigns = await self.ads_client.get_campaigns(customer_id, access_token)
            
            # Add insights to each campaign
            enhanced_campaigns = []
            for campaign in campaigns:
                # Get performance data
                performance = await self.ads_client.get_campaign_performance(
                    customer_id, 
                    campaign["id"]
                )
                
                # Add insights (simplified - would use AI in real implementation)
                insights = await self._generate_campaign_insights(campaign, performance)
                
                enhanced_campaigns.append({
                    **campaign,
                    "performance": performance,
                    "insights": insights
                })
            
            return {
                "campaigns": enhanced_campaigns,
                "customer_id": customer_id,
                "total_campaigns": len(enhanced_campaigns)
            }
            
        except Exception as e:
            raise HTTPException(500, f"Failed to fetch campaigns with insights: {str(e)}")
    
    async def _generate_campaign_insights(
        self, 
        campaign: Dict[str, Any], 
        performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI insights for a campaign"""
        # Simplified insights - in real implementation, this would use Gemini AI
        
        insights = {
            "status": "healthy",
            "recommendations": [],
            "alerts": [],
            "opportunities": []
        }
        
        # Analyze performance metrics
        if performance and "performance" in performance:
            perf_data = performance["performance"]
            
            if perf_data:
                avg_ctr = sum(p.get("ctr", 0) for p in perf_data) / len(perf_data) if perf_data else 0
                
                if avg_ctr < 0.02:  # CTR below 2%
                    insights["recommendations"].append("Consider refreshing ad copy to improve CTR")
                    insights["status"] = "needs_attention"
                
                if avg_ctr > 0.05:  # CTR above 5%
                    insights["opportunities"].append("High CTR - consider increasing budget")
        
        return insights
    
    async def create_campaign_with_ai(
        self, 
        user_id: str, 
        campaign_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create campaign with AI-generated content"""
        try:
            # Get user's customer ID
            user_doc = await self.db.get_document("users", user_id)
            accounts = user_doc.get("google_ads_accounts", [])
            if not accounts:
                raise HTTPException(404, "No Google Ads accounts connected")
            
            customer_id = campaign_request.get("customer_id", accounts[0])
            
            # Generate AI content first
            from services.gemini_service import GeminiService
            gemini_service = GeminiService()
            
            # Generate campaign components
            campaign_name = await gemini_service.generate_campaign_name(
                campaign_request.get("product_info", {}),
                campaign_request.get("target_audience", "")
            )
            
            keywords = await gemini_service.generate_keywords(
                campaign_request.get("product_info", {}),
                campaign_request.get("target_audience", "")
            )
            
            ad_copy = await gemini_service.generate_ad_copy(
                campaign_request.get("product_info", {}),
                campaign_request.get("target_audience", ""),
                campaign_request.get("campaign_goal", "")
            )
            
            # Create campaign data
            campaign_data = {
                "name": campaign_name,
                "budget_amount": campaign_request.get("budget_amount", 100.0),
                "keywords": keywords,
                "ad_copy": ad_copy,
                "target_locations": campaign_request.get("target_locations", [])
            }
            
            # Create campaign via Google Ads API
            result = await self.ads_client.create_campaign(customer_id, campaign_data)
            
            # Store campaign creation record
            creation_record = {
                "user_id": user_id,
                "customer_id": customer_id,
                "campaign_id": result.get("campaign_id"),
                "ai_generated_content": {
                    "name": campaign_name,
                    "keywords": keywords,
                    "ad_copy": ad_copy
                },
                "created_at": self.db.client.SERVER_TIMESTAMP
            }
            
            await self.db.create_document(
                "campaign_creations",
                f"{user_id}_{result.get('campaign_id')}",
                creation_record
            )
            
            return {
                **result,
                "ai_generated_content": {
                    "name": campaign_name,
                    "keywords": keywords,
                    "ad_copy": ad_copy
                }
            }
            
        except Exception as e:
            raise HTTPException(500, f"Failed to create AI-powered campaign: {str(e)}")
    
    async def optimize_campaign_with_ai(
        self, 
        user_id: str, 
        campaign_id: str,
        optimization_goals: List[str]
    ) -> Dict[str, Any]:
        """Optimize existing campaign using AI recommendations"""
        try:
            # Get campaign performance data
            user_doc = await self.db.get_document("users", user_id)
            accounts = user_doc.get("google_ads_accounts", [])
            if not accounts:
                raise HTTPException(404, "No Google Ads accounts connected")
            
            customer_id = accounts[0]  # Use first account for now
            
            performance = await self.ads_client.get_campaign_performance(
                customer_id, 
                campaign_id
            )
            
            # Generate AI optimization recommendations
            from services.gemini_service import GeminiService
            gemini_service = GeminiService()
            
            optimizations = await gemini_service.generate_optimization_recommendations(
                performance,
                optimization_goals
            )
            
            # Store optimization record
            optimization_record = {
                "user_id": user_id,
                "campaign_id": campaign_id,
                "customer_id": customer_id,
                "optimization_goals": optimization_goals,
                "ai_recommendations": optimizations,
                "created_at": self.db.client.SERVER_TIMESTAMP,
                "status": "generated"
            }
            
            await self.db.create_document(
                "campaign_optimizations",
                f"{user_id}_{campaign_id}_{int(asyncio.get_event_loop().time())}",
                optimization_record
            )
            
            return {
                "campaign_id": campaign_id,
                "optimizations": optimizations,
                "status": "recommendations_generated"
            }
            
        except Exception as e:
            raise HTTPException(500, f"Failed to optimize campaign: {str(e)}")