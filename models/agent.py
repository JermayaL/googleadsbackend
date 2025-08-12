"""
Agent data models for ADK integration
"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class AgentSession(BaseModel):
    session_id: str
    user_id: str
    agent_id: str
    conversation_history: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {}
    created_at: datetime
    last_active: datetime
    status: str = "active"

class AgentMessage(BaseModel):
    timestamp: datetime
    user_message: str
    agent_response: str
    context: Dict[str, Any] = {}
    tools_used: List[str] = []

class CustomAgent(BaseModel):
    agent_id: str
    user_id: str
    name: str
    description: Optional[str] = None
    instruction: str
    tools: List[str]
    model: str = "gemini-2.5-flash"
    created_at: datetime
    status: str = "active"
    deployment_status: str = "deployed"
    usage_count: int = 0

class AgentTool(BaseModel):
    name: str
    description: str
    category: str
    parameters: Dict[str, Any] = {}
    available_in_plans: List[str] = ["free", "pro", "enterprise"]