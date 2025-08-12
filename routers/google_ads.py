"""
Fixed Google Ads API Router - Proper Error Handling
"""

import os
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class CampaignCreateRequest(BaseModel):
    name: str
    budget_amount: float
    target_locations: List[str] = []
    keywords: List[str] = []
    customer_id: Optional[str] = None

@router.get("/accounts")
async def get_user_google_ads_accounts(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's connected Google Ads accounts with proper error handling."""
    try:
        # Check if Google Ads client is available
        if not hasattr(request.app.state, 'google_ads_client') or not request.app.state.google_ads_client:
            return {
                "accounts": [],
                "total_count": 0,
                "is_production_ready": False,
                "error": "Google Ads client not initialized",
                "troubleshooting": [
                    "Google Ads client failed to initialize during startup",
                    "Check application logs for initialization errors",
                    "Verify Google Ads API credentials if using production mode"
                ]
            }
        
        google_ads_client = request.app.state.google_ads_client
        
        # Check if client is production ready
        if not google_ads_client.is_production_ready():
            # Return sandbox/demo accounts
            demo_accounts = [
                {
                    "customer_id": "123-456-7890",
                    "account_name": "Demo Account - Search Campaigns",
                    "status": "demo",
                    "connection_type": "sandbox",
                    "is_production": False,
                    "connected_at": "2025-01-16T12:00:00Z",
                    "currency_code": "USD",
                    "demo_data": True
                },
                {
                    "customer_id": "987-654-3210", 
                    "account_name": "Demo Account - Display Campaigns",
                    "status": "demo",
                    "connection_type": "sandbox",
                    "is_production": False,
                    "connected_at": "2025-01-16T12:00:00Z",
                    "currency_code": "USD",
                    "demo_data": True
                }
            ]
            
            return {
                "accounts": demo_accounts,
                "total_count": len(demo_accounts),
                "is_production_ready": False,
                "is_sandbox": True,
                "message": "Using demo accounts - production credentials not configured",
                "setup_guide": {
                    "step_1": "Get Google Ads developer token",
                    "step_2": "Create OAuth2 credentials", 
                    "step_3": "Generate refresh token",
                    "step_4": "Update environment variables",
                    "documentation": "/api/google-ads/setup-guide"
                }
            }
        
        # Production mode - try to get real accounts
        try:
            accessible_customers = await google_ads_client.get_accessible_customers()
            logger.info(f"📋 Found {len(accessible_customers)} accessible customers")
            
            accounts = []
            for customer_id in accessible_customers:
                accounts.append({
                    "customer_id": customer_id,
                    "account_name": f"Google Ads Account {customer_id}",
                    "status": "active",
                    "connection_type": "google_ads_api",
                    "is_production": True,
                    "connected_at": "api_discovery",
                    "currency_code": "USD"
                })
            
            return {
                "accounts": accounts,
                "total_count": len(accounts),
                "is_production_ready": True,
                "api_status": "connected"
            }
            
        except Exception as api_error:
            logger.error(f"❌ Google Ads API error: {api_error}")
            
            return {
                "accounts": [],
                "total_count": 0,
                "is_production_ready": False,
                "api_error": str(api_error),
                "troubleshooting": [
                    "Check if developer token is approved",
                    "Verify refresh token is valid and not expired",
                    "Ensure API credentials have proper permissions",
                    "Check Google Ads API quota and billing"
                ]
            }
        
    except Exception as e:
        logger.error(f"❌ Error fetching accounts: {e}")
        raise HTTPException(500, f"Failed to fetch Google Ads accounts: {str(e)}")

@router.get("/campaigns")
async def get_campaigns(
    request: Request,
    customer_id: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get campaigns with proper error handling."""
    try:
        # Check if Google Ads client is available
        if not hasattr(request.app.state, 'google_ads_client') or not request.app.state.google_ads_client:
            raise HTTPException(503, "Google Ads client not available")
        
        google_ads_client = request.app.state.google_ads_client
        
        # Use default customer ID if not provided
        if not customer_id:
            customer_id = "123-456-7890"  # Default demo account
        
        campaigns = await google_ads_client.get_campaigns(customer_id)
        
        return {
            "campaigns": campaigns,
            "customer_id": customer_id,
            "total_count": len(campaigns),
            "is_production": google_ads_client.is_production_ready(),
            "data_source": "google_ads_api" if google_ads_client.is_production_ready() else "mock_data"
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching campaigns: {e}")
        raise HTTPException(500, f"Failed to fetch campaigns: {str(e)}")

@router.get("/auth/status")
async def get_google_ads_auth_status(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get Google Ads authentication status with proper error handling."""
    try:
        # Check if Google Ads client exists
        if not hasattr(request.app.state, 'google_ads_client') or not request.app.state.google_ads_client:
            return {
                "is_production_ready": False,
                "has_valid_credentials": False,
                "is_sandbox_mode": True,
                "error": "Google Ads client not initialized",
                "status": "unavailable"
            }
        
        google_ads_client = request.app.state.google_ads_client
        
        status = {
            "is_production_ready": google_ads_client.is_production_ready(),
            "has_valid_credentials": google_ads_client._has_valid_credentials(),
            "is_sandbox_mode": google_ads_client.is_sandbox,
            "status": "configured" if google_ads_client.is_production_ready() else "sandbox"
        }
        
        if google_ads_client.is_production_ready():
            # Test API connection
            try:
                accessible_customers = await google_ads_client.get_accessible_customers()
                status.update({
                    "api_connection": "working",
                    "accessible_customers_count": len(accessible_customers),
                    "last_api_test": "successful"
                })
            except Exception as e:
                status.update({
                    "api_connection": "failed",
                    "api_error": str(e),
                    "last_api_test": "failed"
                })
        else:
            status.update({
                "oauth_url": google_ads_client.get_oauth_url(),
                "setup_required": True,
                "missing_components": []
            })
            
            # Check what's missing
            if not os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'):
                status["missing_components"].append("Developer Token")
            if not os.getenv('GOOGLE_ADS_CLIENT_ID'):
                status["missing_components"].append("OAuth Client ID")
            if not os.getenv('GOOGLE_ADS_CLIENT_SECRET'):
                status["missing_components"].append("OAuth Client Secret")
            if not os.getenv('GOOGLE_ADS_REFRESH_TOKEN') or len(os.getenv('GOOGLE_ADS_REFRESH_TOKEN', '').strip()) < 10:
                status["missing_components"].append("Valid Refresh Token")
        
        return status
        
    except Exception as e:
        logger.error(f"❌ Error checking auth status: {e}")
        return {
            "is_production_ready": False,
            "has_valid_credentials": False,
            "is_sandbox_mode": True,
            "error": str(e),
            "status": "error"
        }

@router.get("/setup-guide")
async def get_production_setup_guide():
    """Get production setup guide for Google Ads API."""
    return {
        "title": "Google Ads API Production Setup Guide",
        "current_environment": "Development/Sandbox",
        "overview": "To connect real Google Ads accounts, you need to complete the OAuth flow and get production credentials.",
        "prerequisites": [
            "Google Ads Manager Account with campaigns",
            "Google Cloud Project with APIs enabled",
            "Approved Google Ads developer token"
        ],
        "steps": [
            {
                "step": 1,
                "title": "Get Developer Token",
                "description": "Apply for and get approved developer token",
                "url": "https://developers.google.com/google-ads/api/docs/get-started/dev-token",
                "status": "✅ Configured" if os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN') else "❌ Missing",
                "notes": "This can take several business days for approval"
            },
            {
                "step": 2,
                "title": "Create OAuth2 Credentials",
                "description": "Set up OAuth2 client in Google Cloud Console",
                "url": "https://console.cloud.google.com/apis/credentials",
                "status": "✅ Configured" if os.getenv('GOOGLE_ADS_CLIENT_ID') else "❌ Missing",
                "notes": "Use 'Web application' type with redirect URI"
            },
            {
                "step": 3,
                "title": "Generate Refresh Token",
                "description": "Complete OAuth flow to get refresh token",
                "url": "https://developers.google.com/oauthplayground/",
                "status": "✅ Configured" if (os.getenv('GOOGLE_ADS_REFRESH_TOKEN') and len(os.getenv('GOOGLE_ADS_REFRESH_TOKEN', '').strip()) > 10) else "❌ Missing/Invalid",
                "notes": "Use scope: https://www.googleapis.com/auth/adwords"
            },
            {
                "step": 4,
                "title": "Update Environment Variables",
                "description": "Add credentials to .env file",
                "variables": {
                    "GOOGLE_ADS_DEVELOPER_TOKEN": "Your approved developer token",
                    "GOOGLE_ADS_CLIENT_ID": "OAuth2 client ID",
                    "GOOGLE_ADS_CLIENT_SECRET": "OAuth2 client secret",
                    "GOOGLE_ADS_REFRESH_TOKEN": "OAuth2 refresh token"
                }
            },
            {
                "step": 5,
                "title": "Test Connection",
                "description": "Restart app and verify connection",
                "endpoint": "/api/google-ads/auth/status",
                "expected_result": "is_production_ready: true"
            }
        ],
        "current_status": {
            "mode": "sandbox/demo",
            "features_available": [
                "Demo campaign data",
                "AI optimization recommendations", 
                "Interface testing",
                "Agent conversations"
            ],
            "limitations": [
                "No real campaign data",
                "Cannot make actual changes",
                "Limited to demo accounts"
            ]
        },
        "troubleshooting": [
            "Ensure developer token status is 'Approved', not 'Pending'",
            "Verify OAuth2 credentials are for 'Web application' type",
            "Check that refresh token was generated with correct scope",
            "Confirm Google Ads account has active campaigns",
            "Review API quota limits and billing settings"
        ]
    }

@router.get("/oauth-url")
async def get_oauth_url(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get OAuth URL for Google Ads authentication."""
    try:
        if not hasattr(request.app.state, 'google_ads_client') or not request.app.state.google_ads_client:
            raise HTTPException(503, "Google Ads client not available")
        
        google_ads_client = request.app.state.google_ads_client
        oauth_url = google_ads_client.get_oauth_url()
        
        return {
            "oauth_url": oauth_url,
            "scope": "https://www.googleapis.com/auth/adwords",
            "instructions": [
                "1. Visit the OAuth URL above",
                "2. Grant permissions to your application", 
                "3. Copy the authorization code from the callback",
                "4. Use the code to generate refresh token"
            ],
            "is_sandbox": google_ads_client.is_sandbox,
            "oauth_playground": "https://developers.google.com/oauthplayground/"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to generate OAuth URL: {e}")
        raise HTTPException(500, f"Failed to generate OAuth URL: {str(e)}")