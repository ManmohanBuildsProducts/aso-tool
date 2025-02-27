from typing import List, Dict, Any
from services.app_scraper import AppScraper
from services.keyword_analyzer import KeywordAnalyzer
import logging

logger = logging.getLogger(__name__)

class CompetitorAnalyzer:
    def __init__(self):
        self.app_scraper = AppScraper()
        self.keyword_analyzer = KeywordAnalyzer()

    async def analyze_competitors(self, app_id: str, competitor_ids: List[str]) -> Dict[str, Any]:
        """
        Perform comprehensive competitor analysis
        """
        try:
            # Get main app details
            main_app = await self.app_scraper.get_app_details(app_id)
            
            # Get competitor details
            competitor_details = []
            valid_competitors = False
            for comp_id in competitor_ids:
                try:
                    comp_details = await self.app_scraper.get_app_details(comp_id)
                    competitor_details.append(comp_details)
                    valid_competitors = True
                except Exception as e:
                    logger.warning(f"Error fetching competitor {comp_id}: {str(e)}")
                    continue
            
            if not valid_competitors:
                raise Exception("No valid competitor data found")

            # Perform keyword comparison
            keyword_analysis = await self.keyword_analyzer.compare_keywords(app_id, competitor_ids)

            # Calculate metrics comparison
            metrics_comparison = self._compare_metrics(main_app, competitor_details)

            return {
                "main_app": {
                    "app_id": app_id,
                    "details": main_app
                },
                "competitors": [
                    {"app_id": comp["appId"], "details": comp}
                    for comp in competitor_details
                ],
                "keyword_analysis": keyword_analysis["keyword_comparison"],
                "metrics_comparison": metrics_comparison
            }
        except Exception as e:
            logger.error(f"Error analyzing competitors: {str(e)}")
            raise

    def _compare_metrics(self, main_app: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare various metrics between main app and competitors
        """
        def safe_get(obj: Dict[str, Any], key: str, default: float = 0) -> float:
            """Safely get a numeric value from dictionary"""
            value = obj.get(key)
            try:
                return float(value) if value is not None else default
            except (ValueError, TypeError):
                return default

        metrics = {
            "ratings": {
                "main_app": safe_get(main_app, "score"),
                "competitors": [safe_get(comp, "score") for comp in competitors],
                "avg_competitor_rating": sum(safe_get(comp, "score") for comp in competitors) / len(competitors) if competitors else 0
            },
            "installs": {
                "main_app": safe_get(main_app, "minInstalls"),
                "competitors": [safe_get(comp, "minInstalls") for comp in competitors],
                "avg_competitor_installs": sum(safe_get(comp, "minInstalls") for comp in competitors) / len(competitors) if competitors else 0
            },
            "reviews": {
                "main_app": safe_get(main_app, "reviews"),
                "competitors": [safe_get(comp, "reviews") for comp in competitors],
                "avg_competitor_reviews": sum(safe_get(comp, "reviews") for comp in competitors) / len(competitors) if competitors else 0
            }
        }

        # Calculate relative market position
        metrics["market_position"] = {
            "rating_percentile": self._calculate_percentile(
                main_app.get("score", 0),
                [comp.get("score", 0) for comp in competitors]
            ),
            "installs_percentile": self._calculate_percentile(
                main_app.get("minInstalls", 0),
                [comp.get("minInstalls", 0) for comp in competitors]
            ),
            "reviews_percentile": self._calculate_percentile(
                main_app.get("reviews", 0),
                [comp.get("reviews", 0) for comp in competitors]
            )
        }

        return metrics

    def _calculate_percentile(self, value: float, comparison_values: List[float]) -> float:
        """
        Calculate the percentile of a value within a list of comparison values
        """
        # Convert value to float and handle None/invalid values
        try:
            value = float(value) if value is not None else 0
        except (ValueError, TypeError):
            value = 0
            
        # Filter and convert comparison values
        valid_comparisons = []
        for x in comparison_values:
            try:
                x_float = float(x) if x is not None else 0
                valid_comparisons.append(x_float)
            except (ValueError, TypeError):
                continue
                
        if not valid_comparisons:
            return 0
        
        below_value = sum(1 for x in valid_comparisons if x < value)
        return (below_value / len(valid_comparisons)) * 100

    def _calculate_field_trend(self, values: List[float]) -> Dict[str, Any]:
        """
        Calculate trend metrics for a field
        """
        # Filter out None values and convert to float
        valid_values = [float(v) for v in values if v is not None]
        
        if not valid_values:
            return {
                "current": 0,
                "minimum": 0,
                "maximum": 0,
                "average": 0,
                "direction": "stable",
                "volatility": 0
            }
        
        # Calculate basic metrics
        min_val = min(valid_values)
        max_val = max(valid_values)
        avg_val = sum(valid_values) / len(valid_values)
        
        # Calculate trend direction
        if len(valid_values) >= 2:
            recent_change = valid_values[-1] - valid_values[-2]
            trend_direction = "increasing" if recent_change > 0 else "decreasing" if recent_change < 0 else "stable"
        else:
            trend_direction = "stable"
        
        # Calculate volatility
        if len(valid_values) >= 2:
            changes = [abs(valid_values[i] - valid_values[i-1]) for i in range(1, len(valid_values))]
            volatility = sum(changes) / len(changes)
        else:
            volatility = 0