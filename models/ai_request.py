"""
AI service request and response models
"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class AIGenerationRequest(BaseModel):
    prompt: str
    model: str = "gemini-2.5-flash"
    system_instruction: Optional[str] = None
    temperature: float = 0.7
    max_output_tokens: int = 1024
    context: Dict[str, Any] = {}

class AIGenerationResponse(BaseModel):
    response: str
    model_used: str
    tokens_used: Optional[int] = None
    processing_time_ms: int
    context: Dict[str, Any] = {}

class AdCopyGenerationRequest(BaseModel):
    product_info: Dict[str, Any]
    target_audience: str
    campaign_goal: str
    brand_guidelines: Optional[Dict[str, Any]] = None

class AdCopyGenerationResponse(BaseModel):
    headlines: List[str]
    descriptions: List[str]
    keywords: List[str]
    call_to_action: str
    model_used: str
    confidence_score: float

class PerformanceAnalysisRequest(BaseModel):
    performance_data: Dict[str, Any]
    comparison_data: Optional[Dict[str, Any]] = None
    analysis_type: str = "comprehensive"

class PerformanceAnalysisResponse(BaseModel):
    summary: str
    insights: List[str]
    recommendations: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    confidence_score: float
    model_used: str

class ContextualAssistRequest(BaseModel):
    message: str
    context: Dict[str, Any]
    page_type: Optional[str] = None
    user_intent: Optional[str] = None

class ContextualAssistResponse(BaseModel):
    response: str
    suggestions: List[str] = []
    quick_actions: List[Dict[str, Any]] = []
    context_used: Dict[str, Any]
    confidence_score: float