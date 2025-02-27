import aiohttp
import json
import logging
from typing import Dict, List, Optional
import asyncio

logger = logging.getLogger(__name__)

class DeepseekAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def _make_request(self, messages: List[Dict]) -> Optional[Dict]:
        """Make a request to Deepseek API"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
                
                logger.info(f"Making request to Deepseek API with payload: {json.dumps(payload)}")
                
                async with session.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_text = await response.text()
                    logger.info(f"Deepseek API response: {response_text}")
                    
                    if response.status == 200:
                        data = json.loads(response_text)
                        content = data['choices'][0]['message']['content']
                        
                        # Try to parse the response as JSON
                        try:
                            return json.loads(content)
                        except json.JSONDecodeError:
                            # If not JSON, return as structured data
                            return self._parse_markdown_response(content)
                    else:
                        logger.error(f"Deepseek API error: {response_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error making Deepseek request: {e}")
            return None

    def _parse_markdown_response(self, content: str) -> Dict:
        """Parse markdown response into structured data"""
        try:
            sections = {}
            current_section = None
            current_content = []
            
            for line in content.split('\n'):
                if line.startswith('###'):
                    # Save previous section
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    # Start new section
                    current_section = line.replace('#', '').strip()
                    current_content = []
                else:
                    current_content.append(line)
            
            # Save last section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            
            return {
                "analysis": sections,
                "format": "markdown"
            }
            
        except Exception as e:
            logger.error(f"Error parsing markdown: {e}")
            return {"error": "Failed to parse response"}

    async def analyze_app_metadata(self, app_metadata: Dict, competitor_metadata: List[Dict]) -> Dict:
        """Analyze app metadata and provide ASO recommendations"""
        try:
            prompt = f"""As an ASO expert for B2B and wholesale apps, analyze this app metadata and provide detailed recommendations:

App Metadata:
{json.dumps(app_metadata, indent=2)}

Competitor Metadata:
{json.dumps(competitor_metadata, indent=2)}

Provide a detailed analysis with these sections:
1. Title Optimization
2. Description Analysis
3. Keyword Opportunities
4. Competitive Advantages
5. Feature Recommendations
6. Category-specific Suggestions
7. Priority Actions

Focus on B2B wholesale domain best practices. Format your response in clear sections with ### headers."""

            messages = [
                {"role": "system", "content": "You are an expert ASO analyst specializing in B2B and wholesale applications."},
                {"role": "user", "content": prompt}
            ]

            return await self._make_request(messages)
            
        except Exception as e:
            logger.error(f"Error analyzing metadata: {e}")
            return {"error": str(e)}

    async def generate_keyword_suggestions(self, base_keyword: str, industry: str = "B2B wholesale") -> Dict:
        """Generate keyword suggestions using AI analysis"""
        try:
            prompt = f"""As an ASO expert for {industry} apps, analyze this keyword and provide detailed suggestions:

Base Keyword: {base_keyword}

Provide a detailed analysis with these sections:
1. Keyword Relevance
2. Search Intent
3. Competition Analysis
4. SEO Strategy
5. Related Keywords
6. Industry-specific Variations
7. Priority Recommendations

Format your response in clear sections with ### headers."""

            messages = [
                {"role": "system", "content": "You are an expert ASO keyword analyst for B2B applications."},
                {"role": "user", "content": prompt}
            ]

            return await self._make_request(messages)
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return {"error": str(e)}

    async def analyze_market_trends(self, category: str = "B2B wholesale") -> Dict:
        """Analyze market trends and provide insights"""
        try:
            prompt = f"""As a market analyst for {category} apps, provide detailed trend analysis:

Analyze current trends in these sections:
1. User Acquisition Trends
2. Feature Preferences
3. Monetization Patterns
4. User Engagement
5. Competition Landscape
6. Growth Opportunities
7. Industry Challenges
8. Future Predictions

Format your response in clear sections with ### headers."""

            messages = [
                {"role": "system", "content": "You are an expert market analyst for B2B applications."},
                {"role": "user", "content": prompt}
            ]

            return await self._make_request(messages)
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {"error": str(e)}

    async def optimize_description(self, current_description: str, keywords: List[str]) -> Dict:
        """Optimize app description using AI analysis"""
        try:
            prompt = f"""As an ASO expert, optimize this B2B app description:

Current Description:
{current_description}

Target Keywords:
{', '.join(keywords)}

Provide optimization analysis in these sections:
1. Optimized Description
2. Key Improvements
3. Keyword Placement
4. Structure Recommendations
5. Call-to-action Suggestions
6. Readability Analysis
7. SEO Impact

Format your response in clear sections with ### headers."""

            messages = [
                {"role": "system", "content": "You are an expert ASO copywriter for B2B applications."},
                {"role": "user", "content": prompt}
            ]

            return await self._make_request(messages)
            
        except Exception as e:
            logger.error(f"Error optimizing description: {e}")
            return {"error": str(e)}