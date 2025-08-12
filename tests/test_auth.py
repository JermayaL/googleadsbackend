"""
Authentication tests
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

client = TestClient(app)

class TestAuthentication:
    
    @patch('core.auth.AuthService')
    def test_chrome_extension_auth_success(self, mock_auth_service):
        """Test successful Chrome extension authentication"""
        
        # Mock the auth service
        mock_auth_instance = Mock()
        mock_auth_service.return_value = mock_auth_instance
        
        mock_auth_instance.get_or_create_user.return_value = {
            "uid": "test-user-123",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        # Test data
        test_data = {
            "userInfo": {
                "uid": "test-user-123",
                "email": "test@example.com",
                "name": "Test User"
            },
            "extensionId": "test-extension-id"
        }
        
        response = client.post("/api/v1/auth/chrome-extension", json=test_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "authenticated"
        assert "session_id" in data
        assert "user" in data
    
    def test_chrome_extension_auth_invalid_data(self):
        """Test Chrome extension auth with invalid data"""
        
        response = client.post("/api/v1/auth/chrome-extension", json={})
        
        assert response.status_code == 422  # Validation error
    
    @patch('core.auth.get_current_user')
    def test_get_current_user_success(self, mock_get_user):
        """Test getting current user info"""
        
        mock_get_user.return_value = {
            "uid": "test-user-123",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["uid"] == "test-user-123"
    
    def test_get_current_user_unauthorized(self):
        """Test getting user info without authorization"""
        
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401

@pytest.fixture
def mock_firebase():
    """Mock Firebase for testing"""
    with patch('firebase_admin.initialize_app'), \
         patch('firebase_admin.auth.verify_id_token') as mock_verify, \
         patch('firebase_admin.firestore.client') as mock_firestore:
        
        mock_verify.return_value = {
            "uid": "test-user-123",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        yield {
            "verify": mock_verify,
            "firestore": mock_firestore
        }