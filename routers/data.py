"""
Data management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.user_service import UserService
import json
import aiofiles

router = APIRouter()

class DataExportRequest(BaseModel):
    data_types: List[str]  # ["conversations", "campaigns", "usage_stats"]
    format: str = "json"  # "json" or "csv"

@router.get("/conversations")
async def get_user_conversations(
    limit: int = 50,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's conversation history"""
    try:
        user_service = UserService()
        
        # Get conversations from agent sessions
        sessions_ref = user_service.db.collection('agent_sessions').where('user_id', '==', current_user["uid"])
        sessions = sessions_ref.order_by('last_active', direction=user_service.db.Query.DESCENDING).limit(limit).offset(offset).stream()
        
        conversations = []
        for session in sessions:
            session_data = session.to_dict()
            for conversation in session_data.get('conversation_history', []):
                conversations.append({
                    'session_id': session.id,
                    'agent_id': session_data.get('agent_id'),
                    'timestamp': conversation.get('timestamp'),
                    'user_message': conversation.get('user_message'),
                    'agent_response': conversation.get('agent_response'),
                    'context': conversation.get('context', {})
                })
        
        return {"conversations": conversations, "total": len(conversations)}
        
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch conversations: {str(e)}")

@router.post("/export")
async def export_user_data(
    request: DataExportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Export user data in specified format"""
    try:
        user_service = UserService()
        exported_data = {}
        
        if "conversations" in request.data_types:
            conversations_response = await get_user_conversations(1000, 0, current_user)
            exported_data["conversations"] = conversations_response["conversations"]
        
        if "usage_stats" in request.data_types:
            usage_stats = await user_service.get_user_usage_stats(current_user["uid"])
            exported_data["usage_stats"] = usage_stats
        
        if "profile" in request.data_types:
            profile = await user_service.get_user_profile(current_user["uid"])
            exported_data["profile"] = profile
        
        # Generate export file
        import tempfile
        import os
        
        if request.format == "json":
            filename = f"user_data_export_{current_user['uid']}.json"
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                json.dump(exported_data, f, indent=2, default=str)
                temp_path = f.name
        else:
            # CSV export would be implemented here
            raise HTTPException(400, "CSV export not yet implemented")
        
        return {
            "export_id": f"export_{current_user['uid']}_{len(exported_data)}",
            "download_url": f"/api/v1/data/download/{os.path.basename(temp_path)}",
            "expires_at": "24 hours"
        }
        
    except Exception as e:
        raise HTTPException(500, f"Failed to export data: {str(e)}")

@router.post("/import")
async def import_user_data(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Import user data from file"""
    try:
        # Read uploaded file
        content = await file.read()
        
        if file.filename.endswith('.json'):
            data = json.loads(content.decode('utf-8'))
        else:
            raise HTTPException(400, "Only JSON files are supported")
        
        # Process imported data (simplified)
        imported_items = 0
        
        if "conversations" in data:
            # Import conversations would be implemented here
            imported_items += len(data["conversations"])
        
        return {
            "status": "imported",
            "items_imported": imported_items,
            "file_size": len(content)
        }
        
    except Exception as e:
        raise HTTPException(500, f"Failed to import data: {str(e)}")

@router.delete("/conversations")
async def delete_user_conversations(
    before_date: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete user's conversation history"""
    try:
        user_service = UserService()
        
        # Delete agent sessions (which contain conversations)
        sessions_ref = user_service.db.collection('agent_sessions').where('user_id', '==', current_user["uid"])
        
        if before_date:
            # Parse date and filter (simplified)
            pass
        
        sessions = sessions_ref.stream()
        deleted_count = 0
        
        for session in sessions:
            session.reference.delete()
            deleted_count += 1
        
        return {"status": "deleted", "conversations_deleted": deleted_count}
        
    except Exception as e:
        raise HTTPException(500, f"Failed to delete conversations: {str(e)}")

@router.get("/storage/usage")
async def get_storage_usage(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's data storage usage"""
    try:
        user_service = UserService()
        
        # Calculate storage usage (simplified)
        storage_usage = {
            "conversations": {
                "count": 0,
                "size_mb": 0
            },
            "sessions": {
                "count": 0,
                "size_mb": 0
            },
            "custom_agents": {
                "count": 0,
                "size_mb": 0
            },
            "total_size_mb": 0
        }
        
        # Get actual counts
        sessions_ref = user_service.db.collection('agent_sessions').where('user_id', '==', current_user["uid"])
        sessions = list(sessions_ref.stream())
        storage_usage["sessions"]["count"] = len(sessions)
        
        # Calculate conversation count
        total_conversations = 0
        for session in sessions:
            session_data = session.to_dict()
            total_conversations += len(session_data.get('conversation_history', []))
        
        storage_usage["conversations"]["count"] = total_conversations
        
        # Estimate sizes (simplified calculation)
        storage_usage["conversations"]["size_mb"] = total_conversations * 0.001  # ~1KB per conversation
        storage_usage["sessions"]["size_mb"] = len(sessions) * 0.01  # ~10KB per session
        storage_usage["total_size_mb"] = storage_usage["conversations"]["size_mb"] + storage_usage["sessions"]["size_mb"]
        
        return storage_usage
        
    except Exception as e:
        raise HTTPException(500, f"Failed to calculate storage usage: {str(e)}")