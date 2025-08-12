"""
Data models package
"""

from .user import User, GoogleAdsConnection, UserSession, UsageStats
from .google_ads import Campaign, CampaignPerformance, Keyword, AdGroup, Ad
from .agent import AgentSession, AgentMessage, CustomAgent, AgentTool
from .ai_request import (
    AIGenerationRequest,
    AIGenerationResponse,
    AdCopyGenerationRequest,
    AdCopyGenerationResponse,
    PerformanceAnalysisRequest,
    PerformanceAnalysisResponse,
    ContextualAssistRequest,
    ContextualAssistResponse
)

__all__ = [
    # User models
    "User",
    "GoogleAdsConnection", 
    "UserSession",
    "UsageStats",
    # Google Ads models
    "Campaign",
    "CampaignPerformance",
    "Keyword",
    "AdGroup",
    "Ad",
    # Agent models
    "AgentSession",
    "AgentMessage",
    "CustomAgent",
    "AgentTool",
    # AI models
    "AIGenerationRequest",
    "AIGenerationResponse",
    "AdCopyGenerationRequest",
    "AdCopyGenerationResponse",
    "PerformanceAnalysisRequest",
    "PerformanceAnalysisResponse",
    "ContextualAssistRequest",
    "ContextualAssistResponse"
]