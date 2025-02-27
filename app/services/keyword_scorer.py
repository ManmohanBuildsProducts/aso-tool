from typing import List, Dict, Any
from google_play_scraper import search
import math
import logging
from collections import defaultdict
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class KeywordScorer:
    def __init__(self):
        self.keyword_cache = {}
        self.cache_timeout = timedelta(hours=24)

    async def calculate_keyword_difficulty(self, keyword: str, country: str = 'us') -> Dict[str, Any]:
        """
        Calculate keyword difficulty score based on:
        - Competition (number of apps)
        - Average rating of top apps
        - Average installs of top apps
        """
        cache_key = f"{keyword}_{country}"
        if cache_key in self.keyword_cache:
            cached_result = self.keyword_cache[cache_key]
            if datetime.now() - cached_result['timestamp'] < self.cache_timeout:
                return cached_result['data']

        try:
            # Search for apps using the keyword
            search_results = search(
                keyword,
                country=country,
                n_hits=20  # Get top 20 apps
            )

            if not search_results:
                return {
                    "difficulty_score": 0,
                    "competition_level": "Low",
                    "search_volume": "Low",
                    "ranking_potential": "High"
                }

            # Calculate metrics
            avg_rating = sum(app.get('score', 0) for app in search_results) / len(search_results)
            avg_installs = sum(app.get('minInstalls', 0) for app in search_results) / len(search_results)
            
            # Calculate difficulty score (0-100)
            competition_score = min(len(search_results) / 20, 1) * 40  # 40% weight
            rating_score = (avg_rating / 5) * 30  # 30% weight
            install_score = min(avg_installs / 10000000, 1) * 30  # 30% weight
            
            difficulty_score = competition_score + rating_score + install_score

            # Determine competition level
            competition_level = self._get_competition_level(difficulty_score)
            
            # Estimate search volume based on top app installs
            search_volume = self._estimate_search_volume(avg_installs)
            
            # Calculate ranking potential (inverse of difficulty)
            ranking_potential = self._calculate_ranking_potential(difficulty_score)

            result = {
                "difficulty_score": round(difficulty_score, 2),
                "competition_level": competition_level,
                "search_volume": search_volume,
                "ranking_potential": ranking_potential,
                "metrics": {
                    "avg_rating": round(avg_rating, 2),
                    "avg_installs": int(avg_installs),
                    "competing_apps": len(search_results)
                }
            }

            # Cache the result
            self.keyword_cache[cache_key] = {
                'timestamp': datetime.now(),
                'data': result
            }

            return result

        except Exception as e:
            logger.error(f"Error calculating keyword difficulty for {keyword}: {str(e)}")
            return {
                "error": f"Failed to calculate keyword difficulty: {str(e)}"
            }

    def _get_competition_level(self, score: float) -> str:
        if score < 30:
            return "Very Low"
        elif score < 50:
            return "Low"
        elif score < 70:
            return "Medium"
        elif score < 85:
            return "High"
        else:
            return "Very High"

    def _estimate_search_volume(self, avg_installs: float) -> str:
        if avg_installs < 1000:
            return "Very Low"
        elif avg_installs < 10000:
            return "Low"
        elif avg_installs < 100000:
            return "Medium"
        elif avg_installs < 1000000:
            return "High"
        else:
            return "Very High"

    def _calculate_ranking_potential(self, difficulty_score: float) -> str:
        potential_score = 100 - difficulty_score
        if potential_score < 20:
            return "Very Low"
        elif potential_score < 40:
            return "Low"
        elif potential_score < 60:
            return "Medium"
        elif potential_score < 80:
            return "High"
        else:
            return "Very High"

    async def analyze_keyword_trends(self, keywords: List[str], country: str = 'us') -> Dict[str, Any]:
        """
        Analyze trends for multiple keywords
        """
        results = {}
        for keyword in keywords:
            try:
                difficulty = await self.calculate_keyword_difficulty(keyword, country)
                results[keyword] = difficulty
            except Exception as e:
                logger.error(f"Error analyzing trend for keyword {keyword}: {str(e)}")
                continue
        
        return {
            "timestamp": datetime.now().isoformat(),
            "country": country,
            "keyword_trends": results
        }