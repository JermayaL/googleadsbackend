"""
Google Ads data models
"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class Campaign(BaseModel):
    id: str
    name: str
    status: str
    type: str  # advertising_channel_type
    budget: Optional[str] = None
    customer_id: str
    performance: Optional[Dict[str, Any]] = None

class CampaignPerformance(BaseModel):
    campaign_id: str
    date: str
    cost_micros: int
    clicks: int
    impressions: int
    ctr: float
    average_cpc: float
    conversions: float
    conversion_rate: float

class Keyword(BaseModel):
    text: str
    match_type: str
    status: str
    campaign_id: str
    ad_group_id: Optional[str] = None
    performance: Optional[Dict[str, Any]] = None

class AdGroup(BaseModel):
    id: str
    name: str
    status: str
    campaign_id: str
    cpc_bid_micros: Optional[int] = None

class Ad(BaseModel):
    id: str
    ad_group_id: str
    type: str
    status: str
    headlines: List[str] = []
    descriptions: List[str] = []
    final_urls: List[str] = []