from google_play_scraper import app
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class AppScraper:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=3)
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour

    async def get_app_details(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Get app details from Google Play Store with caching and retries
        """
        try:
            # Check cache first
            cached = self._get_from_cache(app_id)
            if cached:
                return cached

            # Fetch with retries
            for attempt in range(3):
                try:
                    # Run in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self._executor,
                        lambda: app(
                            app_id,
                            lang='en',
                            country='us'
                        )
                    )
                    
                    if result:
                        # Clean and validate data
                        cleaned_data = self._clean_app_data(result)
                        # Cache the result
                        self._cache[app_id] = {
                            'data': cleaned_data,
                            'timestamp': datetime.now().timestamp()
                        }
                        return cleaned_data
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {app_id}: {str(e)}")
                    await asyncio.sleep(1)  # Wait before retry
            
            raise Exception(f"Failed to fetch app details after 3 attempts for {app_id}")
            
        except Exception as e:
            logger.error(f"Error fetching app details for {app_id}: {str(e)}")
            return None

    def _get_from_cache(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Check cache for valid data"""
        if app_id in self._cache:
            cache_entry = self._cache[app_id]
            if datetime.now().timestamp() - cache_entry['timestamp'] < self._cache_ttl:
                return cache_entry['data']
            else:
                del self._cache[app_id]
        return None

    def _clean_app_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate app data with improved error handling"""
        try:
            # Extract and validate critical fields
            title = str(data.get('title', '')).strip()
            score = float(data.get('score')) if data.get('score') is not None else 0.0
            reviews = int(data.get('reviews', 0))
            installs = str(data.get('installs', '0+')).strip()
            min_installs = int(data.get('minInstalls', 0))
            
            # Enhanced data structure with marketing-focused metrics
            cleaned = {
                # Basic Info
                "title": title,
                "summary": str(data.get('summary', '')).strip(),
                "description": str(data.get('description', '')).strip(),
                "descriptionHTML": str(data.get('descriptionHTML', '')).strip(),
                "appId": str(data.get('appId', '')).strip(),
                "url": str(data.get('url', '')).strip(),
                
                # Performance Metrics
                "score": score,
                "ratings": int(data.get('ratings', 0)),
                "reviews": reviews,
                "installs": installs,
                "minInstalls": min_installs,
                "maxInstalls": int(data.get('maxInstalls', min_installs)),
                
                # Engagement Metrics
                "reviewsPerInstall": (reviews / min_installs) if min_installs > 0 else 0,
                "scoreToReviewsRatio": (score * reviews) if reviews > 0 else 0,
                
                # Business Info
                "price": float(data.get('price', 0)),
                "free": bool(data.get('free', True)),
                "currency": str(data.get('currency', 'USD')),
                "inAppProducts": bool(data.get('offersIAP', False)),
                
                # Category Info
                "genre": str(data.get('genre', '')).strip(),
                "genreId": str(data.get('genreId', '')).strip(),
                "categories": data.get('categories', []),
                
                # Developer Info
                "developer": str(data.get('developer', '')).strip(),
                "developerId": str(data.get('developerId', '')).strip(),
                "developerEmail": str(data.get('developerEmail', '')).strip(),
                "developerWebsite": str(data.get('developerWebsite', '')).strip(),
                
                # Visual Assets
                "icon": str(data.get('icon', '')).strip(),
                "headerImage": str(data.get('headerImage', '')).strip(),
                "screenshots": list(data.get('screenshots', [])),
                "video": str(data.get('video', '')).strip(),
                
                # Content Info
                "contentRating": str(data.get('contentRating', '')).strip(),
                "contentRatingDescription": str(data.get('contentRatingDescription', '')).strip(),
                "adSupported": bool(data.get('adSupported', False)),
                "containsAds": bool(data.get('containsAds', False)),
                
                # Technical Info
                "released": str(data.get('released', '')).strip(),
                "updated": int(data.get('updated', 0)),
                "version": str(data.get('version', '')).strip(),
                "recentChanges": str(data.get('recentChanges', '')).strip(),
                "size": str(data.get('size', '')).strip(),
                "androidVersion": str(data.get('androidVersion', '')).strip(),
                "androidVersionText": str(data.get('androidVersionText', '')).strip(),
                
                # Review Distribution
                "histogram": [int(x) for x in data.get('histogram', [0, 0, 0, 0, 0])],
                
                # Metadata
                "scrapedAt": datetime.now().isoformat(),
                "dataQuality": self._calculate_data_quality(data)
            }
            
            # Add computed metrics
            cleaned.update(self._calculate_additional_metrics(cleaned))
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning app data: {str(e)}")
            # Return minimal valid data
            return {
                "title": str(data.get('title', 'Unknown')),
                "appId": str(data.get('appId', '')),
                "score": 0.0,
                "ratings": 0,
                "reviews": 0,
                "minInstalls": 0,
                "installs": "0+",
                "genre": "Unknown",
                "histogram": [0, 0, 0, 0, 0],
                "scrapedAt": datetime.now().isoformat(),
                "dataQuality": "minimal"
            }

    def _calculate_data_quality(self, data: Dict[str, Any]) -> str:
        """Calculate data quality score"""
        required_fields = ['title', 'score', 'reviews', 'installs', 'description']
        optional_fields = ['developerWebsite', 'video', 'recentChanges']
        
        required_count = sum(1 for field in required_fields if data.get(field))
        optional_count = sum(1 for field in optional_fields if data.get(field))
        
        total_score = (required_count / len(required_fields)) * 0.7 + (optional_count / len(optional_fields)) * 0.3
        
        if total_score >= 0.8:
            return "high"
        elif total_score >= 0.5:
            return "medium"
        else:
            return "low"

    def _calculate_additional_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional marketing-focused metrics"""
        try:
            metrics = {}
            
            # Review Quality Score (0-100)
            if data['reviews'] > 0 and data['score'] > 0:
                review_quality = (data['score'] * 20) * (1 + (data['reviews'] / 100000))
                metrics['reviewQualityScore'] = min(100, review_quality)
            else:
                metrics['reviewQualityScore'] = 0
            
            # Installation Velocity (estimated monthly installs)
            if data['minInstalls'] > 0 and data['updated'] > 0:
                days_since_update = (datetime.now().timestamp() - data['updated']) / 86400
                if days_since_update > 0:
                    metrics['estimatedMonthlyInstalls'] = int(data['minInstalls'] / (days_since_update / 30))
                else:
                    metrics['estimatedMonthlyInstalls'] = 0
            else:
                metrics['estimatedMonthlyInstalls'] = 0
            
            # User Engagement Score (0-100)
            if data['minInstalls'] > 0:
                engagement = (data['reviews'] / data['minInstalls']) * 1000
                metrics['userEngagementScore'] = min(100, engagement)
            else:
                metrics['userEngagementScore'] = 0
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating additional metrics: {str(e)}")
            return {
                'reviewQualityScore': 0,
                'estimatedMonthlyInstalls': 0,
                'userEngagementScore': 0
            }