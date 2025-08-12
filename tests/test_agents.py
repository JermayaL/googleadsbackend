"""
Agent management tests
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

client = TestClient(app)

class TestAgents:
    
    @patch('services.agent_service.AgentService')
    @patch('core.auth.get_current_user')
    def test_get_available_agents_success(self, mock_get_user, mock_agent_service):
        """Test getting available agents"""
        
        mock_get_user.return_value = {
            "uid": "test-user-123",
            "email": "test@example.com"
        }
        
        mock_service_instance = Mock()
        mock_agent_service.return_value = mock_service_instance
        
        mock_agents = [
            {
                "id": "campaign_manager",
                "name": "Campaign Manager",
                "description": "AI assistant for campaign management",
                "available": True
            }
        ]
        
        mock_service_instance.get_available_agents.return_value = mock_agents
        
        response = client.get(
            "/api/v1/agents/available",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) == 1
        assert data["agents"][0]["name"] == "Campaign Manager"
    
    @patch('services.agent_service.AgentService')
    @patch('core.auth.get_current_user')
    def test_create_agent_session_success(self, mock_get_user, mock_agent_service):
        """Test creating agent session"""
        
        mock_get_user.return_value = {
            "uid": "test-user-123",
            "email": "test@example.com"
        }
        
        mock_service_instance = Mock()
        mock_agent_service.return_value = mock_service_instance
        
        mock_service_instance.create_agent_session.return_value = {
            "session_id": "session_123",
            "agent_id": "campaign_manager",
            "status": "created"
        }
        
        request_data = {
            "agent_id": "campaign_manager"
        }
        
        response = client.post(
            "/api/v1/agents/session",
            json=request_data,
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "session_123"
        assert data["agent_id"] == "campaign_manager"
    
    @patch('services.agent_service.AgentService')
    @patch('services.user_service.UserService')
    @patch('core.auth.get_current_user')
    def test_run_agent_success(self, mock_get_user, mock_user_service, mock_agent_service):
        """Test running an agent"""
        
        mock_get_user.return_value = {
            "uid": "test-user-123",
            "email": "test@example.com"
        }
        
        # Mock services
        mock_agent_instance = Mock()
        mock_user_instance = Mock()
        mock_agent_service.return_value = mock_agent_instance
        mock_user_service.return_value = mock_user_instance
        
        mock_agent_instance.create_agent_session.return_value = {
            "session_id": "session_123"
        }
        
        request_data = {
            "message": "Help me optimize my campaigns"
        }
        
        response = client.post(
            "/api/v1/agents/campaign_manager/run",
            json=request_data,
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert data["agent_id"] == "campaign_manager"