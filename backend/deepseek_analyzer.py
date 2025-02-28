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
                    "max_tokens": 2000,
                    "response_format": { "type": "json_object" }
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
                        try:
                            data = json.loads(response_text)
                            content = data['choices'][0]['message']['content']
                            
                            # Ensure content is valid JSON
                            if isinstance(content, str):
                                content = json.loads(content)
                            
                            return {
                                "analysis": content,
                                "format": "json"
                            }
                        except json.JSONDecodeError as e:
                            logger.error(f"Error parsing JSON response: {e}")
                            return {
                                "analysis": self._parse_markdown_response(content),
                                "format": "markdown"
                            }
                    else:
                        error_msg = f"Deepseek API error: {response_text}"
                        logger.error(error_msg)
                        return {
                            "error": error_msg,
                            "format": "error"
                        }
                        
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

    async def analyze_competitor_metadata(self, app_metadata: Dict, competitor_metadata: List[Dict]) -> Dict:
        """Analyze competitor metadata and provide insights"""
        try:
            prompt = f"""As an ASO expert for B2B and wholesale apps, analyze this competitive landscape and provide insights in this exact JSON format:
{{
    "competitive_analysis": {{
        "strengths": [
            "strength 1",
            "strength 2"
        ],
        "weaknesses": [
            "weakness 1",
            "weakness 2"
        ],
        "opportunities": [
            "opportunity 1",
            "opportunity 2"
        ],
        "threats": [
            "threat 1",
            "threat 2"
        ]
    }},
    "keyword_gaps": [
        {{
            "keyword": "missing keyword",
            "importance": "high",
            "competitor_usage": "common"
        }}
    ],
    "feature_gaps": [
        {{
            "feature": "missing feature",
            "priority": "high",
            "competitors": ["competitor1", "competitor2"]
        }}
    ],
    "recommendations": [
        "recommendation 1",
        "recommendation 2"
    ]
}}

Your App Metadata:
{json.dumps(app_metadata, indent=2)}

Competitor Metadata:
{json.dumps(competitor_metadata, indent=2)}

Focus on B2B wholesale domain best practices. Ensure the response is valid JSON."""

            messages = [
                {"role": "system", "content": "You are an expert ASO competitive analyst for B2B applications."},
                {"role": "user", "content": prompt}
            ]

            return await self._make_request(messages)
            
        except Exception as e:
            logger.error(f"Error analyzing competitor metadata: {e}")
            return {"error": str(e)}

    async def analyze_app_metadata(self, app_metadata: Dict, competitor_metadata: List[Dict]) -> Dict:
        """Analyze app metadata and provide ASO recommendations"""
        try:
            prompt = f"""As an ASO expert for B2B and wholesale apps, analyze this app metadata and provide recommendations in this exact JSON format:
{{
    "title_analysis": {{
        "current_score": 85,
        "suggestions": [
            "suggestion 1",
            "suggestion 2"
        ],
        "keywords_missing": [
            "keyword 1",
            "keyword 2"
        ]
    }},
    "description_analysis": {{
        "current_score": 75,
        "structure_issues": [
            "issue 1",
            "issue 2"
        ],
        "content_gaps": [
            "gap 1",
            "gap 2"
        ]
    }},
    "keyword_opportunities": [
        {{
            "keyword": "opportunity keyword",
            "relevance": 0.9,
            "competition": "medium",
            "priority": "high"
        }}
    ],
    "recommendations": [
        "recommendation 1",
        "recommendation 2"
    ]
}}

App Metadata:
{json.dumps(app_metadata, indent=2)}

Focus on B2B wholesale domain best practices. Ensure the response is valid JSON."""

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
            prompt = f"""As an ASO expert for {industry} apps, analyze this keyword and provide detailed suggestions in this exact JSON format:
{{
    "variations": [
        {{"keyword": "example variation", "relevance": 0.9, "competition": "high", "priority": "high"}},
        // more variations...
    ],
    "long_tail": [
        {{"keyword": "example long tail", "search_intent": "transactional", "opportunity": "high"}},
        // more long tail...
    ],
    "related_terms": [
        {{"term": "example term", "relevance": 0.8, "category": "business"}},
        // more terms...
    ],
    "recommendations": [
        "recommendation 1",
        "recommendation 2"
    ]
}}

Base Keyword: {base_keyword}

Focus on B2B and wholesale industry patterns. Ensure the response is valid JSON."""

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