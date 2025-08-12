"""
Agent management endpoints for ADK integration
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.agent_service import AgentService
from services.user_service import UserService

router = APIRouter()

class AgentSessionRequest(BaseModel):
    agent_id: str
    context: Optional[Dict[str, Any]] = None

class AgentRunRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class CustomAgentRequest(BaseModel):
    name: str
    description: Optional[str] = None
    instruction: str
    tools: List[str]
    model: Optional[str] = "gemini-2.5-flash"

@router.get("/available")
async def get_available_agents(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get list of available agents for user"""
    try:
        agent_service = AgentService()
        agents = await agent_service.get_available_agents(current_user["uid"])
        
        return {"agents": agents}
        
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch available agents: {str(e)}")

@router.post("/session")
async def create_agent_session(
    request: AgentSessionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new agent session"""
    try:
        agent_service = AgentService()
        session = await agent_service.create_agent_session(current_user["uid"], request.agent_id)
        
        return session
        
    except Exception as e:
        raise HTTPException(500, f"Failed to create agent session: {str(e)}")

@router.get("/sessions")
async def get_user_agent_sessions(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all agent sessions for user"""
    try:
        agent_service = AgentService()
        sessions = await agent_service.get_user_agent_sessions(current_user["uid"])
        
        return {"sessions": sessions}
        
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch agent sessions: {str(e)}")

async def _run_campaign_manager(message: str, context: Dict[str, Any]) -> str:
    """Simulate campaign manager agent"""
    from core.gemini_client import GeminiClient
    
    gemini_client = GeminiClient()
    
    prompt = f"""
    You are a Google Ads campaign manager AI. The user said: "{message}"
    
    User context: {context}
    
    Provide helpful advice about Google Ads campaign management.
    """
    
    response = await gemini_client.generate_content(
        prompt=prompt,
        system_instruction="You are an expert Google Ads campaign manager. Provide specific, actionable advice."
    )
    
    return response

async def _run_keyword_researcher(message: str, context: Dict[str, Any]) -> str:
    """Simulate keyword research agent"""
    from core.gemini_client import GeminiClient
    
    gemini_client = GeminiClient()
    
    prompt = f"""
    You are a keyword research specialist. The user said: "{message}"
    
    Provide keyword research insights and recommendations.
    """
    
    response = await gemini_client.generate_content(
        prompt=prompt,
        system_instruction="You are a keyword research expert. Suggest relevant keywords with search volume insights."
    )
    
    return response

@router.post("/{agent_id}/run")
async def run_agent(
    agent_id: str,
    request: AgentRunRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Run an agent with user input"""
    try:
        agent_service = AgentService()
        user_service = UserService()
        
        # Create session if not provided
        session_id = request.session_id
        if not session_id:
            session = await agent_service.create_agent_session(current_user["uid"], agent_id)
            session_id = session["session_id"]
        
        # Add user context to the request
        user_context = {
            "user_id": current_user["uid"],
            "session_id": session_id
        }
        
        # Add request context if provided
        if request.context:
            user_context.update(request.context)
        
        # Simulate agent processing (in real implementation, this would use ADK)
        if agent_id == "campaign_manager":
            agent_response = await _run_campaign_manager(request.message, user_context)
        elif agent_id == "keyword_researcher":
            agent_response = await _run_keyword_researcher(request.message, user_context)
        else:
            agent_response = "I'm an AI assistant ready to help with your Google Ads!"
        
        # Update conversation history
        await agent_service.update_session_conversation(
            session_id, request.message, agent_response, user_context
        )
        
        # Track usage
        await user_service.increment_usage(current_user["uid"], "ai_generations")
        
        return {
            "response": agent_response,
            "session_id": session_id,
            "agent_id": agent_id
        }
        
    except Exception as e:
        raise HTTPException(500, f"Failed to run agent: {str(e)}")

@router.get("/{agent_id}/history")
async def get_agent_interaction_history(
    agent_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's interaction history with specific agent"""
    try:
        agent_service = AgentService()
        
        # Get all sessions for this agent
        sessions = await agent_service.get_user_agent_sessions(current_user["uid"])
        agent_sessions = [s for s in sessions if s.get("agent_id") == agent_id]
        
        return {"agent_id": agent_id, "sessions": agent_sessions}
        
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch agent history: {str(e)}")

@router.post("/custom")
async def deploy_custom_agent(
    request: CustomAgentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Deploy a custom agent created by user"""
    try:
        agent_service = AgentService()
        user_service = UserService()
        
        # Check user's subscription plan
        user_profile = await user_service.get_user_profile(current_user["uid"])
        subscription_plan = user_profile.get("subscription_plan", "free")
        
        if subscription_plan == "free":
            raise HTTPException(403, "Custom agents require Pro or Enterprise subscription")
        
        result = await agent_service.deploy_custom_agent(current_user["uid"], request.dict())
        
        await user_service.increment_usage(current_user["uid"], "agents_created")
        
        return result
        
    except Exception as e:
        raise HTTPException(500, f"Failed to deploy custom agent: {str(e)}")

@router.get("/custom")
async def get_custom_agents(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's custom agents"""
    try:
        agent_service = AgentService()
        
        # Get custom agents from Firestore
        agents_ref = agent_service.db.collection('custom_agents').where('user_id', '==', current_user["uid"])
        agents = agents_ref.stream()
        
        result = []
        for agent in agents:
            agent_data = agent.to_dict()
            agent_data['agent_id'] = agent.id
            result.append(agent_data)
        
        return {"custom_agents": result}
        
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch custom agents: {str(e)}")