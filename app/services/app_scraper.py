from google_play_scraper import app
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re

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
            # Extract and validate critical fields with default values
            cleaned = {
                # Basic Info
                "title": str(data.get('title', '')).strip() or 'Unknown',
                "summary": str(data.get('summary', '')).strip() or '',
                "description": str(data.get('description', '')).strip() or '',
                "descriptionHTML": str(data.get('descriptionHTML', '')).strip() or '',
                "appId": str(data.get('appId', '')).strip(),
                "url": str(data.get('url', '')).strip(),
                
                # Performance Metrics
                "score": float(data.get('score', 0) or 0),
                "ratings": int(data.get('ratings', 0) or 0),
                "reviews": int(data.get('reviews', 0) or 0),
                "installs": str(data.get('installs', '0+')).strip(),
                "minInstalls": int(data.get('minInstalls', 0) or 0),
                "maxInstalls": int(data.get('maxInstalls', 0) or 0),
                
                # Business Info
                "price": float(data.get('price', 0) or 0),
                "free": bool(data.get('free', True)),
                "currency": str(data.get('currency', 'USD')),
                "offersIAP": bool(data.get('offersIAP', False)),
                
                # Category Info
                "genre": str(data.get('genre', '')).strip() or 'Unknown',
                "genreId": str(data.get('genreId', '')).strip(),
                
                # Developer Info
                "developer": str(data.get('developer', '')).strip() or 'Unknown',
                "developerId": str(data.get('developerId', '')).strip(),
                "developerEmail": str(data.get('developerEmail', '')).strip(),
                "developerWebsite": str(data.get('developerWebsite', '')).strip(),
                
                # Visual Assets
                "icon": str(data.get('icon', '')).strip(),
                "headerImage": str(data.get('headerImage', '')).strip(),
                "screenshots": list(data.get('screenshots', [])),
                "video": str(data.get('video', '')).strip(),
                
                # Content Info
                "contentRating": str(data.get('contentRating', '')).strip() or 'Not Rated',
                "contentRatingDescription": str(data.get('contentRatingDescription', '')).strip(),
                "adSupported": bool(data.get('adSupported', False)),
                "containsAds": bool(data.get('containsAds', False)),
                
                # Technical Info
                "released": str(data.get('released', '')).strip(),
                "updated": int(data.get('updated', 0) or 0),
                "version": str(data.get('version', '')).strip() or 'Unknown',
                "recentChanges": str(data.get('recentChanges', '')).strip(),
                "size": str(data.get('size', '')).strip() or 'Unknown',
                "androidVersion": str(data.get('androidVersion', '')).strip() or 'Unknown',
                "androidVersionText": str(data.get('androidVersionText', '')).strip() or 'Unknown',
                
                # Review Distribution
                "histogram": [int(x) for x in data.get('histogram', [0, 0, 0, 0, 0])],
                
                # Metadata
                "scrapedAt": datetime.now().isoformat(),
            }

            # Add computed metrics
            cleaned.update(self._calculate_metrics(cleaned))
            
            # Add data quality score
            cleaned["dataQuality"] = self._calculate_data_quality(cleaned)
            
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

    def _calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional metrics"""
        try:
            metrics = {}
            
            # Calculate review quality (0-100)
            if data['reviews'] > 0 and data['score'] > 0:
                review_quality = (data['score'] * 20) * (1 + (data['reviews'] / 100000))
                metrics['reviewQualityScore'] = min(100, review_quality)
            else:
                metrics['reviewQualityScore'] = 0
            
            # Calculate engagement rate (0-100)
            if data['minInstalls'] > 0:
                engagement = (data['reviews'] / data['minInstalls']) * 1000
                metrics['engagementScore'] = min(100, engagement)
            else:
                metrics['engagementScore'] = 0
            
            # Extract real install count from string
            install_match = re.search(r'(\d+(?:,\d+)*)', data['installs'])
            if install_match:
                real_installs = int(install_match.group(1).replace(',', ''))
                metrics['realInstalls'] = real_installs
            else:
                metrics['realInstalls'] = data['minInstalls']
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return {
                'reviewQualityScore': 0,
                'engagementScore': 0,
                'realInstalls': 0
            }

    def _calculate_data_quality(self, data: Dict[str, Any]) -> str:
        """Calculate data quality score"""
        try:
            required_fields = [
                'title', 'description', 'score', 'reviews',
                'installs', 'genre', 'developer'
            ]
            
            optional_fields = [
                'developerWebsite', 'video', 'recentChanges',
                'contentRatingDescription', 'headerImage'
            ]
            
            # Calculate completeness scores
            required_score = sum(1 for field in required_fields if data.get(field)) / len(required_fields)
            optional_score = sum(1 for field in optional_fields if data.get(field)) / len(optional_fields)
            
            # Calculate validity scores
            valid_score = 0
            total_checks = 0
            
            # Check numeric fields
            if data['score'] >= 0 and data['score'] <= 5:
                valid_score += 1
            total_checks += 1
            
            if data['reviews'] >= 0:
                valid_score += 1
            total_checks += 1
            
            if data['minInstalls'] >= 0:
                valid_score += 1
            total_checks += 1
            
            # Check text fields
            if len(data['description']) > 100:
                valid_score += 1
            total_checks += 1
            
            if len(data['title']) > 0:
                valid_score += 1
            total_checks += 1
            
            validity_score = valid_score / total_checks if total_checks > 0 else 0
            
            # Calculate final score
            final_score = (required_score * 0.5) + (optional_score * 0.2) + (validity_score * 0.3)
            
            if final_score >= 0.8:
                return "high"
            elif final_score >= 0.5:
                return "medium"
            else:
                return "low"
            
        except Exception as e:
            logger.error(f"Error calculating data quality: {str(e)}")
            return "unknown"