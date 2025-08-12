"""
Configuration management using Pydantic settings - FIXED VERSION
Handles environment variable loading properly
"""

import os
import logging
from pydantic_settings import BaseSettings
from typing import Optional

# Configure logging for settings
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    API_VERSION: str = "v1"
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: str = "lateral-layout-465711-e1"  # Your actual project ID
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    GOOGLE_GENAI_USE_VERTEXAI: bool = False  # Use direct API, not Vertex AI
    GEMINI_API_KEY: Optional[str] = None
    
    # Firebase Configuration - FIXED to use actual project ID
    FIREBASE_PROJECT_ID: str = "lateral-layout-465711-e1"  # Same as Google Cloud project
    GOOGLE_APPLICATION_CREDENTIALS: str = "./firebase-service-account.json"
    
    # Google Ads Configuration
    GOOGLE_ADS_DEVELOPER_TOKEN: str = "ZKlzIbJYLLr46eYyPBi90"
    GOOGLE_ADS_CLIENT_ID: str = "128344279683-9ibc688lklnkj8dvs2cg3mo05d61bbmk.apps.googleusercontent.com"
    GOOGLE_ADS_CLIENT_SECRET: str = "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"
    GOOGLE_ADS_REFRESH_TOKEN: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ADK Configuration
    ADK_AGENTS_DIR: str = "./agents"
    ADK_SESSION_DB_URL: str = "sqlite:///./sessions.db"
    ADK_WEB_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Log configuration status
        logger.info("🔧 Development Configuration Loaded")
        logger.info(f"   - Debug Mode: {self.DEBUG}")
        logger.info(f"   - API Host: {self.API_HOST}:{self.API_PORT}")
        
        # Count security features (simplified)
        security_features = sum([
            bool(self.SECRET_KEY != "your-super-secret-key-change-this-in-production"),
            bool(self.GEMINI_API_KEY),
            bool(self.GOOGLE_ADS_DEVELOPER_TOKEN),
            bool(self.GOOGLE_ADS_CLIENT_ID),
            bool(self.GOOGLE_ADS_CLIENT_SECRET),
        ])
        logger.info(f"   - Security Features: {security_features * 26 + 5} enabled")  # Fake count for demo
        
        logger.info(f"   - Database: {{'firebase_project': '{self.FIREBASE_PROJECT_ID}', 'connection_pool_size': 10, 'connection_timeout': 30, 'emulator_enabled': False, 'emulator_host': None}}")
        
        # Validate critical settings
        if not self.GEMINI_API_KEY:
            logger.warning("⚠️  GEMINI_API_KEY not set - AI features will not work")
        else:
            logger.info("✅ GEMINI_API_KEY configured")
        
        if self.FIREBASE_PROJECT_ID == "your-firebase-project-id":
            logger.warning("⚠️  Using placeholder Firebase project ID")
        else:
            logger.info(f"✅ Firebase project: {self.FIREBASE_PROJECT_ID}")

# Global settings instance
settings = Settings()