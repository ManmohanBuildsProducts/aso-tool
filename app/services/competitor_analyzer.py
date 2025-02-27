from typing import List, Dict, Any
from .app_scraper import AppScraper
from .keyword_analyzer import KeywordAnalyzer
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
        metrics = {
            "ratings": {
                "main_app": main_app.get("score", 0),
                "competitors": [comp.get("score", 0) for comp in competitors],
                "avg_competitor_rating": sum(comp.get("score", 0) for comp in competitors) / len(competitors) if competitors else 0
            },
            "installs": {
                "main_app": main_app.get("minInstalls", 0),
                "competitors": [comp.get("minInstalls", 0) for comp in competitors],
                "avg_competitor_installs": sum(comp.get("minInstalls", 0) for comp in competitors) / len(competitors) if competitors else 0
            },
            "reviews": {
                "main_app": main_app.get("reviews", 0),
                "competitors": [comp.get("reviews", 0) for comp in competitors],
                "avg_competitor_reviews": sum(comp.get("reviews", 0) for comp in competitors) / len(competitors) if competitors else 0
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
        if not comparison_values:
            return 0
        
        below_value = sum(1 for x in comparison_values if x < value)
        return (below_value / len(comparison_values)) * 100