"""
AI services tests
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

client = TestClient(app)

class TestAIServices:
    
    @patch('core.gemini_client.GeminiClient')
    @patch('core.auth.get_current_user')
    def test_generate_ad_copy_success(self, mock_get_user, mock_gemini_client):
        """Test successful ad copy generation"""
        
        mock_get_user.return_value = {
            "uid": "test-user-123",
            "email": "test@example.com"
        }
        
        mock_client_instance = Mock()
        mock_gemini_client.return_value = mock_client_instance
        
        mock_client_instance.generate_ad_copy.return_value = {
            "generated_copy": "Amazing Product - Buy Now!",
            "model_used": "gemini-2.5-pro"
        }
        
        request_data = {
            "product_info": {
                "name": "Amazing Product",
                "description": "The best product ever"
            },
            "target_audience": "Young professionals",
            "campaign_goal": "increase sales"
        }
        
        response = client.post(
            "/api/v1/ai/generate-ad-copy",
            json=request_data,
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "generated_copy" in data
        assert data["model_used"] == "gemini-2.5-pro"
    
    @patch('core.gemini_client.GeminiClient')
    @patch('core.auth.get_current_user')
    def test_analyze_performance_success(self, mock_get_user, mock_gemini_client):
        """Test successful performance analysis"""
        
        mock_get_user.return_value = {
            "uid": "test-user-123",
            "email": "test@example.com"
        }
        
        mock_client_instance = Mock()
        mock_gemini_client.return_value = mock_client_instance
        
        mock_client_instance.analyze_performance.return_value = {
            "analysis": "Campaign performance is above average",
            "confidence_score": 0.85
        }
        
        request_data = {
            "performance_data": {
                "clicks": 1000,
                "impressions": 50000,
                "ctr": 0.02,
                "cost": 500
            }
        }
        
        response = client.post(
            "/api/v1/ai/analyze-performance",
            json=request_data,
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert data["confidence_score"] == 0.85
    
    @patch('core.gemini_client.GeminiClient')
    @patch('core.auth.get_current_user')
    def test_contextual_assist_success(self, mock_get_user, mock_gemini_client):
        """Test successful contextual AI assistance"""
        
        mock_get_user.return_value = {
            "uid": "test-user-123",
            "email": "test@example.com"
        }
        
        mock_client_instance = Mock()
        mock_gemini_client.return_value = mock_client_instance
        
        mock_client_instance.generate_content.return_value = "Here are some optimization suggestions for your campaign..."
        
        request_data = {
            "message": "How can I improve this campaign?",
            "context": {
                "page_type": "campaigns",
                "current_data": {
                    "campaign_name": "Test Campaign",
                    "ctr": "2.5%"
                }
            }
        }
        
        response = client.post(
            "/api/v1/ai/contextual-assist",
            json=request_data,
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "context_used" in data