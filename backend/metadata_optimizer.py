import logging
from typing import Dict, List, Optional
import json
import re

logger = logging.getLogger(__name__)

class MetadataOptimizer:
    def __init__(self, db_client, deepseek_analyzer):
        self.db = db_client
        self.deepseek = deepseek_analyzer

    async def optimize_app_title(self, app_id: str, target_keywords: List[str]) -> Dict:
        """Generate optimized app title variations"""
        try:
            app = await self.db.apps.find_one({"package_name": app_id})
            if not app:
                return {"error": "App not found"}

            current_title = app.get("metadata", {}).get("title", "")
            
            prompt = f"""As an ASO expert, generate optimized app title variations:

Current Title: {current_title}
Target Keywords: {', '.join(target_keywords)}
App Type: B2B Wholesale Platform

Requirements:
1. Max length: 50 characters
2. Include brand name
3. Include main keywords
4. Follow B2B best practices

Generate:
1. 5 title variations
2. Analysis of each variation
3. Keyword coverage
4. Brand visibility
5. Click-through potential
6. Best practices alignment

Format your response in clear sections with ### headers."""

            messages = [
                {"role": "system", "content": "You are an expert ASO title optimizer for B2B applications."},
                {"role": "user", "content": prompt}
            ]

            return await self.deepseek._make_request(messages)

        except Exception as e:
            logger.error(f"Error optimizing title: {e}")
            return {"error": str(e)}

    async def analyze_screenshot_impact(self, app_id: str) -> Dict:
        """Analyze screenshot effectiveness and suggest improvements"""
        try:
            app = await self.db.apps.find_one({"package_name": app_id})
            if not app:
                return {"error": "App not found"}

            screenshots = app.get("metadata", {}).get("screenshots", [])
            competitors = await self.db.apps.find({"is_competitor": True}).to_list(length=10)
            
            competitor_screenshots = {
                comp["package_name"]: comp.get("metadata", {}).get("screenshots", [])
                for comp in competitors
            }

            prompt = f"""As an ASO expert, analyze screenshot strategy and suggest improvements:

Current Screenshots: {json.dumps(screenshots, indent=2)}
Competitor Screenshots: {json.dumps(competitor_screenshots, indent=2)}
App Type: B2B Wholesale Platform

Analyze:
1. Screenshot quantity and coverage
2. Feature visualization
3. Competitive comparison
4. B2B best practices
5. Conversion optimization
6. Localization needs

Format your response in clear sections with ### headers."""

            messages = [
                {"role": "system", "content": "You are an expert ASO screenshot analyst for B2B applications."},
                {"role": "user", "content": prompt}
            ]

            return await self.deepseek._make_request(messages)

        except Exception as e:
            logger.error(f"Error analyzing screenshots: {e}")
            return {"error": str(e)}

    async def generate_feature_bullets(self, app_id: str, target_keywords: List[str]) -> Dict:
        """Generate optimized feature bullets for app description"""
        try:
            app = await self.db.apps.find_one({"package_name": app_id})
            if not app:
                return {"error": "App not found"}

            current_description = app.get("metadata", {}).get("full_description", "")
            
            prompt = f"""As an ASO expert, generate optimized feature bullets for this B2B app:

Current Description: {current_description}
Target Keywords: {', '.join(target_keywords)}
App Type: B2B Wholesale Platform

Generate:
1. 10 feature bullets
2. USP highlights
3. Benefit statements
4. Technical features
5. B2B specific points
6. Call-to-action suggestions

Format your response in clear sections with ### headers."""

            messages = [
                {"role": "system", "content": "You are an expert ASO content writer for B2B applications."},
                {"role": "user", "content": prompt}
            ]

            return await self.deepseek._make_request(messages)

        except Exception as e:
            logger.error(f"Error generating features: {e}")
            return {"error": str(e)}

    async def analyze_review_keywords(self, app_id: str) -> Dict:
        """Analyze keywords from user reviews for ASO insights"""
        try:
            # Get app reviews (assuming we have a reviews collection)
            reviews = await self.db.reviews.find({
                "app_id": app_id
            }).sort("date", -1).to_list(length=1000)

            review_texts = [review.get("text", "") for review in reviews]
            
            prompt = f"""As an ASO expert, analyze these user reviews for keyword insights:

Review Texts:
{json.dumps(review_texts[:50], indent=2)}  # Analyze first 50 reviews

Analyze:
1. Common keywords and phrases
2. Sentiment patterns
3. Feature mentions
4. User pain points
5. Competitive mentions
6. ASO opportunities

Format your response in clear sections with ### headers."""

            messages = [
                {"role": "system", "content": "You are an expert ASO review analyst for B2B applications."},
                {"role": "user", "content": prompt}
            ]

            return await self.deepseek._make_request(messages)

        except Exception as e:
            logger.error(f"Error analyzing reviews: {e}")
            return {"error": str(e)}