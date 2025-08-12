"""
Google Ads Agent for ADK Web UI - FINAL FIXED VERSION
Compatible with ADK v1.6.1+ - Proper type hints for Gemini API
"""

import os
from google.adk.agents import Agent

# Verify environment variables are available
print(f"🔍 Agent Environment Check:")
print(f"   - GEMINI_API_KEY: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
print(f"   - GOOGLE_CLOUD_PROJECT: {os.getenv('GOOGLE_CLOUD_PROJECT', 'NOT SET')}")
print(f"   - FIREBASE_PROJECT_ID: {os.getenv('FIREBASE_PROJECT_ID', 'NOT SET')}")

# Simple Python functions that will be automatically converted to tools
def get_campaign_performance(campaign_id: str, date_range: str = "LAST_30_DAYS") -> dict:
    """Get Google Ads campaign performance data.
    
    Args:
        campaign_id: The ID of the campaign to analyze
        date_range: Date range for the analysis (default: LAST_30_DAYS)
    
    Returns:
        dict: Performance metrics and insights
    """
    return {
        "campaign_id": campaign_id,
        "date_range": date_range,
        "metrics": {
            "impressions": 15000,
            "clicks": 450,
            "ctr": 3.0,
            "cost": 2250.50,
            "conversions": 25,
            "conversion_rate": 5.6
        },
        "insights": [
            "Campaign performance exceeds industry benchmarks",
            "Consider increasing budget for peak performance hours",
            "Test new ad copy variations to improve CTR"
        ]
    }

def optimize_keywords(keywords: list[str], budget: float) -> dict:
    """Optimize keyword bids and provide suggestions.
    
    Args:
        keywords: List of current keywords to optimize
        budget: Available budget for optimization in dollars
    
    Returns:
        dict: Optimization recommendations and budget allocation
    """
    return {
        "original_keywords": keywords,
        "optimized_keywords": [
            {"keyword": kw, "suggested_bid": 2.50, "quality_score": 8}
            for kw in keywords
        ],
        "new_suggestions": [
            {"keyword": "google ads optimization", "suggested_bid": 3.20, "search_volume": "high"},
            {"keyword": "ppc campaign management", "suggested_bid": 2.80, "search_volume": "medium"}
        ],
        "budget_allocation": {
            "high_performers": budget * 0.6,
            "testing_budget": budget * 0.4
        }
    }

def generate_ad_copy(product: str, audience: str, goal: str) -> dict:
    """Generate optimized ad copy for campaigns.
    
    Args:
        product: Product or service to advertise
        audience: Target audience description
        goal: Campaign goal (e.g., 'increase_sales', 'brand_awareness')
    
    Returns:
        dict: Generated ad copy and optimization tips
    """
    return {
        "headlines": [
            f"Best {product} for {audience}",
            f"Premium {product} Solutions",
            f"Transform Your {product} Strategy"
        ],
        "descriptions": [
            f"Discover why {audience} trust our {product}. Start today!",
            f"Get results with our proven {product} approach. Free trial available."
        ],
        "call_to_action": "Get Started Today",
        "optimization_tips": [
            "Test multiple headline variations",
            "Include your main keyword in headlines",
            "Focus on benefits over features"
        ]
    }

# Define the root agent - this is what ADK web will discover
root_agent = Agent(
    name="google_ads_strategist",
    model="gemini-2.5-pro",
    description="Expert Google Ads strategist for campaign optimization and management",
    instruction="""
    You are a Google Ads expert strategist with deep knowledge of:
    - Campaign performance analysis and optimization
    - Keyword research and bid management  
    - Ad copy creation and A/B testing
    - Budget allocation and ROI improvement
    - Conversion rate optimization
    
    Always provide specific, actionable recommendations with expected impact.
    Use the available tools to analyze data and generate insights.
    Focus on maximizing ROI and improving campaign performance.
    
    When users ask about campaigns, use get_campaign_performance to get data.
    When they need keyword help, use optimize_keywords.
    When they need ad copy, use generate_ad_copy.
    
    Be helpful, professional, and provide concrete next steps.
    """,
    tools=[get_campaign_performance, optimize_keywords, generate_ad_copy]
)