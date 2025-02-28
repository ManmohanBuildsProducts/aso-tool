import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
from collections import Counter
import json
import re

logger = logging.getLogger(__name__)

class KeywordAnalyzer:
    def __init__(self, db_client):
        self.db = db_client
        self.keyword_categories = {
            "business_model": [
                "b2b", "wholesale", "bulk", "distributor", "manufacturer direct",
                "business wholesale", "trade", "reseller", "stockist"
            ],
            "product_categories": [
                "fmcg", "grocery", "fashion", "electronics", "home appliances",
                "kitchenware", "stationery", "personal care", "food and beverages"
            ],
            "business_type": [
                "kirana store", "retail shop", "small business", "medium business",
                "distributor business", "wholesale business", "retail business"
            ],
            "features": [
                "order online", "bulk order", "wholesale price", "business price",
                "direct supply", "doorstep delivery", "easy returns", "credit facility"
            ],
            "location": [
                "near me", "local", "city", "state", "nationwide",
                "pan india", "regional", "zone"
            ],
            "benefits": [
                "best price", "lowest price", "direct price", "factory price",
                "bulk discount", "wholesale margin", "business savings"
            ],
            "trust_factors": [
                "verified", "trusted", "authorized", "genuine", "reliable",
                "top rated", "recommended", "certified"
            ],
            "business_processes": [
                "inventory management", "supply chain", "procurement", "ordering system",
                "stock management", "payment terms", "credit period"
            ]
        }
        
    async def get_keyword_suggestions(self, base_keyword: str) -> List[Dict]:
        """Generate keyword suggestions based on a base keyword"""
        try:
            suggestions = []
            base_words = set(base_keyword.lower().split())
            
            # Find relevant categories
            relevant_categories = []
            for category, keywords in self.keyword_categories.items():
                for kw in keywords:
                    if any(word in kw for word in base_words):
                        relevant_categories.append(category)
                        break
            
            # Generate suggestions from relevant categories
            for category in relevant_categories:
                for keyword in self.keyword_categories[category]:
                    # Skip exact matches
                    if keyword == base_keyword:
                        continue
                        
                    # Calculate relevance score
                    relevance = self._calculate_relevance(base_keyword, keyword)
                    if relevance > 0.3:  # Threshold for relevance
                        suggestions.append({
                            "keyword": keyword,
                            "category": category,
                            "relevance_score": relevance,
                            "source": "category_match"
                        })
            
            # Generate combinations
            for category in relevant_categories:
                combinations = self._generate_keyword_combinations(
                    base_keyword,
                    self.keyword_categories[category]
                )
                suggestions.extend(combinations)
            
            # Sort by relevance
            suggestions.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # Add competition and trend data
            await self._enrich_keyword_data(suggestions)
            
            return suggestions[:50]  # Return top 50 suggestions
            
        except Exception as e:
            logger.error(f"Error generating keyword suggestions: {e}")
            return []
    
    def _calculate_relevance(self, base_keyword: str, suggestion: str) -> float:
        """Calculate relevance score between base keyword and suggestion"""
        try:
            base_words = set(base_keyword.lower().split())
            suggestion_words = set(suggestion.lower().split())
            
            # Calculate word overlap
            common_words = base_words.intersection(suggestion_words)
            total_words = base_words.union(suggestion_words)
            
            # Basic Jaccard similarity
            similarity = len(common_words) / len(total_words)
            
            # Adjust score based on length difference
            length_penalty = 1 - (abs(len(base_keyword) - len(suggestion)) / max(len(base_keyword), len(suggestion)))
            
            # Adjust score based on word order for exact phrases
            order_score = 1.0
            if len(common_words) > 1:
                base_order = [w for w in base_keyword.lower().split() if w in common_words]
                sugg_order = [w for w in suggestion.lower().split() if w in common_words]
                if base_order != sugg_order:
                    order_score = 0.8
            
            return (similarity * 0.5 + length_penalty * 0.3 + order_score * 0.2)
            
        except Exception as e:
            logger.error(f"Error calculating relevance: {e}")
            return 0.0
    
    def _generate_keyword_combinations(self, base_keyword: str, category_keywords: List[str]) -> List[Dict]:
        """Generate meaningful keyword combinations"""
        try:
            combinations = []
            base_words = base_keyword.lower().split()
            
            for keyword in category_keywords:
                kw_words = keyword.lower().split()
                
                # Combine with base keyword
                for i in range(len(base_words)):
                    for j in range(len(kw_words)):
                        combination = " ".join(base_words[:i+1] + kw_words[j:])
                        if combination != base_keyword and combination != keyword:
                            relevance = self._calculate_relevance(base_keyword, combination)
                            if relevance > 0.4:  # Higher threshold for combinations
                                combinations.append({
                                    "keyword": combination,
                                    "category": "combination",
                                    "relevance_score": relevance,
                                    "source": "combination"
                                })
            
            return combinations
            
        except Exception as e:
            logger.error(f"Error generating combinations: {e}")
            return []
    
    async def _enrich_keyword_data(self, keywords: List[Dict]) -> None:
        """Add competition and trend data to keywords"""
        try:
            # Get historical ranking data
            all_keywords = [k["keyword"] for k in keywords]
            rankings = await self.db.rankings.find({
                "keyword": {"$in": all_keywords}
            }).to_list(length=1000)
            
            # Group rankings by keyword
            keyword_rankings = {}
            for rank in rankings:
                kw = rank["keyword"]
                if kw not in keyword_rankings:
                    keyword_rankings[kw] = []
                keyword_rankings[kw].append(rank["rank"])
            
            # Calculate competition scores
            for keyword in keywords:
                kw = keyword["keyword"]
                ranks = keyword_rankings.get(kw, [])
                
                if ranks:
                    # Calculate competition score
                    avg_rank = sum(ranks) / len(ranks)
                    rank_volatility = max(ranks) - min(ranks) if len(ranks) > 1 else 0
                    
                    keyword["competition_score"] = min(100, max(0, (
                        (100 - avg_rank * 2) * 0.7 +  # Lower rank = higher score
                        (rank_volatility * 2) * 0.3    # Higher volatility = higher score
                    )))
                    
                    # Add trend
                    keyword["trend"] = self._calculate_trend(ranks)
                else:
                    keyword["competition_score"] = 50  # Default score
                    keyword["trend"] = "stable"
                    
        except Exception as e:
            logger.error(f"Error enriching keyword data: {e}")
    
    def _calculate_trend(self, ranks: List[int]) -> str:
        """Calculate trend from ranking history"""
        try:
            if len(ranks) < 2:
                return "stable"
            
            # Calculate average rank change
            changes = [ranks[i] - ranks[i-1] for i in range(1, len(ranks))]
            avg_change = sum(changes) / len(changes)
            
            if avg_change < -2:
                return "strongly_improving"
            elif avg_change < -0.5:
                return "improving"
            elif avg_change > 2:
                return "strongly_declining"
            elif avg_change > 0.5:
                return "declining"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return "stable"