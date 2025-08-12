"""
Gemini AI service - high-level AI operations
"""

from typing import Dict, Any, List, Optional
from core.gemini_client import GeminiClient
from fastapi import HTTPException

class GeminiService:
    """High-level Gemini AI service"""
    
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    async def generate_campaign_name(
        self, 
        product_info: Dict[str, Any], 
        target_audience: str
    ) -> str:
        """Generate compelling campaign name"""
        try:
            prompt = f"""
            Generate a compelling Google Ads campaign name for:
            Product: {product_info.get('name', 'Unknown Product')}
            Description: {product_info.get('description', 'No description')}
            Target Audience: {target_audience}
            
            Requirements:
            - Maximum 30 characters
            - Clear and compelling
            - Include main benefit or feature
            - Professional tone
            
            Return only the campaign name.
            """
            
            response = await self.gemini_client.generate_content(
                prompt=prompt,
                model="gemini-2.5-flash",
                system_instruction="You are a Google Ads expert. Generate concise, compelling campaign names.",
                temperature=0.8,
                max_output_tokens=50
            )
            
            return response.strip()
            
        except Exception as e:
            raise HTTPException(500, f"Failed to generate campaign name: {str(e)}")
    
    async def generate_keywords(
        self, 
        product_info: Dict[str, Any], 
        target_audience: str,
        keyword_count: int = 20
    ) -> List[str]:
        """Generate relevant keywords"""
        try:
            prompt = f"""
            Generate {keyword_count} highly relevant Google Ads keywords for:
            Product: {product_info.get('name', 'Unknown Product')}
            Description: {product_info.get('description', 'No description')}
            Category: {product_info.get('category', 'General')}
            Target Audience: {target_audience}
            
            Requirements:
            - Mix of broad, phrase, and exact match intent
            - Include commercial intent keywords
            - Include long-tail variations
            - Consider buyer journey stages
            - Focus on high-converting potential
            
            Return as a simple list, one keyword per line.
            """
            
            response = await self.gemini_client.generate_content(
                prompt=prompt,
                model="gemini-2.5-flash",
                system_instruction="You are a keyword research expert. Generate high-converting keywords.",
                temperature=0.7,
                max_output_tokens=500
            )
            
            keywords = [kw.strip() for kw in response.split('\n') if kw.strip()]
            return keywords[:keyword_count]
            
        except Exception as e:
            raise HTTPException(500, f"Failed to generate keywords: {str(e)}")
    
    async def generate_optimization_recommendations(
        self, 
        performance_data: Dict[str, Any],
        optimization_goals: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate campaign optimization recommendations"""
        try:
            prompt = f"""
            Analyze this Google Ads campaign performance and provide optimization recommendations:
            
            Performance Data: {performance_data}
            Optimization Goals: {optimization_goals}
            
            Provide specific, actionable recommendations in the following areas:
            1. Bid adjustments
            2. Keyword optimization
            3. Ad copy improvements
            4. Targeting refinements
            5. Budget allocation
            
            For each recommendation, include:
            - Priority level (High/Medium/Low)
            - Expected impact
            - Implementation difficulty
            - Estimated timeline
            """
            
            response = await self.gemini_client.generate_content(
                prompt=prompt,
                model="gemini-2.5-pro",
                system_instruction="You are a Google Ads optimization expert. Provide data-driven, actionable recommendations.",
                temperature=0.3,
                max_output_tokens=1500
            )
            
            # Parse response into structured recommendations
            recommendations = self._parse_optimization_response(response)
            
            return recommendations
            
        except Exception as e:
            raise HTTPException(500, f"Failed to generate optimization recommendations: {str(e)}")
    
    def _parse_optimization_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured recommendations"""
        # Simplified parsing - in production, you'd want more robust parsing
        recommendations = []
        
        lines = response.split('\n')
        current_rec = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('Priority:'):
                if current_rec:
                    recommendations.append(current_rec)
                current_rec = {
                    'priority': line.replace('Priority:', '').strip(),
                    'description': '',
                    'impact': '',
                    'difficulty': '',
                    'timeline': ''
                }
            elif line.startswith('Impact:'):
                current_rec['impact'] = line.replace('Impact:', '').strip()
            elif line.startswith('Difficulty:'):
                current_rec['difficulty'] = line.replace('Difficulty:', '').strip()
            elif line.startswith('Timeline:'):
                current_rec['timeline'] = line.replace('Timeline:', '').strip()
            else:
                if current_rec and not current_rec.get('description'):
                    current_rec['description'] = line
        
        if current_rec:
            recommendations.append(current_rec)
        
        return recommendations
    
    async def analyze_competitor_ads(
        self, 
        industry: str, 
        keywords: List[str]
    ) -> Dict[str, Any]:
        """Analyze competitor advertising strategies"""
        try:
            prompt = f"""
            Analyze competitor advertising strategies for:
            Industry: {industry}
            Target Keywords: {', '.join(keywords[:10])}
            
            Provide insights on:
            1. Common messaging themes
            2. Typical ad formats and extensions
            3. Competitive positioning strategies
            4. Pricing and promotion approaches
            5. Opportunities for differentiation
            
            Focus on actionable competitive intelligence.
            """
            
            response = await self.gemini_client.generate_content(
                prompt=prompt,
                model="gemini-2.5-pro",
                system_instruction="You are a competitive intelligence expert for digital advertising.",
                temperature=0.4,
                max_output_tokens=1200
            )
            
            return {
                "analysis": response,
                "industry": industry,
                "keywords_analyzed": keywords[:10],
                "generated_at": "timestamp"
            }
            
        except Exception as e:
            raise HTTPException(500, f"Failed to analyze competitor ads: {str(e)}")
    
    async def generate_seasonal_adjustments(
        self, 
        campaign_data: Dict[str, Any], 
        season: str,
        historical_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate seasonal campaign adjustments"""
        try:
            prompt = f"""
            Generate seasonal optimization strategies for this Google Ads campaign:
            
            Campaign: {campaign_data.get('name', 'Unknown Campaign')}
            Product Category: {campaign_data.get('category', 'General')}
            Current Season: {season}
            Historical Data: {historical_data or 'Not available'}
            
            Provide recommendations for:
            1. Budget adjustments
            2. Seasonal keyword additions
            3. Ad copy modifications
            4. Bid strategy changes
            5. Targeting adjustments
            6. Promotional strategies
            
            Consider seasonal trends, consumer behavior, and competitive landscape.
            """
            
            response = await self.gemini_client.generate_content(
                prompt=prompt,
                model="gemini-2.5-pro",
                system_instruction="You are a seasonal marketing strategist specializing in Google Ads.",
                temperature=0.5,
                max_output_tokens=1000
            )
            
            return {
                "seasonal_strategy": response,
                "season": season,
                "campaign": campaign_data.get('name', 'Unknown'),
                "implementation_priority": "high" if season in ["holiday", "black_friday"] else "medium"
            }
            
        except Exception as e:
            raise HTTPException(500, f"Failed to generate seasonal adjustments: {str(e)}")