import aiohttp
import json
import logging
import os
from typing import Dict, List, Optional
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from utils.key_manager import decrypt_api_key

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DeepseekAnalyzer:
    def __init__(self):
        """Initialize DeepSeek analyzer with encrypted API key"""
        encrypted_key = os.environ.get('DEEPSEEK_API_KEY_ENCRYPTED')
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        
        if not encrypted_key or not encryption_key:
            raise ValueError("DeepSeek API key encryption settings not found in environment")
            
        self.api_key = decrypt_api_key(encrypted_key, encryption_key.encode())
        if not self.api_key:
            raise ValueError("Failed to decrypt DeepSeek API key")
            
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
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
                
                logger.info("Making request to Deepseek API")
                
                async with session.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_text = await response.text()
                    logger.info(f"Deepseek API status code: {response.status}")
                    
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
                                "analysis": self._parse_markdown_response(response_text),
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
            
            return sections
            
        except Exception as e:
            logger.error(f"Error parsing markdown: {e}")
            return {"error": "Failed to parse response"}

    async def analyze_app_metadata(self, app_metadata: Dict, competitor_metadata: List[Dict] = None) -> Dict:
        """Analyze app metadata and provide ASO recommendations"""
        if not competitor_metadata:
            competitor_metadata = []
            
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

    async def analyze_competitor_metadata(self, app_metadata: Dict, competitor_metadata: List[Dict] = None) -> Dict:
        """Analyze competitor metadata and provide insights"""
        if not competitor_metadata:
            competitor_metadata = []
            
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
            prompt = f"""As a market analyst for {category} apps, provide detailed trend analysis in this exact JSON format:
{{
    "market_trends": [
        {{
            "trend": "trend description",
            "impact": "high/medium/low",
            "timeframe": "short/medium/long term"
        }}
    ],
    "user_preferences": [
        {{
            "feature": "feature name",
            "importance": "high/medium/low",
            "adoption_rate": "percentage"
        }}
    ],
    "monetization_insights": [
        {{
            "strategy": "strategy name",
            "effectiveness": "high/medium/low",
            "market_share": "percentage"
        }}
    ],
    "recommendations": [
        "recommendation 1",
        "recommendation 2"
    ]
}}

Focus on B2B and wholesale industry patterns. Ensure the response is valid JSON."""

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
            prompt = f"""As an ASO expert, optimize this B2B app description in this exact JSON format:
{{
    "optimized_description": "full optimized description here",
    "improvements": [
        {{
            "type": "keyword placement/readability/structure",
            "change": "what was changed",
            "impact": "expected impact"
        }}
    ],
    "keyword_usage": [
        {{
            "keyword": "used keyword",
            "count": 2,
            "placement": "title/first_paragraph/body"
        }}
    ],
    "recommendations": [
        "recommendation 1",
        "recommendation 2"
    ]
}}

Current Description:
{current_description}

Target Keywords:
{', '.join(keywords)}

Focus on B2B wholesale domain best practices. Ensure the response is valid JSON."""

            messages = [
                {"role": "system", "content": "You are an expert ASO copywriter for B2B applications."},
                {"role": "user", "content": prompt}
            ]

            return await self._make_request(messages)
            
        except Exception as e:
            logger.error(f"Error optimizing description: {e}")
            return {"error": str(e)}