"""
Campaign Manager Agent for ADK Web UI
"""

from google.adk.agents import Agent

def manage_campaign_budget(campaign_id: str, action: str, amount: float) -> dict:
    """Manage campaign budget operations.
    
    Args:
        campaign_id: ID of the campaign to manage
        action: Action to take (increase, decrease, pause, resume)
        amount: Budget amount for increase/decrease actions
    
    Returns:
        dict: Budget management results
    """
    return {
        "campaign_id": campaign_id,
        "action_taken": action,
        "budget_amount": amount,
        "status": "success",
        "message": f"Campaign {campaign_id} budget {action} by ${amount}",
        "new_daily_budget": 150.00 + amount if action == "increase" else 150.00 - amount,
        "estimated_impact": {
            "impression_change": f"+{amount * 10}%" if action == "increase" else f"-{amount * 10}%",
            "click_change": f"+{amount * 8}%" if action == "increase" else f"-{amount * 8}%"
        }
    }

def optimize_campaign_settings(campaign_id: str, optimization_type: str) -> dict:
    """Optimize campaign settings and configuration.
    
    Args:
        campaign_id: ID of the campaign to optimize
        optimization_type: Type of optimization (bidding, targeting, scheduling, keywords)
    
    Returns:
        dict: Optimization results and recommendations
    """
    return {
        "campaign_id": campaign_id,
        "optimization_type": optimization_type,
        "changes_made": [
            "Updated bid strategy to Target CPA",
            "Added demographic targeting refinements",
            "Optimized ad scheduling for peak hours",
            "Added negative keywords to improve relevance"
        ],
        "expected_improvements": {
            "cost_efficiency": "12-18% improvement",
            "conversion_rate": "15-20% increase",
            "quality_score": "8-15% improvement"
        },
        "monitoring_required": [
            "Track CPA changes over next 7 days",
            "Monitor impression share",
            "Review search terms weekly"
        ]
    }

def create_campaign_plan(product_name: str, target_audience: str, budget: float, goals: list[str]) -> dict:
    """Create a comprehensive campaign plan.
    
    Args:
        product_name: Name of product or service to advertise
        target_audience: Description of target audience
        budget: Total campaign budget
        goals: List of campaign goals
    
    Returns:
        dict: Complete campaign plan with strategy
    """
    return {
        "product_name": product_name,
        "target_audience": target_audience,
        "total_budget": budget,
        "campaign_goals": goals,
        "recommended_structure": {
            "campaigns": 3,
            "ad_groups_per_campaign": 5,
            "keywords_per_ad_group": 15,
            "ads_per_ad_group": 3
        },
        "budget_allocation": {
            "search_campaigns": budget * 0.7,
            "display_campaigns": budget * 0.2,
            "video_campaigns": budget * 0.1
        },
        "timeline": {
            "setup_phase": "1-2 weeks",
            "optimization_phase": "3-4 weeks",
            "scaling_phase": "ongoing"
        },
        "key_metrics_to_track": [
            "Cost per acquisition (CPA)",
            "Return on ad spend (ROAS)",
            "Quality Score",
            "Impression Share"
        ]
    }

def schedule_campaign_actions(campaign_id: str, actions: list[str], schedule_date: str) -> dict:
    """Schedule future campaign management actions.
    
    Args:
        campaign_id: ID of the campaign
        actions: List of actions to schedule
        schedule_date: Date to execute actions (YYYY-MM-DD format)
    
    Returns:
        dict: Scheduling confirmation and details
    """
    return {
        "campaign_id": campaign_id,
        "scheduled_actions": actions,
        "execution_date": schedule_date,
        "status": "scheduled",
        "action_details": [
            {
                "action": action,
                "estimated_duration": "5-10 minutes",
                "impact_level": "medium"
            } for action in actions
        ],
        "reminders_set": [
            f"Email reminder 24 hours before {schedule_date}",
            f"Dashboard notification on {schedule_date}"
        ],
        "backup_plan": "Manual execution available if automation fails"
    }

root_agent = Agent(
    name="campaign_manager_agent",
    model="gemini-2.5-pro",
    description="Campaign management specialist for Google Ads operations",
    instruction="""
    You are a Google Ads campaign management specialist responsible for:
    
    1. Campaign budget management and optimization
    2. Campaign settings and configuration management
    3. Strategic campaign planning and structure
    4. Scheduling and automation of campaign tasks
    
    Your responsibilities include:
    - Budget allocation and bid management
    - Campaign structure optimization
    - Performance monitoring and adjustments
    - Strategic planning and execution
    
    Always provide:
    - Clear action plans with expected outcomes
    - Risk assessments for changes
    - Timeline estimates for implementation
    - Monitoring requirements and success metrics
    
    Be proactive in suggesting optimizations and improvements.
    """,
    tools=[manage_campaign_budget, optimize_campaign_settings, create_campaign_plan, schedule_campaign_actions]
)