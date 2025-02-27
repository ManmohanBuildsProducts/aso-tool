from google_play_scraper import app
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AppScraper:
    def __init__(self):
        pass

    async def get_app_details(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Get app details from Google Play Store with improved error handling and data validation
        """
        try:
            result = app(
                app_id,
                lang='en',
                country='us'
            )
            
            # Validate and clean the data
            cleaned_data = self._clean_app_data(result)
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error fetching app details for {app_id}: {str(e)}")
            return None

    def _clean_app_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and validate app data, ensuring all required fields have proper values
        """
        try:
            # Ensure critical fields have default values
            cleaned = {
                "title": str(data.get("title", "")) or "Unknown",
                "description": str(data.get("description", "")) or "",
                "descriptionHTML": str(data.get("descriptionHTML", "")) or "",
                "summary": str(data.get("summary", "")) or "",
                "installs": str(data.get("installs", "0+")) or "0+",
                "minInstalls": int(data.get("minInstalls", 0)) or 0,
                "score": float(data.get("score", 0)) if data.get("score") is not None else 0.0,
                "ratings": int(data.get("ratings", 0)) or 0,
                "reviews": int(data.get("reviews", 0)) or 0,
                "price": float(data.get("price", 0)) or 0.0,
                "free": bool(data.get("free", True)),
                "currency": str(data.get("currency", "USD")) or "USD",
                "genre": str(data.get("genre", "")) or "Unknown",
                "genreId": str(data.get("genreId", "")) or "",
                "developer": str(data.get("developer", "")) or "Unknown",
                "developerId": str(data.get("developerId", "")) or "",
                "icon": str(data.get("icon", "")) or "",
                "headerImage": str(data.get("headerImage", "")) or "",
                "screenshots": list(data.get("screenshots", [])) or [],
                "contentRating": str(data.get("contentRating", "")) or "Not Rated",
                "adSupported": bool(data.get("adSupported", False)),
                "containsAds": bool(data.get("containsAds", False)),
                "released": str(data.get("released", "")) or "Unknown",
                "updated": int(data.get("updated", 0)) or 0,
                "version": str(data.get("version", "")) or "Unknown",
                "recentChanges": str(data.get("recentChanges", "")) or "",
                "size": str(data.get("size", "")) or "Unknown",
                "androidVersion": str(data.get("androidVersion", "")) or "Unknown",
                "androidVersionText": str(data.get("androidVersionText", "")) or "Unknown"
            }

            # Add computed fields
            cleaned["appId"] = str(data.get("appId", "")) or ""
            cleaned["url"] = str(data.get("url", "")) or f"https://play.google.com/store/apps/details?id={cleaned['appId']}&hl=en&gl=us"
            
            # Add histogram data with validation
            histogram = data.get("histogram", [0, 0, 0, 0, 0])
            cleaned["histogram"] = [int(x) for x in histogram] if isinstance(histogram, list) else [0, 0, 0, 0, 0]

            return cleaned
        except Exception as e:
            logger.error(f"Error cleaning app data: {str(e)}")
            # Return minimal valid data
            return {
                "title": "Unknown",
                "appId": str(data.get("appId", "")) or "",
                "score": 0.0,
                "ratings": 0,
                "reviews": 0,
                "minInstalls": 0,
                "installs": "0+",
                "genre": "Unknown",
                "histogram": [0, 0, 0, 0, 0]
            }