"""
Google Ads API tests
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

client = TestClient(app)

class TestGoogleAds:
    
    @patch('core.google_ads_client.GoogleAdsClient')
    @patch('core.auth.get_current_user')
    def test_get_campaigns_success(self, mock_get_user, mock_ads_client):
        """Test successful campaign retrieval"""
        
        # Mock user
        mock_get_user.return_value = {
            "uid": "test-user-123",
            "email": "test@example.com"
        }
        
        # Mock Google Ads client
        mock_client_instance = Mock()
        mock_ads_client.return_value = mock_client_instance
        
        mock_campaigns = [
            {
                "id": "123456789",
                "name": "Test Campaign",
                "status": "ENABLED",
                "type": "SEARCH"
            }
        ]
        
        mock_client_instance.get_campaigns.return_value = mock_campaigns
        
        response = client.get(
            "/api/v1/google-ads/campaigns",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "campaigns" in data
        assert len(data["campaigns"]) == 1
        assert data["campaigns"][0]["name"] == "Test Campaign"
    
    @patch('core.auth.get_current_user')
    def test_get_campaigns_no_accounts(self, mock_get_user):
        """Test campaign retrieval with no connected accounts"""
        
        mock_get_user.return_value = {
            "uid": "test-user-123",
            "email": "test@example.com"
        }
        
        response = client.get(
            "/api/v1/google-ads/campaigns",
            headers={"Authorization": "Bearer test-token"}
        )
        
        # Should return empty campaigns list when no accounts connected
        assert response.status_code == 200
        data = response.json()
        assert data["campaigns"] == []
    
    @patch('core.google_ads_client.GoogleAdsClient')
    @patch('core.auth.get_current_user')
    def test_create_campaign_success(self, mock_get_user, mock_ads_client):
        """Test successful campaign creation"""
        
        mock_get_user.return_value = {
            "uid": "test-user-123",
            "email": "test@example.com"
        }
        
        mock_client_instance = Mock()
        mock_ads_client.return_value = mock_client_instance
        
        mock_client_instance.create_campaign.return_value = {
            "campaign_id": "987654321",
            "status": "created"
        }
        
        campaign_data = {
            "name": "Test Campaign",
            "budget_amount": 100.0,
            "target_locations": ["US"],
            "keywords": ["test keyword"]
        }
        
        response = client.post(
            "/api/v1/google-ads/campaigns",
            json=campaign_data,
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["campaign_id"] == "987654321"
        assert data["status"] == "created"