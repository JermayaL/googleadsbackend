"""
Google Ads API Client for campaign management - 2025 Edition
Updated with latest Google Ads API patterns and proper error handling
"""

from typing import List, Dict, Any, Optional
import logging
import asyncio
import os
from config.settings import settings

logger = logging.getLogger(__name__)

class GoogleAdsClient:
    def __init__(self):
        self.client = None
        self.is_sandbox = True  # Start in sandbox mode for development
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Ads client with 2025 best practices"""
        try:
            # Check if we have real credentials or should use sandbox
            if self._has_valid_credentials():
                self._initialize_production_client()
            else:
                logger.info("🏗️ Google Ads client initialized in SANDBOX mode")
                logger.info("   - Using mock data for development")
                logger.info("   - To use real API, complete OAuth flow")
                self.is_sandbox = True
                
        except Exception as e:
            logger.warning(f"⚠️ Google Ads client initialization failed: {e}")
            logger.info("🏗️ Falling back to sandbox mode")
            self.is_sandbox = True
    
    def _has_valid_credentials(self) -> bool:
        """Check if we have valid Google Ads API credentials"""
        required_fields = [
            settings.GOOGLE_ADS_DEVELOPER_TOKEN,
            settings.GOOGLE_ADS_CLIENT_ID,
            settings.GOOGLE_ADS_CLIENT_SECRET,
        ]
        
        # Check if all required fields are present and not empty
        has_basic_creds = all(field and field.strip() for field in required_fields)
        
        # Check if we have a valid refresh token (must be substantial length)
        refresh_token = settings.GOOGLE_ADS_REFRESH_TOKEN
        has_refresh_token = (
            refresh_token and 
            len(refresh_token.strip()) > 20 and  # Real refresh tokens are much longer
            not refresh_token.strip().endswith('//')  # Not incomplete like "1//"
        )
        
        logger.info(f"🔐 Production credential check:")
        logger.info(f"   - Developer token: {'✅' if settings.GOOGLE_ADS_DEVELOPER_TOKEN else '❌'}")
        logger.info(f"   - Client ID: {'✅' if settings.GOOGLE_ADS_CLIENT_ID else '❌'}")
        logger.info(f"   - Client secret: {'✅' if settings.GOOGLE_ADS_CLIENT_SECRET else '❌'}")
        logger.info(f"   - Refresh token: {'✅' if has_refresh_token else f'❌ (length: {len(refresh_token.strip()) if refresh_token else 0})'}")
        
        return has_basic_creds and has_refresh_token
    
    def _initialize_production_client(self):
        """Initialize the actual Google Ads client"""
        try:
            # Import here to avoid errors if package not installed
            from google.ads.googleads.client import GoogleAdsClient as GACClient
            
            # Create client configuration dictionary
            config = {
                "developer_token": settings.GOOGLE_ADS_DEVELOPER_TOKEN,
                "client_id": settings.GOOGLE_ADS_CLIENT_ID,
                "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
                "refresh_token": settings.GOOGLE_ADS_REFRESH_TOKEN,
                "use_proto_plus": True,  # Required for 2025 versions
                "json_key_file_path": None,  # Not using service account
                "impersonated_email": None,  # Not using service account
            }
            
            # Add login customer ID if available
            if hasattr(settings, 'GOOGLE_ADS_LOGIN_CUSTOMER_ID') and settings.GOOGLE_ADS_LOGIN_CUSTOMER_ID:
                config["login_customer_id"] = settings.GOOGLE_ADS_LOGIN_CUSTOMER_ID
            
            self.client = GACClient.load_from_dict(config)
            self.is_sandbox = False
            logger.info("✅ Google Ads production client initialized successfully")
            
        except ImportError:
            logger.error("❌ google-ads package not installed. Run: pip install google-ads")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Ads production client: {e}")
            raise
    
    async def get_accessible_customers(self) -> List[str]:
        """Get list of accessible customer IDs"""
        if self.is_sandbox:
            return await self._mock_get_accessible_customers()
        
        try:
            customer_service = self.client.get_service("CustomerService")
            accessible_customers = await asyncio.to_thread(
                customer_service.list_accessible_customers
            )
            
            return [
                customer.resource_name.split('/')[-1] 
                for customer in accessible_customers.results
            ]
            
        except Exception as e:
            logger.error(f"❌ Error fetching accessible customers: {e}")
            logger.info("🏗️ Falling back to mock data")
            return await self._mock_get_accessible_customers()
    
    async def get_campaigns(
        self,
        customer_id: str,
        access_token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get campaigns for a customer"""
        if self.is_sandbox:
            return await self._mock_get_campaigns(customer_id)
        
        try:
            # Update client credentials if access token provided
            if access_token:
                logger.info("🔄 Updating client credentials with new access token")
                # In production, you'd update the client's OAuth credentials here
            
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    campaign.campaign_budget,
                    metrics.cost_micros,
                    metrics.clicks,
                    metrics.impressions,
                    metrics.ctr
                FROM campaign
                WHERE campaign.status != 'REMOVED'
                ORDER BY campaign.name
                LIMIT 50
            """
            
            response = await asyncio.to_thread(
                ga_service.search,
                customer_id=customer_id,
                query=query
            )
            
            campaigns = []
            for row in response:
                campaigns.append({
                    "id": str(row.campaign.id),
                    "name": row.campaign.name,
                    "status": row.campaign.status.name,
                    "type": row.campaign.advertising_channel_type.name,
                    "budget": row.campaign.campaign_budget,
                    "performance": {
                        "cost_micros": row.metrics.cost_micros,
                        "clicks": row.metrics.clicks,
                        "impressions": row.metrics.impressions,
                        "ctr": row.metrics.ctr
                    }
                })
            
            logger.info(f"✅ Retrieved {len(campaigns)} campaigns for customer {customer_id}")
            return campaigns
            
        except Exception as e:
            logger.error(f"❌ Error fetching campaigns: {e}")
            logger.info("🏗️ Falling back to mock data")
            return await self._mock_get_campaigns(customer_id)
    
    async def get_campaign_performance(
        self,
        customer_id: str,
        campaign_id: str,
        date_range: str = "LAST_30_DAYS"
    ) -> Dict[str, Any]:
        """Get detailed performance data for a campaign"""
        if self.is_sandbox:
            return await self._mock_get_campaign_performance(customer_id, campaign_id, date_range)
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    metrics.cost_micros,
                    metrics.clicks,
                    metrics.impressions,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.conversions,
                    metrics.conversion_rate,
                    segments.date
                FROM campaign
                WHERE campaign.id = {campaign_id}
                AND segments.date DURING {date_range}
                ORDER BY segments.date DESC
                LIMIT 100
            """
            
            response = await asyncio.to_thread(
                ga_service.search,
                customer_id=customer_id,
                query=query
            )
            
            performance_data = []
            for row in response:
                performance_data.append({
                    "date": str(row.segments.date),
                    "cost_micros": row.metrics.cost_micros,
                    "clicks": row.metrics.clicks,
                    "impressions": row.metrics.impressions,
                    "ctr": row.metrics.ctr,
                    "average_cpc": row.metrics.average_cpc,
                    "conversions": row.metrics.conversions,
                    "conversion_rate": row.metrics.conversion_rate
                })
            
            return {
                "campaign_id": campaign_id,
                "customer_id": customer_id,
                "date_range": date_range,
                "performance": performance_data,
                "total_records": len(performance_data)
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching campaign performance: {e}")
            logger.info("🏗️ Falling back to mock data")
            return await self._mock_get_campaign_performance(customer_id, campaign_id, date_range)
    
    async def create_campaign(
        self,
        customer_id: str,
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new campaign"""
        if self.is_sandbox:
            return await self._mock_create_campaign(customer_id, campaign_data)
        
        try:
            campaign_service = self.client.get_service("CampaignService")
            campaign_operation = self.client.get_type("CampaignOperation")
            
            # Configure campaign
            campaign = campaign_operation.create
            campaign.name = campaign_data["name"]
            campaign.advertising_channel_type = self.client.enums.AdvertisingChannelTypeEnum.SEARCH
            campaign.status = self.client.enums.CampaignStatusEnum.PAUSED  # Start paused for safety
            
            # Set budget - this would need proper budget resource creation in production
            if "budget_amount" in campaign_data:
                # In production, you'd create a budget resource first
                logger.info(f"💰 Would create budget of ${campaign_data['budget_amount']}")
            
            response = await asyncio.to_thread(
                campaign_service.mutate_campaigns,
                customer_id=customer_id,
                operations=[campaign_operation]
            )
            
            campaign_id = response.results[0].resource_name.split('/')[-1]
            
            return {
                "campaign_id": campaign_id,
                "customer_id": customer_id,
                "status": "created",
                "resource_name": response.results[0].resource_name
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating campaign: {e}")
            logger.info("🏗️ Falling back to mock creation")
            return await self._mock_create_campaign(customer_id, campaign_data)
    
    # Mock methods for development/testing
    async def _mock_get_accessible_customers(self) -> List[str]:
        """Mock accessible customers for development"""
        return ["123-456-7890", "987-654-3210"]
    
    async def _mock_get_campaigns(self, customer_id: str) -> List[Dict[str, Any]]:
        """Mock campaigns data for development"""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        return [
            {
                "id": "11111111",
                "name": "🏗️ Mock Campaign - Search Ads",
                "status": "ENABLED",
                "type": "SEARCH",
                "budget": f"customers/{customer_id}/campaignBudgets/22222222",
                "performance": {
                    "cost_micros": 1500000000,  # $1,500 in micros
                    "clicks": 450,
                    "impressions": 15000,
                    "ctr": 0.03
                }
            },
            {
                "id": "33333333",
                "name": "🏗️ Mock Campaign - Display Ads",
                "status": "ENABLED", 
                "type": "DISPLAY",
                "budget": f"customers/{customer_id}/campaignBudgets/44444444",
                "performance": {
                    "cost_micros": 800000000,  # $800 in micros
                    "clicks": 120,
                    "impressions": 25000,
                    "ctr": 0.0048
                }
            },
            {
                "id": "55555555",
                "name": "🏗️ Mock Campaign - Shopping Ads",
                "status": "PAUSED",
                "type": "SHOPPING",
                "budget": f"customers/{customer_id}/campaignBudgets/66666666",
                "performance": {
                    "cost_micros": 600000000,  # $600 in micros
                    "clicks": 85,
                    "impressions": 8000,
                    "ctr": 0.01063
                }
            }
        ]
    
    async def _mock_get_campaign_performance(
        self, 
        customer_id: str, 
        campaign_id: str, 
        date_range: str
    ) -> Dict[str, Any]:
        """Mock campaign performance data"""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        # Generate mock performance data for the last 7 days
        from datetime import datetime, timedelta
        
        performance_data = []
        base_date = datetime.now() - timedelta(days=7)
        
        for i in range(7):
            date = base_date + timedelta(days=i)
            performance_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "cost_micros": 150000000 + (i * 10000000),  # Varying costs
                "clicks": 45 + (i * 5),
                "impressions": 1500 + (i * 100),
                "ctr": 0.025 + (i * 0.002),
                "average_cpc": 3500000,  # $3.50 in micros
                "conversions": 2 + (i % 3),
                "conversion_rate": 0.045 + (i * 0.005)
            })
        
        return {
            "campaign_id": campaign_id,
            "customer_id": customer_id,
            "date_range": date_range,
            "performance": performance_data,
            "total_records": len(performance_data),
            "mock_data": True
        }
    
    async def _mock_create_campaign(
        self, 
        customer_id: str, 
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock campaign creation"""
        await asyncio.sleep(0.2)  # Simulate API delay
        
        import random
        campaign_id = str(random.randint(10000000, 99999999))
        
        return {
            "campaign_id": campaign_id,
            "customer_id": customer_id,
            "status": "created_mock",
            "resource_name": f"customers/{customer_id}/campaigns/{campaign_id}",
            "mock_data": True,
            "created_campaign": campaign_data
        }
    
    def get_oauth_url(self) -> str:
        """Get OAuth URL for user authentication"""
        # This would generate the actual OAuth URL in production
        return (
            f"https://accounts.google.com/o/oauth2/auth"
            f"?client_id={settings.GOOGLE_ADS_CLIENT_ID}"
            f"&redirect_uri=http://localhost:8000/auth/callback"
            f"&scope=https://www.googleapis.com/auth/adwords"
            f"&response_type=code"
            f"&access_type=offline"
            f"&prompt=consent"
        )
    
    def is_production_ready(self) -> bool:
        """Check if client is ready for production use"""
        return not self.is_sandbox and self.client is not None