import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
from collections import Counter
import json

logger = logging.getLogger(__name__)

class ASOAnalyzer:
    def __init__(self, db_client):
        self.db = db_client
        
    async def analyze_keyword_opportunity(self, keyword_data: Dict) -> Dict:
        """
        Analyze keyword opportunity based on various metrics
        """
        try:
            volume_score = keyword_data.get('search_volume_score', 0)
            difficulty_score = keyword_data.get('difficulty_score', 0)
            current_rank = keyword_data.get('current_rank')
            
            # Calculate opportunity score
            opportunity_score = 0
            if volume_score and difficulty_score:
                # Higher volume and lower difficulty = better opportunity
                opportunity_score = (volume_score * 0.7) - (difficulty_score * 0.3)
            
            # Determine priority
            priority = "low"
            if opportunity_score > 70:
                priority = "high"
            elif opportunity_score > 40:
                priority = "medium"
            
            # Generate recommendation
            recommendation = ""
            if current_rank is None:
                recommendation = "New keyword opportunity - consider adding to metadata"
            elif current_rank > 10:
                recommendation = "Optimize metadata to improve ranking"
            elif current_rank <= 10:
                recommendation = "Maintain current optimization strategy"
            
            return {
                "opportunity_score": opportunity_score,
                "priority": priority,
                "recommendation": recommendation
            }
        except Exception as e:
            logger.error(f"Error analyzing keyword opportunity: {e}")
            return {
                "opportunity_score": 0,
                "priority": "low",
                "recommendation": "Error analyzing keyword"
            }

    async def analyze_competitor_metadata(self, app_metadata: Dict, competitor_metadata: Dict) -> Dict:
        """
        Analyze differences in metadata between app and competitor
        """
        try:
            differences = {}
            
            # Analyze title
            app_title_words = set(app_metadata.get('title', '').lower().split())
            comp_title_words = set(competitor_metadata.get('title', '').lower().split())
            unique_comp_words = comp_title_words - app_title_words
            if unique_comp_words:
                differences['title'] = {
                    'missing_keywords': list(unique_comp_words),
                    'recommendation': 'Consider adding these keywords to title'
                }
            
            # Analyze description
            app_desc = app_metadata.get('full_description', '').lower()
            comp_desc = competitor_metadata.get('full_description', '').lower()
            
            # Extract key phrases (simplified version)
            def extract_phrases(text: str) -> List[str]:
                words = text.split()
                return [' '.join(words[i:i+3]) for i in range(len(words)-2)]
            
            app_phrases = set(extract_phrases(app_desc))
            comp_phrases = set(extract_phrases(comp_desc))
            unique_phrases = comp_phrases - app_phrases
            
            if unique_phrases:
                differences['description'] = {
                    'missing_phrases': list(unique_phrases)[:5],  # Top 5 phrases
                    'recommendation': 'Consider incorporating these phrases'
                }
            
            return differences
        except Exception as e:
            logger.error(f"Error analyzing competitor metadata: {e}")
            return {"error": str(e)}

    async def generate_aso_recommendations(self, app_id: str) -> List[Dict]:
        """
        Generate ASO recommendations based on analysis
        """
        try:
            recommendations = []
            
            # Get app data
            app_data = await self.db.apps.find_one({"_id": app_id})
            if not app_data:
                return recommendations
            
            # Analyze title
            title = app_data.get('metadata', {}).get('title', '')
            if len(title) < 50:  # Play Store title limit
                recommendations.append({
                    "category": "title",
                    "current_value": title,
                    "suggested_value": "Add more relevant keywords",
                    "impact_score": 90,
                    "reasoning": "Title not using maximum allowed length",
                    "implementation_difficulty": "easy"
                })
            
            # Analyze description
            description = app_data.get('metadata', {}).get('full_description', '')
            if len(description) < 3000:  # Recommended minimum
                recommendations.append({
                    "category": "description",
                    "current_value": "Current description length: " + str(len(description)),
                    "suggested_value": "Expand description with features and keywords",
                    "impact_score": 85,
                    "reasoning": "Description length below recommended minimum",
                    "implementation_difficulty": "medium"
                })
            
            # Analyze screenshots
            screenshots = app_data.get('metadata', {}).get('screenshots', [])
            if len(screenshots) < 8:
                recommendations.append({
                    "category": "screenshots",
                    "current_value": f"Current screenshots: {len(screenshots)}",
                    "suggested_value": "Add more screenshots showcasing features",
                    "impact_score": 75,
                    "reasoning": "More screenshots can improve conversion",
                    "implementation_difficulty": "medium"
                })
            
            return recommendations
        except Exception as e:
            logger.error(f"Error generating ASO recommendations: {e}")
            return []

    async def analyze_b2b_specific_metrics(self, app_id: str) -> Dict:
        """
        Analyze B2B-specific ASO metrics
        """
        try:
            b2b_keywords = [
                "wholesale", "b2b", "business", "supplier", "distributor",
                "bulk", "trade", "manufacturer", "inventory", "procurement",
                "supply chain", "vendor", "enterprise", "commercial", "industrial"
            ]
            
            analysis = {
                "keyword_coverage": {},
                "competitor_comparison": {},
                "opportunities": []
            }
            
            # Analyze keyword coverage
            app_data = await self.db.apps.find_one({"_id": app_id})
            if app_data:
                metadata = app_data.get('metadata', {})
                title = metadata.get('title', '').lower()
                description = metadata.get('full_description', '').lower()
                
                for keyword in b2b_keywords:
                    in_title = keyword in title
                    in_description = keyword in description
                    analysis["keyword_coverage"][keyword] = {
                        "in_title": in_title,
                        "in_description": in_description,
                        "recommendation": "Add to title" if not in_title else "Optimize placement"
                    }
            
            # Get competitor rankings for these keywords
            competitor_rankings = await self.db.rankings.find({
                "keyword": {"$in": b2b_keywords}
            }).to_list(length=100)
            
            if competitor_rankings:
                for keyword in b2b_keywords:
                    keyword_ranks = [r for r in competitor_rankings if r["keyword"] == keyword]
                    if keyword_ranks:
                        analysis["competitor_comparison"][keyword] = {
                            "avg_rank": sum(r["rank"] for r in keyword_ranks) / len(keyword_ranks),
                            "best_rank": min(r["rank"] for r in keyword_ranks),
                            "opportunity_score": self._calculate_opportunity_score(keyword_ranks)
                        }
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing B2B metrics: {e}")
            return {"error": str(e)}

    def _calculate_opportunity_score(self, keyword_ranks: List[Dict]) -> float:
        """
        Calculate opportunity score based on ranking distribution
        """
        try:
            if not keyword_ranks:
                return 0.0
            
            best_rank = min(r["rank"] for r in keyword_ranks)
            avg_rank = sum(r["rank"] for r in keyword_ranks) / len(keyword_ranks)
            
            # Higher score if there's more variation in rankings (opportunity to compete)
            rank_variation = max(r["rank"] for r in keyword_ranks) - best_rank
            
            # Score formula: 100 - (avg_rank * 0.5) + (rank_variation * 0.3)
            # This favors keywords where:
            # - Best rank is good (high potential)
            # - There's variation in rankings (possible to compete)
            score = 100 - (avg_rank * 0.5) + (rank_variation * 0.3)
            return max(0, min(100, score))  # Clamp between 0-100
        except Exception as e:
            logger.error(f"Error calculating opportunity score: {e}")
            return 0.0