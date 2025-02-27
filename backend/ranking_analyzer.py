import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class RankingAnalyzer:
    def __init__(self, db_client, deepseek_analyzer):
        self.db = db_client
        self.deepseek = deepseek_analyzer

    async def analyze_ranking_changes(self, app_id: str, days: int = 30) -> Dict:
        """Analyze ranking changes and get AI insights"""
        try:
            # Get historical rankings
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            rankings = await self.db.rankings.find({
                "app_id": app_id,
                "date": {"$gte": cutoff_date}
            }).sort("date", -1).to_list(length=1000)

            # Prepare data for AI analysis
            ranking_data = self._prepare_ranking_data(rankings)

            # Get AI insights
            prompt = f"""As an ASO expert, analyze these ranking changes and provide strategic insights:

Ranking Data:
{json.dumps(ranking_data, indent=2)}

Analyze:
1. Significant changes in rankings
2. Patterns in keyword performance
3. Competitive positioning
4. Opportunities for improvement
5. Risk factors
6. Actionable recommendations

Format your response in clear sections with ### headers."""

            messages = [
                {"role": "system", "content": "You are an expert ASO analyst specializing in B2B applications."},
                {"role": "user", "content": prompt}
            ]

            return await self.deepseek._make_request(messages)

        except Exception as e:
            logger.error(f"Error analyzing ranking changes: {e}")
            return {"error": str(e)}

    def _prepare_ranking_data(self, rankings: List[Dict]) -> Dict:
        """Prepare ranking data for analysis"""
        data = {}
        for rank in rankings:
            keyword = rank["keyword"]
            if keyword not in data:
                data[keyword] = {
                    "rankings": [],
                    "avg_rank": 0,
                    "best_rank": float('inf'),
                    "worst_rank": 0,
                    "volatility": 0
                }
            
            data[keyword]["rankings"].append({
                "date": rank["date"].isoformat(),
                "rank": rank["rank"]
            })
            
            # Update statistics
            ranks = [r["rank"] for r in data[keyword]["rankings"]]
            data[keyword]["avg_rank"] = sum(ranks) / len(ranks)
            data[keyword]["best_rank"] = min(ranks)
            data[keyword]["worst_rank"] = max(ranks)
            data[keyword]["volatility"] = max(ranks) - min(ranks)

        return data

    async def analyze_competitor_impact(self, app_id: str, competitor_ids: List[str]) -> Dict:
        """Analyze how competitor actions impact rankings"""
        try:
            # Get app and competitor rankings
            app_rankings = await self.db.rankings.find({
                "app_id": app_id
            }).sort("date", -1).to_list(length=1000)

            competitor_rankings = await self.db.rankings.find({
                "app_id": {"$in": competitor_ids}
            }).sort("date", -1).to_list(length=1000)

            # Prepare data for analysis
            impact_data = self._prepare_impact_data(app_rankings, competitor_rankings)

            # Get AI insights
            prompt = f"""As an ASO expert, analyze how competitor actions impact this app's rankings:

Impact Data:
{json.dumps(impact_data, indent=2)}

Analyze:
1. Direct ranking correlations
2. Keyword battlegrounds
3. Competitive advantages/disadvantages
4. Market share analysis
5. Strategic opportunities
6. Defense recommendations

Format your response in clear sections with ### headers."""

            messages = [
                {"role": "system", "content": "You are an expert ASO competitive analyst for B2B applications."},
                {"role": "user", "content": prompt}
            ]

            return await self.deepseek._make_request(messages)

        except Exception as e:
            logger.error(f"Error analyzing competitor impact: {e}")
            return {"error": str(e)}

    def _prepare_impact_data(self, app_rankings: List[Dict], competitor_rankings: List[Dict]) -> Dict:
        """Prepare competitor impact data for analysis"""
        data = {}
        
        # Group rankings by keyword
        for rank in app_rankings + competitor_rankings:
            keyword = rank["keyword"]
            if keyword not in data:
                data[keyword] = {
                    "app_rankings": [],
                    "competitor_rankings": {},
                    "correlation": {}
                }
            
            if rank["app_id"] == app_rankings[0]["app_id"]:
                data[keyword]["app_rankings"].append({
                    "date": rank["date"].isoformat(),
                    "rank": rank["rank"]
                })
            else:
                if rank["app_id"] not in data[keyword]["competitor_rankings"]:
                    data[keyword]["competitor_rankings"][rank["app_id"]] = []
                data[keyword]["competitor_rankings"][rank["app_id"]].append({
                    "date": rank["date"].isoformat(),
                    "rank": rank["rank"]
                })

        # Calculate correlations
        for keyword in data:
            app_ranks = [r["rank"] for r in data[keyword]["app_rankings"]]
            for comp_id, comp_ranks in data[keyword]["competitor_rankings"].items():
                comp_ranks_list = [r["rank"] for r in comp_ranks]
                if len(app_ranks) == len(comp_ranks_list):
                    correlation = self._calculate_correlation(app_ranks, comp_ranks_list)
                    data[keyword]["correlation"][comp_id] = correlation

        return data

    def _calculate_correlation(self, ranks1: List[int], ranks2: List[int]) -> float:
        """Calculate correlation between two ranking series"""
        try:
            n = len(ranks1)
            if n != len(ranks2) or n < 2:
                return 0
            
            mean1 = sum(ranks1) / n
            mean2 = sum(ranks2) / n
            
            dev1 = [x - mean1 for x in ranks1]
            dev2 = [x - mean2 for x in ranks2]
            
            dev_prod = sum(x * y for x, y in zip(dev1, dev2))
            dev1_sq = sum(x * x for x in dev1)
            dev2_sq = sum(x * x for x in dev2)
            
            if dev1_sq == 0 or dev2_sq == 0:
                return 0
                
            return dev_prod / (dev1_sq * dev2_sq) ** 0.5
            
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return 0

    async def predict_ranking_trends(self, app_id: str, keyword: str) -> Dict:
        """Predict future ranking trends using historical data and AI analysis"""
        try:
            # Get historical rankings
            rankings = await self.db.rankings.find({
                "app_id": app_id,
                "keyword": keyword
            }).sort("date", -1).to_list(length=100)

            # Prepare trend data
            trend_data = self._prepare_trend_data(rankings)

            # Get AI predictions
            prompt = f"""As an ASO expert, analyze these ranking trends and predict future performance:

Trend Data:
{json.dumps(trend_data, indent=2)}

Provide:
1. Short-term predictions (7 days)
2. Long-term predictions (30 days)
3. Influencing factors
4. Risk assessment
5. Optimization opportunities
6. Strategic recommendations

Format your response in clear sections with ### headers."""

            messages = [
                {"role": "system", "content": "You are an expert ASO trend analyst for B2B applications."},
                {"role": "user", "content": prompt}
            ]

            return await self.deepseek._make_request(messages)

        except Exception as e:
            logger.error(f"Error predicting trends: {e}")
            return {"error": str(e)}

    def _prepare_trend_data(self, rankings: List[Dict]) -> Dict:
        """Prepare trend data for analysis"""
        data = {
            "daily_rankings": [],
            "weekly_averages": [],
            "trends": {
                "short_term": "",
                "long_term": "",
                "volatility": 0
            }
        }

        if not rankings:
            return data

        # Sort rankings by date
        rankings.sort(key=lambda x: x["date"])

        # Calculate daily rankings
        for rank in rankings:
            data["daily_rankings"].append({
                "date": rank["date"].isoformat(),
                "rank": rank["rank"]
            })

        # Calculate weekly averages
        current_week = []
        current_date = rankings[0]["date"]
        for rank in rankings:
            if (rank["date"] - current_date).days <= 7:
                current_week.append(rank["rank"])
            else:
                if current_week:
                    avg = sum(current_week) / len(current_week)
                    data["weekly_averages"].append({
                        "week": current_date.isoformat(),
                        "avg_rank": avg
                    })
                current_week = [rank["rank"]]
                current_date = rank["date"]

        # Add last week if exists
        if current_week:
            avg = sum(current_week) / len(current_week)
            data["weekly_averages"].append({
                "week": current_date.isoformat(),
                "avg_rank": avg
            })

        # Calculate trends
        ranks = [r["rank"] for r in rankings]
        if len(ranks) >= 7:
            short_term_change = ranks[-1] - ranks[-7]
            data["trends"]["short_term"] = "improving" if short_term_change < 0 else "declining" if short_term_change > 0 else "stable"

        if len(ranks) >= 30:
            long_term_change = ranks[-1] - ranks[-30]
            data["trends"]["long_term"] = "improving" if long_term_change < 0 else "declining" if long_term_change > 0 else "stable"

        data["trends"]["volatility"] = max(ranks) - min(ranks)

        return data