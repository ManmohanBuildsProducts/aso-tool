from typing import List, Dict, Any, Optional
from services.app_scraper import AppScraper
from services.keyword_analyzer import KeywordAnalyzer
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CompetitorAnalyzer:
    def __init__(self):
        self.app_scraper = AppScraper()
        self.keyword_analyzer = KeywordAnalyzer()

    async def analyze_competitors(self, app_id: str, competitor_ids: List[str]) -> Dict[str, Any]:
        """
        Perform comprehensive competitor analysis with improved error handling
        """
        try:
            # Get main app details with validation
            main_app = await self._get_app_details_safely(app_id)
            if not main_app:
                return self._get_error_response(f"Failed to fetch main app details for {app_id}")
            
            # Get competitor details with validation
            competitor_details = []
            for comp_id in competitor_ids:
                try:
                    comp_details = await self._get_app_details_safely(comp_id)
                    if comp_details:
                        competitor_details.append(comp_details)
                except Exception as e:
                    logger.warning(f"Error fetching competitor {comp_id}: {str(e)}")
                    continue
            
            # Perform analysis even if some competitors failed
            metrics_comparison = self._compare_metrics(main_app, competitor_details)
            
            return {
                "status": "success",
                "main_app": {
                    "app_id": app_id,
                    "details": main_app,
                    "metrics": self._calculate_app_metrics(main_app)
                },
                "competitors": [
                    {
                        "app_id": comp["appId"],
                        "details": comp,
                        "metrics": self._calculate_app_metrics(comp),
                        "comparison": self._compare_with_main_app(main_app, comp)
                    }
                    for comp in competitor_details
                ],
                "market_analysis": self._analyze_market_position(main_app, competitor_details),
                "metrics_comparison": metrics_comparison,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing competitors: {str(e)}")
            return self._get_error_response(str(e))

    def _get_error_response(self, message: str) -> Dict[str, Any]:
        """Return a standardized error response"""
        return {
            "status": "error",
            "message": message,
            "main_app": None,
            "competitors": [],
            "market_analysis": self._get_default_market_analysis(),
            "metrics_comparison": self._get_default_metrics(),
            "analyzed_at": datetime.now().isoformat()
        }

    async def _get_app_details_safely(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Safely fetch app details with validation and default values
        """
        try:
            details = await self.app_scraper.get_app_details(app_id)
            if not details:
                return None

            # Ensure critical fields have default values
            return {
                **details,
                "score": float(details.get("score", 0) or 0),
                "ratings": int(details.get("ratings", 0) or 0),
                "reviews": int(details.get("reviews", 0) or 0),
                "minInstalls": int(details.get("minInstalls", 0) or 0),
                "maxInstalls": int(details.get("maxInstalls", 0) or details.get("minInstalls", 0) or 0),
                "analyzed_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching app details for {app_id}: {str(e)}")
            return None

    def _calculate_app_metrics(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key metrics for an app"""
        try:
            reviews = int(app_data.get("reviews", 0) or 0)
            installs = int(app_data.get("minInstalls", 0) or 0)
            ratings = int(app_data.get("ratings", 0) or 0)
            score = float(app_data.get("score", 0) or 0)
            
            metrics = {
                "rating_score": score,
                "total_ratings": ratings,
                "total_reviews": reviews,
                "total_installs": installs,
                "review_quality": app_data.get("reviewQualityScore", 0),
                "engagement_score": app_data.get("engagementScore", 0),
                "estimated_revenue": self._estimate_revenue(app_data),
                "market_presence": self._calculate_market_presence(app_data),
                "growth_metrics": {
                    "daily_installs": app_data.get("estimatedDailyInstalls", 0),
                    "monthly_installs": app_data.get("estimatedMonthlyInstalls", 0),
                }
            }
            
            # Add review sentiment if available
            if "recent_reviews" in app_data:
                metrics["review_sentiment"] = app_data["recent_reviews"].get("sentiment_distribution", {})
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating app metrics: {str(e)}")
            return self._get_default_app_metrics()

    def _compare_with_main_app(self, main_app: Dict[str, Any], competitor: Dict[str, Any]) -> Dict[str, Any]:
        """Compare competitor with main app"""
        try:
            main_metrics = self._calculate_app_metrics(main_app)
            comp_metrics = self._calculate_app_metrics(competitor)
            
            return {
                "rating_difference": self._calculate_difference(
                    comp_metrics["rating_score"],
                    main_metrics["rating_score"]
                ),
                "install_difference": self._calculate_difference(
                    comp_metrics["total_installs"],
                    main_metrics["total_installs"]
                ),
                "review_difference": self._calculate_difference(
                    comp_metrics["total_reviews"],
                    main_metrics["total_reviews"]
                ),
                "engagement_difference": self._calculate_difference(
                    comp_metrics["engagement_score"],
                    main_metrics["engagement_score"]
                ),
                "relative_market_position": self._compare_market_position(
                    main_metrics,
                    comp_metrics
                )
            }
            
        except Exception as e:
            logger.error(f"Error comparing with main app: {str(e)}")
            return self._get_default_comparison()

    def _analyze_market_position(self, main_app: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market position and trends"""
        try:
            main_metrics = self._calculate_app_metrics(main_app)
            competitor_metrics = [
                self._calculate_app_metrics(comp)
                for comp in competitors
            ]
            
            # Calculate percentiles
            rating_percentile = self._calculate_percentile(
                main_metrics["rating_score"],
                [m["rating_score"] for m in competitor_metrics]
            )
            
            install_percentile = self._calculate_percentile(
                main_metrics["total_installs"],
                [m["total_installs"] for m in competitor_metrics]
            )
            
            engagement_percentile = self._calculate_percentile(
                main_metrics["engagement_score"],
                [m["engagement_score"] for m in competitor_metrics]
            )
            
            # Calculate overall position
            overall_percentile = (rating_percentile + install_percentile + engagement_percentile) / 3
            
            return {
                "market_position": self._get_market_position_category(overall_percentile),
                "percentiles": {
                    "rating": rating_percentile,
                    "installs": install_percentile,
                    "engagement": engagement_percentile,
                    "overall": overall_percentile
                },
                "market_share": self._calculate_market_share(
                    main_metrics["total_installs"],
                    [m["total_installs"] for m in competitor_metrics]
                ),
                "competitive_analysis": {
                    "strengths": self._identify_strengths(main_metrics, competitor_metrics),
                    "weaknesses": self._identify_weaknesses(main_metrics, competitor_metrics),
                    "opportunities": self._identify_opportunities(main_metrics, competitor_metrics)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market position: {str(e)}")
            return self._get_default_market_analysis()

    def _calculate_market_presence(self, app_data: Dict[str, Any]) -> float:
        """Calculate market presence score (0-100)"""
        try:
            # Weights for different factors
            weights = {
                'installs': 0.4,
                'reviews': 0.2,
                'rating': 0.2,
                'engagement': 0.2
            }
            
            # Calculate normalized scores
            install_score = min(int(app_data.get('minInstalls', 0) or 0) / 1000000, 1) * 100
            review_score = min(int(app_data.get('reviews', 0) or 0) / 100000, 1) * 100
            rating_score = (float(app_data.get('score', 0) or 0) / 5) * 100
            engagement_score = float(app_data.get('engagementScore', 0) or 0)
            
            # Calculate weighted average
            market_presence = (
                (install_score * weights['installs']) +
                (review_score * weights['reviews']) +
                (rating_score * weights['rating']) +
                (engagement_score * weights['engagement'])
            )
            
            return round(market_presence, 2)
            
        except Exception as e:
            logger.error(f"Error calculating market presence: {str(e)}")
            return 0.0

    def _estimate_revenue(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate app revenue"""
        try:
            # Basic revenue estimation
            price = float(app_data.get('price', 0) or 0)
            installs = int(app_data.get('minInstalls', 0) or 0)
            has_iap = bool(app_data.get('offersIAP', False))
            
            if price > 0:
                base_revenue = price * installs
            else:
                base_revenue = 0
            
            # Estimate IAP revenue if applicable
            iap_revenue = 0
            if has_iap:
                # Assume 5% of users make IAPs with average value of $5
                iap_revenue = (installs * 0.05) * 5
            
            # Estimate ad revenue
            ad_supported = bool(app_data.get('adSupported', False))
            ad_revenue = 0
            if ad_supported:
                # Assume $0.01 per user per month
                ad_revenue = installs * 0.01
            
            total_revenue = base_revenue + iap_revenue + ad_revenue
            
            return {
                "estimated_total_revenue": round(total_revenue, 2),
                "breakdown": {
                    "base_revenue": round(base_revenue, 2),
                    "iap_revenue": round(iap_revenue, 2),
                    "ad_revenue": round(ad_revenue, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error estimating revenue: {str(e)}")
            return {
                "estimated_total_revenue": 0,
                "breakdown": {
                    "base_revenue": 0,
                    "iap_revenue": 0,
                    "ad_revenue": 0
                }
            }

    def _identify_strengths(self, main_metrics: Dict[str, Any], competitor_metrics: List[Dict[str, Any]]) -> List[str]:
        """Identify app strengths"""
        strengths = []
        
        # Compare with average competitor metrics
        avg_competitor_rating = sum(m["rating_score"] for m in competitor_metrics) / len(competitor_metrics) if competitor_metrics else 0
        if main_metrics["rating_score"] > avg_competitor_rating:
            strengths.append("Higher user rating than competitors")
        
        avg_competitor_engagement = sum(m["engagement_score"] for m in competitor_metrics) / len(competitor_metrics) if competitor_metrics else 0
        if main_metrics["engagement_score"] > avg_competitor_engagement:
            strengths.append("Better user engagement")
        
        if main_metrics["review_quality"] > 70:
            strengths.append("High review quality")
        
        return strengths

    def _identify_weaknesses(self, main_metrics: Dict[str, Any], competitor_metrics: List[Dict[str, Any]]) -> List[str]:
        """Identify app weaknesses"""
        weaknesses = []
        
        avg_competitor_rating = sum(m["rating_score"] for m in competitor_metrics) / len(competitor_metrics) if competitor_metrics else 0
        if main_metrics["rating_score"] < avg_competitor_rating:
            weaknesses.append("Lower user rating than competitors")
        
        avg_competitor_engagement = sum(m["engagement_score"] for m in competitor_metrics) / len(competitor_metrics) if competitor_metrics else 0
        if main_metrics["engagement_score"] < avg_competitor_engagement:
            weaknesses.append("Lower user engagement")
        
        if main_metrics["review_quality"] < 30:
            weaknesses.append("Low review quality")
        
        return weaknesses

    def _identify_opportunities(self, main_metrics: Dict[str, Any], competitor_metrics: List[Dict[str, Any]]) -> List[str]:
        """Identify market opportunities"""
        opportunities = []
        
        # Analyze market gaps
        max_competitor_rating = max(m["rating_score"] for m in competitor_metrics) if competitor_metrics else 0
        if main_metrics["rating_score"] < max_competitor_rating:
            opportunities.append("Potential to improve rating to match market leaders")
        
        if main_metrics["engagement_score"] < 50:
            opportunities.append("Room for improving user engagement")
        
        if main_metrics["review_quality"] < 50:
            opportunities.append("Opportunity to improve review quality")
        
        return opportunities

    def _calculate_market_share(self, main_installs: int, competitor_installs: List[int]) -> Dict[str, Any]:
        """Calculate market share percentages"""
        try:
            total_installs = main_installs + sum(competitor_installs)
            if total_installs == 0:
                return {
                    "main_app": 0,
                    "competitors": 0,
                    "total_market_size": 0
                }
            
            main_share = (main_installs / total_installs) * 100
            competitor_share = 100 - main_share
            
            return {
                "main_app": round(main_share, 2),
                "competitors": round(competitor_share, 2),
                "total_market_size": total_installs
            }
            
        except Exception as e:
            logger.error(f"Error calculating market share: {str(e)}")
            return {
                "main_app": 0,
                "competitors": 0,
                "total_market_size": 0
            }

    def _calculate_difference(self, value1: float, value2: float) -> Dict[str, Any]:
        """Calculate difference with percentage"""
        try:
            absolute_diff = value1 - value2
            if value2 != 0:
                percentage_diff = (absolute_diff / value2) * 100
            else:
                percentage_diff = 0 if value1 == 0 else 100
            
            return {
                "absolute": round(absolute_diff, 2),
                "percentage": round(percentage_diff, 2)
            }
            
        except Exception:
            return {
                "absolute": 0,
                "percentage": 0
            }

    def _compare_market_position(self, main_metrics: Dict[str, Any], comp_metrics: Dict[str, Any]) -> str:
        """Compare market positions"""
        try:
            main_score = (
                main_metrics["rating_score"] * 0.3 +
                main_metrics["engagement_score"] * 0.3 +
                (main_metrics["total_installs"] / 1000000) * 0.4
            )
            
            comp_score = (
                comp_metrics["rating_score"] * 0.3 +
                comp_metrics["engagement_score"] * 0.3 +
                (comp_metrics["total_installs"] / 1000000) * 0.4
            )
            
            diff = main_score - comp_score
            
            if diff > 10:
                return "Market Leader"
            elif diff > 0:
                return "Competitive Advantage"
            elif diff > -10:
                return "Close Competitor"
            else:
                return "Market Follower"
                
        except Exception:
            return "Unknown"

    def _calculate_percentile(self, value: float, comparison_values: List[float]) -> float:
        """Calculate percentile with improved error handling"""
        try:
            if not comparison_values:
                return 0.0
            
            below_value = sum(1 for x in comparison_values if x < value)
            return (below_value / len(comparison_values)) * 100 if comparison_values else 0.0
        except Exception:
            return 0.0

    def _get_market_position_category(self, percentile: float) -> str:
        """Determine market position category based on percentile"""
        if percentile >= 75:
            return "Market Leader"
        elif percentile >= 50:
            return "Strong Competitor"
        elif percentile >= 25:
            return "Growing Competitor"
        else:
            return "Market Challenger"

    def _get_default_app_metrics(self) -> Dict[str, Any]:
        """Return default app metrics"""
        return {
            "rating_score": 0.0,
            "total_ratings": 0,
            "total_reviews": 0,
            "total_installs": 0,
            "review_quality": 0,
            "engagement_score": 0,
            "estimated_revenue": {
                "estimated_total_revenue": 0,
                "breakdown": {
                    "base_revenue": 0,
                    "iap_revenue": 0,
                    "ad_revenue": 0
                }
            },
            "market_presence": 0,
            "growth_metrics": {
                "daily_installs": 0,
                "monthly_installs": 0
            }
        }

    def _get_default_comparison(self) -> Dict[str, Any]:
        """Return default comparison metrics"""
        return {
            "rating_difference": {"absolute": 0, "percentage": 0},
            "install_difference": {"absolute": 0, "percentage": 0},
            "review_difference": {"absolute": 0, "percentage": 0},
            "engagement_difference": {"absolute": 0, "percentage": 0},
            "relative_market_position": "Unknown"
        }

    def _get_default_market_analysis(self) -> Dict[str, Any]:
        """Return default market analysis"""
        return {
            "market_position": "Unknown",
            "percentiles": {
                "rating": 0,
                "installs": 0,
                "engagement": 0,
                "overall": 0
            },
            "market_share": {
                "main_app": 0,
                "competitors": 0,
                "total_market_size": 0
            },
            "competitive_analysis": {
                "strengths": [],
                "weaknesses": [],
                "opportunities": []
            }
        }