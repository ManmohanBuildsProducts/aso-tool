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
        Perform comprehensive competitor analysis with improved error handling and data validation
        """
        try:
            # Get main app details with validation
            main_app = await self._get_app_details_safely(app_id)
            if not main_app:
                raise Exception(f"Failed to fetch main app details for {app_id}")
            
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
            
            if not competitor_details:
                logger.warning("No valid competitor data found")
                # Return analysis with only main app data
                return {
                    "status": "partial",
                    "main_app": {
                        "app_id": app_id,
                        "details": main_app
                    },
                    "competitors": [],
                    "metrics_comparison": self._get_default_metrics()
                }

            # Perform keyword comparison
            try:
                keyword_analysis = await self.keyword_analyzer.compare_keywords(app_id, competitor_ids)
            except Exception as e:
                logger.error(f"Error in keyword analysis: {str(e)}")
                keyword_analysis = {"keyword_comparison": {}}

            # Calculate metrics comparison with improved error handling
            metrics_comparison = self._compare_metrics(main_app, competitor_details)

            return {
                "status": "success",
                "main_app": {
                    "app_id": app_id,
                    "details": main_app
                },
                "competitors": [
                    {"app_id": comp["appId"], "details": comp}
                    for comp in competitor_details
                ],
                "keyword_analysis": keyword_analysis.get("keyword_comparison", {}),
                "metrics_comparison": metrics_comparison
            }
        except Exception as e:
            logger.error(f"Error analyzing competitors: {str(e)}")
            raise

    async def _get_app_details_safely(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Safely fetch app details with validation and default values
        """
        try:
            details = await self.app_scraper.get_app_details(app_id)
            if not details:
                return None

            # Ensure critical fields have default values
            details["score"] = self._safe_float(details.get("score")) or 0.0
            details["reviews"] = self._safe_int(details.get("reviews")) or 0
            details["minInstalls"] = self._safe_int(details.get("minInstalls")) or 0
            details["maxInstalls"] = self._safe_int(details.get("maxInstalls")) or details["minInstalls"]
            details["ratings"] = self._safe_int(details.get("ratings")) or 0
            
            # Add timestamp for tracking
            details["analyzed_at"] = datetime.now().isoformat()
            
            return details
        except Exception as e:
            logger.error(f"Error fetching app details for {app_id}: {str(e)}")
            return None

    def _compare_metrics(self, main_app: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare various metrics between main app and competitors with improved error handling
        """
        try:
            # Calculate basic metrics
            metrics = {
                "ratings": self._calculate_rating_metrics(main_app, competitors),
                "installs": self._calculate_install_metrics(main_app, competitors),
                "reviews": self._calculate_review_metrics(main_app, competitors),
                "engagement": self._calculate_engagement_metrics(main_app, competitors),
                "market_position": self._calculate_market_position(main_app, competitors)
            }

            # Add trend analysis
            metrics["trends"] = {
                "rating_trend": self._calculate_trend(
                    metrics["ratings"]["main_app"],
                    metrics["ratings"]["avg_competitor_rating"]
                ),
                "install_trend": self._calculate_trend(
                    metrics["installs"]["main_app"],
                    metrics["installs"]["avg_competitor_installs"]
                ),
                "review_trend": self._calculate_trend(
                    metrics["reviews"]["main_app"],
                    metrics["reviews"]["avg_competitor_reviews"]
                )
            }

            return metrics
        except Exception as e:
            logger.error(f"Error comparing metrics: {str(e)}")
            return self._get_default_metrics()

    def _calculate_rating_metrics(self, main_app: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate rating-related metrics"""
        main_rating = self._safe_float(main_app.get("score")) or 0.0
        competitor_ratings = [self._safe_float(comp.get("score")) or 0.0 for comp in competitors]
        
        avg_competitor_rating = sum(competitor_ratings) / len(competitor_ratings) if competitor_ratings else 0.0
        
        return {
            "main_app": main_rating,
            "competitors": competitor_ratings,
            "avg_competitor_rating": avg_competitor_rating,
            "rating_difference": main_rating - avg_competitor_rating,
            "percentile": self._calculate_percentile(main_rating, competitor_ratings)
        }

    def _calculate_install_metrics(self, main_app: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate installation-related metrics"""
        main_installs = self._safe_int(main_app.get("minInstalls")) or 0
        competitor_installs = [self._safe_int(comp.get("minInstalls")) or 0 for comp in competitors]
        
        avg_competitor_installs = sum(competitor_installs) / len(competitor_installs) if competitor_installs else 0
        
        return {
            "main_app": main_installs,
            "competitors": competitor_installs,
            "avg_competitor_installs": avg_competitor_installs,
            "install_difference": main_installs - avg_competitor_installs,
            "percentile": self._calculate_percentile(main_installs, competitor_installs)
        }

    def _calculate_review_metrics(self, main_app: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate review-related metrics"""
        main_reviews = self._safe_int(main_app.get("reviews")) or 0
        competitor_reviews = [self._safe_int(comp.get("reviews")) or 0 for comp in competitors]
        
        avg_competitor_reviews = sum(competitor_reviews) / len(competitor_reviews) if competitor_reviews else 0
        
        return {
            "main_app": main_reviews,
            "competitors": competitor_reviews,
            "avg_competitor_reviews": avg_competitor_reviews,
            "review_difference": main_reviews - avg_competitor_reviews,
            "percentile": self._calculate_percentile(main_reviews, competitor_reviews)
        }

    def _calculate_engagement_metrics(self, main_app: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate engagement metrics"""
        def calc_engagement(app: Dict[str, Any]) -> float:
            reviews = self._safe_int(app.get("reviews")) or 0
            installs = self._safe_int(app.get("minInstalls")) or 1  # Avoid division by zero
            return (reviews / installs) * 100 if installs > 0 else 0

        main_engagement = calc_engagement(main_app)
        competitor_engagements = [calc_engagement(comp) for comp in competitors]
        avg_competitor_engagement = sum(competitor_engagements) / len(competitor_engagements) if competitor_engagements else 0

        return {
            "main_app": main_engagement,
            "competitors": competitor_engagements,
            "avg_competitor_engagement": avg_competitor_engagement,
            "engagement_difference": main_engagement - avg_competitor_engagement,
            "percentile": self._calculate_percentile(main_engagement, competitor_engagements)
        }

    def _calculate_market_position(self, main_app: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall market position"""
        metrics = {
            "rating_percentile": self._calculate_percentile(
                self._safe_float(main_app.get("score")) or 0.0,
                [self._safe_float(comp.get("score")) or 0.0 for comp in competitors]
            ),
            "installs_percentile": self._calculate_percentile(
                self._safe_int(main_app.get("minInstalls")) or 0,
                [self._safe_int(comp.get("minInstalls")) or 0 for comp in competitors]
            ),
            "reviews_percentile": self._calculate_percentile(
                self._safe_int(main_app.get("reviews")) or 0,
                [self._safe_int(comp.get("reviews")) or 0 for comp in competitors]
            )
        }
        
        # Calculate overall market position
        avg_percentile = sum(metrics.values()) / len(metrics)
        position_category = self._get_market_position_category(avg_percentile)
        
        metrics.update({
            "overall_percentile": avg_percentile,
            "market_position": position_category
        })
        
        return metrics

    def _calculate_trend(self, current_value: float, comparison_value: float) -> Dict[str, Any]:
        """Calculate trend metrics"""
        if comparison_value == 0:
            return {
                "direction": "stable",
                "percentage_change": 0,
                "status": "neutral"
            }

        percentage_change = ((current_value - comparison_value) / comparison_value) * 100
        
        return {
            "direction": "increasing" if percentage_change > 0 else "decreasing" if percentage_change < 0 else "stable",
            "percentage_change": percentage_change,
            "status": "positive" if percentage_change > 0 else "negative" if percentage_change < 0 else "neutral"
        }

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
            return "Growing"
        else:
            return "Emerging"

    def _get_default_metrics(self) -> Dict[str, Any]:
        """Return default metrics structure"""
        return {
            "ratings": {
                "main_app": 0.0,
                "competitors": [],
                "avg_competitor_rating": 0.0,
                "rating_difference": 0.0,
                "percentile": 0.0
            },
            "installs": {
                "main_app": 0,
                "competitors": [],
                "avg_competitor_installs": 0,
                "install_difference": 0,
                "percentile": 0.0
            },
            "reviews": {
                "main_app": 0,
                "competitors": [],
                "avg_competitor_reviews": 0,
                "review_difference": 0,
                "percentile": 0.0
            },
            "engagement": {
                "main_app": 0.0,
                "competitors": [],
                "avg_competitor_engagement": 0.0,
                "engagement_difference": 0.0,
                "percentile": 0.0
            },
            "market_position": {
                "rating_percentile": 0.0,
                "installs_percentile": 0.0,
                "reviews_percentile": 0.0,
                "overall_percentile": 0.0,
                "market_position": "Unknown"
            },
            "trends": {
                "rating_trend": {"direction": "stable", "percentage_change": 0, "status": "neutral"},
                "install_trend": {"direction": "stable", "percentage_change": 0, "status": "neutral"},
                "review_trend": {"direction": "stable", "percentage_change": 0, "status": "neutral"}
            }
        }

    @staticmethod
    def _safe_float(value: Any) -> Optional[float]:
        """Safely convert value to float"""
        try:
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_int(value: Any) -> Optional[int]:
        """Safely convert value to integer"""
        try:
            return int(value) if value is not None else None
        except (ValueError, TypeError):
            return None