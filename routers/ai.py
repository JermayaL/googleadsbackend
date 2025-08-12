"""
AI services endpoints using Gemini
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from core.gemini_client import GeminiClient
from core.auth import get_current_user

router = APIRouter()

class AdCopyRequest(BaseModel):
    product_info: Dict[str, Any]
    target_audience: str
    campaign_goal: str

class PerformanceAnalysisRequest(BaseModel):
    performance_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

class EmbeddingRequest(BaseModel):
    text: str

@router.post("/generate-ad-copy")
async def generate_ad_copy(
    request: AdCopyRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate ad copy using Gemini AI"""
    try:
        gemini_client = GeminiClient()
        
        result = await gemini_client.generate_ad_copy(
            request.product_info,
            request.target_audience,
            request.campaign_goal
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(500, f"Failed to generate ad copy: {str(e)}")

@router.post("/analyze-performance")
async def analyze_performance(
    request: PerformanceAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze campaign performance using Gemini AI"""
    try:
        gemini_client = GeminiClient()
        
        result = await gemini_client.analyze_performance(request.performance_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(500, f"Failed to analyze performance: {str(e)}")

@router.post("/embed")
async def generate_embeddings(
    request: EmbeddingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate text embeddings"""
    try:
        gemini_client = GeminiClient()
        
        embeddings = await gemini_client.generate_embeddings(request.text)
        
        return {"embeddings": embeddings, "text": request.text}
        
    except Exception as e:
        raise HTTPException(500, f"Failed to generate embeddings: {str(e)}")

@router.post("/contextual-assist")
async def contextual_ai_assist(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """AI assistance based on current Google Ads page context (for Chrome extension)"""
    try:
        gemini_client = GeminiClient()
        
        # Create context-aware prompt
        context = request.get("context", {})
        message = request.get("message", "")
        
        prompt = f"""
        User is on Google Ads page: {context.get('page_type', 'unknown')}
        Current data: {context.get('current_data', {})}
        User question: {message}
        
        Provide helpful, specific advice for optimizing their Google Ads based on this context.
        """
        
        response = await gemini_client.generate_content(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction="You are a Google Ads optimization expert. Provide specific, actionable advice."
        )
        
        return {"response": response, "context_used": context}
        
    except Exception as e:
        raise HTTPException(500, f"Failed to provide AI assistance: {str(e)}")