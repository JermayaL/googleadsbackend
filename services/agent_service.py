"""
Agent management service for ADK integration - FIXED FOR 2025 FIRESTORE API
Updated with proper timestamp handling based on 2025 API documentation
"""

from typing import Dict, Any, List, Optional
from google.cloud import firestore
from core.auth import AuthService
from fastapi import HTTPException
import json
import os
import datetime

class AgentService:
    def __init__(self):
        self.auth_service = AuthService()
        self.db = self.auth_service.db
    
    async def create_agent_session(self, user_id: str, agent_id: str) -> Dict[str, Any]:
        """Create a new agent session for user"""
        try:
            # FIXED: Use datetime.datetime.now() instead of SERVER_TIMESTAMP for individual fields
            current_time = datetime.datetime.now()
            
            session_data = {
                'user_id': user_id,
                'agent_id': agent_id,
                'conversation_history': [],
                'context': {},
                'created_at': current_time,  # FIXED: Use datetime object directly
                'last_active': current_time,  # FIXED: Use datetime object directly
                'status': 'active'
            }
            
            session_ref = self.db.collection('agent_sessions').document()
            session_ref.set(session_data)
            
            return {
                'session_id': session_ref.id,
                'agent_id': agent_id,
                'status': 'created'
            }
            
        except Exception as e:
            raise HTTPException(500, f"Error creating agent session: {str(e)}")
    
    async def get_user_agent_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all agent sessions for a user"""
        try:
            sessions_ref = self.db.collection('agent_sessions').where('user_id', '==', user_id)
            sessions = sessions_ref.order_by('last_active', direction=firestore.Query.DESCENDING).stream()
            
            result = []
            for session in sessions:
                session_data = session.to_dict()
                session_data['session_id'] = session.id
                result.append(session_data)
            
            return result
            
        except Exception as e:
            raise HTTPException(500, f"Error fetching agent sessions: {str(e)}")
    
    async def update_session_conversation(
        self, 
        session_id: str, 
        user_message: str, 
        agent_response: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Update conversation history in session - FIXED for 2025 API"""
        try:
            session_ref = self.db.collection('agent_sessions').document(session_id)
            
            # FIXED: Use datetime.datetime.now() directly
            current_time = datetime.datetime.now()
            
            conversation_entry = {
                'timestamp': current_time,  # FIXED: Use datetime object
                'user_message': user_message,
                'agent_response': agent_response,
                'context': context or {}
            }
            
            # FIXED: Update the document properly with 2025 API
            session_ref.update({
                'conversation_history': firestore.ArrayUnion([conversation_entry]),
                'last_active': current_time  # FIXED: Use datetime object
            })
            
        except Exception as e:
            raise HTTPException(500, f"Error updating conversation: {str(e)}")
    
    async def get_available_agents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get list of available agents for user"""
        try:
            # Get user's subscription to determine available agents
            user_doc = self.db.collection('users').document(user_id).get()
            subscription_plan = user_doc.to_dict().get('subscription_plan', 'free') if user_doc.exists else 'free'
            
            # Define available agents based on subscription
            agents = [
                {
                    'id': 'campaign_manager',
                    'name': 'Campaign Manager',
                    'description': 'AI assistant for Google Ads campaign management and optimization',
                    'category': 'campaign_management',
                    'available': True
                },
                {
                    'id': 'keyword_researcher',
                    'name': 'Keyword Researcher', 
                    'description': 'AI-powered keyword research and analysis',
                    'category': 'keyword_research',
                    'available': subscription_plan in ['pro', 'enterprise']
                },
                {
                    'id': 'creative_optimizer',
                    'name': 'Creative Optimizer',
                    'description': 'Generate and optimize ad copy and creatives',
                    'category': 'creative',
                    'available': subscription_plan in ['pro', 'enterprise']
                },
                {
                    'id': 'performance_analyst',
                    'name': 'Performance Analyst',
                    'description': 'Deep performance analysis and recommendations',
                    'category': 'analytics',
                    'available': subscription_plan == 'enterprise'
                }
            ]
            
            return agents
            
        except Exception as e:
            raise HTTPException(500, f"Error fetching available agents: {str(e)}")
    
    async def deploy_custom_agent(self, user_id: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a custom agent created by user"""
        try:
            # Validate agent configuration
            required_fields = ['name', 'instruction', 'tools']
            for field in required_fields:
                if field not in agent_config:
                    raise HTTPException(400, f"Missing required field: {field}")
            
            # FIXED: Use datetime.datetime.now() for timestamps
            current_time = datetime.datetime.now()
            
            # Store agent configuration
            agent_data = {
                'user_id': user_id,
                'name': agent_config['name'],
                'description': agent_config.get('description', ''),
                'instruction': agent_config['instruction'],
                'tools': agent_config['tools'],
                'model': agent_config.get('model', 'gemini-2.5-flash'),
                'created_at': current_time,  # FIXED: Use datetime object
                'status': 'active',
                'deployment_status': 'deploying'
            }
            
            agent_ref = self.db.collection('custom_agents').document()
            agent_ref.set(agent_data)
            
            # Create agent file structure (simplified)
            agent_id = agent_ref.id
            await self._create_agent_files(agent_id, agent_config)
            
            # Update deployment status
            agent_ref.update({'deployment_status': 'deployed'})
            
            return {
                'agent_id': agent_id,
                'status': 'deployed',
                'endpoint': f'/api/v1/agents/{agent_id}/run'
            }
            
        except Exception as e:
            raise HTTPException(500, f"Error deploying custom agent: {str(e)}")
    
    async def _create_agent_files(self, agent_id: str, agent_config: Dict[str, Any]):
        """Create agent files for ADK"""
        try:
            agent_dir = f"agents/custom_{agent_id}"
            os.makedirs(agent_dir, exist_ok=True)
            
            # Create agent.py file
            agent_code = f'''
"""
Custom Agent: {agent_config['name']}
Auto-generated by Google Ads AI System
"""

from google.adk.agents import Agent
from agents.base_infrastructure_agent import INFRASTRUCTURE_TOOLS

root_agent = Agent(
    name="{agent_config['name'].lower().replace(' ', '_')}",
    model="{agent_config.get('model', 'gemini-2.5-flash')}",
    instruction="""{agent_config['instruction']}""",
    description="{agent_config.get('description', '')}",
    tools=INFRASTRUCTURE_TOOLS,
)
'''
            
            with open(f"{agent_dir}/agent.py", 'w') as f:
                f.write(agent_code)
            
            # Create __init__.py
            with open(f"{agent_dir}/__init__.py", 'w') as f:
                f.write("")
            
            # Create .env file
            env_content = f'''
GOOGLE_CLOUD_PROJECT={os.getenv('GOOGLE_CLOUD_PROJECT')}
GOOGLE_CLOUD_LOCATION={os.getenv('GOOGLE_CLOUD_LOCATION')}
GOOGLE_GENAI_USE_VERTEXAI=True
'''
            
            with open(f"{agent_dir}/.env", 'w') as f:
                f.write(env_content)
                
        except Exception as e:
            print(f"Error creating agent files: {e}")
            raise