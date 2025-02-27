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

    async def _make_request(self, messages: List[Dict]) -> Optional[str]:
        """Make a request to Deepseek API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=self.headers,
                    json={
                        "model": "deepseek-chat",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        error_text = await response.text()
                        logger.error(f"Deepseek API error: {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error making Deepseek request: {e}")
            return None

    async def analyze_app_metadata(self, app_metadata: Dict, competitor_metadata: List[Dict]) -> Dict:
        """Analyze app metadata and provide ASO recommendations"""
        try:
            prompt = f"""As an ASO expert for B2B and wholesale apps, analyze this app metadata and provide detailed recommendations:

App Metadata:
{json.dumps(app_metadata, indent=2)}

Competitor Metadata:
{json.dumps(competitor_metadata, indent=2)}

Provide analysis in JSON format with these sections:
1. Title optimization
2. Description improvements
3. Keyword opportunities
4. Competitive advantages
5. Feature recommendations
6. Category-specific suggestions
7. Priority actions

Focus on B2B wholesale domain best practices."""

            messages = [
                {"role": "system", "content": "You are an expert ASO analyst specializing in B2B and wholesale applications."},
                {"role": "user", "content": prompt}
            ]

            response = await self._make_request(messages)
            if response:
                return json.loads(response)
            return {"error": "Failed to get analysis"}

        except Exception as e:
            logger.error(f"Error analyzing metadata: {e}")
            return {"error": str(e)}

    async def generate_keyword_suggestions(self, base_keyword: str, industry: str = "B2B wholesale") -> Dict:
        """Generate keyword suggestions using AI analysis"""
        try:
            prompt = f"""As an ASO expert for {industry} apps, analyze this keyword and provide detailed suggestions:

Base Keyword: {base_keyword}

Provide analysis in JSON format with:
1. High-impact variations
2. Long-tail opportunities
3. Related business terms
4. Industry-specific combinations
5. Feature-based variations
6. Search intent analysis
7. Competition level estimates
8. Priority recommendations

Focus on B2B and wholesale industry patterns."""

            messages = [
                {"role": "system", "content": "You are an expert ASO keyword analyst for B2B applications."},
                {"role": "user", "content": prompt}
            ]

            response = await self._make_request(messages)
            if response:
                return json.loads(response)
            return {"error": "Failed to get suggestions"}

        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return {"error": str(e)}

    async def analyze_market_trends(self, category: str = "B2B wholesale") -> Dict:
        """Analyze market trends and provide insights"""
        try:
            prompt = f"""As a market analyst for {category} apps, provide detailed trend analysis:

Analyze current trends in:
1. User acquisition
2. Feature preferences
3. Monetization patterns
4. User engagement
5. Competition landscape
6. Growth opportunities

Provide analysis in JSON format with actionable insights."""

            messages = [
                {"role": "system", "content": "You are an expert market analyst for B2B applications."},
                {"role": "user", "content": prompt}
            ]

            response = await self._make_request(messages)
            if response:
                return json.loads(response)
            return {"error": "Failed to get trends"}

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

Provide in JSON format:
1. Optimized description
2. Key improvements
3. Keyword placement
4. Structure recommendations
5. Call-to-action suggestions

Focus on B2B wholesale best practices."""

            messages = [
                {"role": "system", "content": "You are an expert ASO copywriter for B2B applications."},
                {"role": "user", "content": prompt}
            ]

            response = await self._make_request(messages)
            if response:
                return json.loads(response)
            return {"error": "Failed to optimize description"}

        except Exception as e:
            logger.error(f"Error optimizing description: {e}")
            return {"error": str(e)}