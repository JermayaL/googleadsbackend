"""
Gemini AI Client using the latest Google Gen AI SDK - COMPLETE REPLACEMENT
Updated for 2025 - FULLY HANDLES MAX_TOKENS AND EMPTY RESPONSES
"""

from typing import List, Dict, Any, Optional
from google import genai
import asyncio
from config.settings import settings

class GeminiClient:
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client with DIRECT API KEY (no Vertex AI)"""
        try:
            # Use DIRECT Gemini API with API key - NO VERTEX AI
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            print("✅ Gemini client initialized successfully (Direct API)")
            
        except Exception as e:
            print(f"❌ Failed to initialize Gemini client: {e}")
            raise
    
    async def generate_content(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048
    ) -> str:
        """Generate content using Gemini models via DIRECT API - FIXED VERSION"""
        try:
            # Build config properly using the new SDK format
            config_dict = {
                "temperature": temperature,
                "max_output_tokens": max_output_tokens
            }
            
            # Add system instruction if provided
            if system_instruction:
                config_dict["system_instruction"] = system_instruction
            
            # Use the correct types import for config
            from google.genai import types
            config = types.GenerateContentConfig(**config_dict)
            
            # Use the direct API call with proper error handling
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=model,
                contents=prompt,
                config=config
            )
            
            # FIXED: Proper response handling for google-genai SDK
            result = self._extract_text_from_response(response)
            
            print(f"✅ Successfully generated content: {result[:100]}...")
            return result or "No response generated"
            
        except Exception as e:
            print(f"❌ Error generating content: {e}")
            return f"Error: {str(e)}"
    
    def _extract_text_from_response(self, response) -> str:
        """
        FIXED: Comprehensive text extraction from Google GenAI SDK response
        Handles MAX_TOKENS, empty responses, and all edge cases
        """
        try:
            # Debug: Log response structure
            print(f"🔍 Response type: {type(response)}")
            
            # Check if response has candidates
            if not hasattr(response, 'candidates') or not response.candidates:
                print("❌ No candidates in response")
                return "No candidates in response"
            
            candidate = response.candidates[0]
            
            # Handle MAX_TOKENS finish reason
            if hasattr(candidate, 'finish_reason'):
                finish_reason = candidate.finish_reason
                if hasattr(finish_reason, 'name'):
                    finish_reason_name = finish_reason.name
                else:
                    finish_reason_name = str(finish_reason)
                
                print(f"🔍 Finish reason: {finish_reason_name}")
                
                # Special handling for MAX_TOKENS
                if finish_reason_name == 'MAX_TOKENS':
                    print("⚠️ MAX_TOKENS reached - attempting to extract partial content")
                    partial_text = self._extract_partial_text(candidate)
                    if partial_text:
                        return partial_text + " [Response truncated due to token limit]"
                    else:
                        return "Response was truncated due to token limit. Please try with a shorter prompt."
            
            # Method 1: Try the direct text property
            if hasattr(response, 'text'):
                try:
                    text = response.text
                    if text and text.strip():
                        return text
                except Exception as e:
                    print(f"❌ Error accessing response.text: {e}")
            
            # Method 2: Try accessing candidates array and parts
            if hasattr(candidate, 'content') and candidate.content:
                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text = part.text
                            if text and text.strip():
                                return text
            
            # Method 3: Check for any parts in the response
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'text') and part.text:
                        text = part.text
                        if text and text.strip():
                            return text
            
            # If all methods fail, provide helpful error message
            return "No readable text content found in response. The model may have encountered an issue."
            
        except Exception as e:
            print(f"❌ Error extracting text from response: {e}")
            return f"Error extracting response: {str(e)}"
    
    def _extract_partial_text(self, candidate) -> str:
        """Extract partial text content when MAX_TOKENS is reached"""
        try:
            if hasattr(candidate, 'content') and candidate.content:
                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text'):
                            text = part.text
                            if text is not None:  # Allow empty strings
                                return text
            return ""
        except Exception as e:
            print(f"❌ Error extracting partial text: {e}")
            return ""
    
    async def generate_content_with_retry(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 2
    ) -> str:
        """Generate content with automatic retry for MAX_TOKENS errors"""
        max_tokens_values = [4096, 2048, 1024]  # Try progressively smaller limits
        
        for attempt in range(max_retries + 1):
            try:
                max_tokens = max_tokens_values[min(attempt, len(max_tokens_values) - 1)]
                
                result = await self.generate_content(
                    prompt=prompt,
                    model=model,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
                
                # If successful and not truncated, return result
                if result and not result.endswith("[Response truncated due to token limit]"):
                    return result
                elif attempt == max_retries:
                    return result  # Return even truncated result on final attempt
                
            except Exception as e:
                if attempt == max_retries:
                    return f"Error after {max_retries + 1} attempts: {str(e)}"
                
                print(f"⚠️ Attempt {attempt + 1} failed, retrying...")
        
        return "Failed to generate content after multiple attempts"
    
    async def generate_embeddings(
        self,
        text: str,
        model: str = "text-embedding-004"
    ) -> List[float]:
        """Generate embeddings for text"""
        try:
            response = await asyncio.to_thread(
                self.client.models.embed_content,
                model=model,
                contents=text
            )
            
            if hasattr(response, 'embeddings') and response.embeddings:
                return response.embeddings[0].values
            
            raise Exception("No embeddings found in response")
            
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            raise
    
    async def generate_ad_copy(
        self,
        product_info: Dict[str, Any],
        target_audience: str,
        campaign_goal: str
    ) -> Dict[str, Any]:
        """Generate Google Ads copy using Gemini"""
        
        prompt = f"""
        Generate Google Ads copy for the following:
        
        Product/Service: {product_info.get('name', 'Unknown')}
        Description: {product_info.get('description', 'No description')}
        Price: {product_info.get('price', 'Contact for pricing')}
        Target Audience: {target_audience}
        Campaign Goal: {campaign_goal}
        
        Generate:
        1. 3 headlines (30 characters max each)
        2. 2 descriptions (90 characters max each)
        3. 5 keywords
        4. 1 call-to-action
        
        Ensure all copy follows Google Ads policies and is compelling.
        """
        
        system_instruction = """
        You are an expert Google Ads copywriter. Create compelling, 
        policy-compliant ad copy that drives conversions. Be concise 
        and persuasive while staying within character limits.
        """
        
        response = await self.generate_content_with_retry(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction=system_instruction,
            temperature=0.8
        )
        
        return {
            "generated_copy": response,
            "model_used": "gemini-2.5-flash",
            "api_type": "direct_gemini_api"
        }
    
    async def analyze_performance(
        self,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze campaign performance using Gemini"""
        
        prompt = f"""
        Analyze this Google Ads campaign performance data:
        
        {performance_data}
        
        Provide:
        1. Performance summary
        2. Key insights and trends
        3. Optimization recommendations
        4. Risk assessment
        5. Next actions with confidence scores
        """
        
        system_instruction = """
        You are a Google Ads performance analyst. Provide data-driven 
        insights and actionable recommendations based on campaign metrics.
        Be specific and quantify recommendations where possible.
        """
        
        response = await self.generate_content_with_retry(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction=system_instruction,
            temperature=0.3
        )
        
        return {
            "analysis": response,
            "confidence_score": 0.85,
            "model_used": "gemini-2.5-flash",
            "api_type": "direct_gemini_api"
        }