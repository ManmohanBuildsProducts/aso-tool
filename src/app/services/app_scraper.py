from google_play_scraper import app, reviews, exceptions
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re
import time
import random

logger = logging.getLogger(__name__)

class AppScraper:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=3)
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour
        self._retry_delays = [1, 2, 5]  # Exponential backoff
        self._countries = ['us', 'in', 'gb']  # Try multiple countries if one fails

    async def get_app_details(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get app details with retries, caching, and fallbacks"""
        try:
            # Check cache first
            cached = self._get_from_cache(app_id)
            if cached:
                return cached

            # Try each country until successful
            for country in self._countries:
                for attempt, delay in enumerate(self._retry_delays):
                    try:
                        # Run in thread pool to avoid blocking
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(
                            self._executor,
                            lambda: app(
                                app_id,
                                lang='en',
                                country=country
                            )
                        )
                        
                        if result:
                            # Enhance data with reviews
                            result = await self._enhance_with_reviews(app_id, result, country)
                            
                            # Clean and validate data
                            cleaned_data = self._clean_app_data(result)
                            
                            # Cache the result
                            self._cache[app_id] = {
                                'data': cleaned_data,
                                'timestamp': datetime.now().timestamp()
                            }
                            
                            return cleaned_data
                            
                    except exceptions.NotFoundError:
                        logger.warning(f"App {app_id} not found in {country}")
                        break  # Try next country
                    except Exception as e:
                        logger.warning(f"Attempt {attempt + 1} failed for {app_id} in {country}: {str(e)}")
                        if attempt < len(self._retry_delays) - 1:
                            await asyncio.sleep(delay + random.random())  # Add jitter
                        continue
            
            raise Exception(f"Failed to fetch app details after all attempts for {app_id}")
            
        except Exception as e:
            logger.error(f"Error fetching app details for {app_id}: {str(e)}")
            return self._get_minimal_data(app_id)

    async def _enhance_with_reviews(self, app_id: str, app_data: Dict[str, Any], country: str) -> Dict[str, Any]:
        """Enhance app data with review analysis"""
        try:
            # Get latest reviews
            loop = asyncio.get_event_loop()
            result, continuation_token = await loop.run_in_executor(
                self._executor,
                lambda: reviews(
                    app_id,
                    lang='en',
                    country=country,
                    count=100,
                    sort='newest'
                )
            )
            
            if result:
                # Calculate review metrics
                review_metrics = self._analyze_reviews(result)
                app_data.update(review_metrics)
            
            return app_data
            
        except Exception as e:
            logger.warning(f"Error fetching reviews for {app_id}: {str(e)}")
            return app_data

    def _analyze_reviews(self, reviews_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze reviews for sentiment and key metrics"""
        try:
            if not reviews_data:
                return {}
                
            total_reviews = len(reviews_data)
            if total_reviews == 0:
                return {}
                
            # Calculate metrics
            avg_score = sum(review['score'] for review in reviews_data) / total_reviews
            sentiment_counts = {
                'positive': sum(1 for r in reviews_data if r['score'] >= 4),
                'neutral': sum(1 for r in reviews_data if r['score'] == 3),
                'negative': sum(1 for r in reviews_data if r['score'] <= 2)
            }
            
            # Calculate percentages
            sentiment_percentages = {
                key: (count / total_reviews) * 100 
                for key, count in sentiment_counts.items()
            }
            
            return {
                'recent_reviews': {
                    'count': total_reviews,
                    'average_score': round(avg_score, 2),
                    'sentiment_distribution': sentiment_percentages,
                    'latest_review_date': max(r['at'] for r in reviews_data),
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing reviews: {str(e)}")
            return {}

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
            title = str(data.get('title', '')).strip() or 'Unknown'
            score = self._safe_float(data.get('score')) or 0.0
            reviews_count = self._safe_int(data.get('reviews')) or 0
            installs = str(data.get('installs', '0+')).strip()
            min_installs = self._safe_int(data.get('minInstalls')) or 0
            
            # Extract real install count
            real_installs = self._extract_real_installs(installs, min_installs)
            
            cleaned = {
                # Basic Info
                "title": title,
                "summary": str(data.get('summary', '')).strip() or title,
                "description": str(data.get('description', '')).strip(),
                "descriptionHTML": str(data.get('descriptionHTML', '')).strip(),
                "appId": str(data.get('appId', '')).strip(),
                "url": str(data.get('url', '')).strip(),
                
                # Performance Metrics
                "score": score,
                "ratings": self._safe_int(data.get('ratings')) or 0,
                "reviews": reviews_count,
                "installs": installs,
                "minInstalls": min_installs,
                "maxInstalls": self._safe_int(data.get('maxInstalls')) or min_installs,
                "realInstalls": real_installs,
                
                # Business Info
                "price": self._safe_float(data.get('price')) or 0.0,
                "free": bool(data.get('free', True)),
                "currency": str(data.get('currency', 'USD')),
                "offersIAP": bool(data.get('offersIAP', False)),
                
                # Category Info
                "genre": str(data.get('genre', '')).strip() or 'Unknown',
                "genreId": str(data.get('genreId', '')).strip(),
                "categories": data.get('categories', []),
                
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
                "updated": self._safe_int(data.get('updated')) or int(time.time()),
                "version": str(data.get('version', '')).strip() or 'Unknown',
                "recentChanges": str(data.get('recentChanges', '')).strip(),
                "size": str(data.get('size', '')).strip() or 'Unknown',
                "androidVersion": str(data.get('androidVersion', '')).strip() or 'Unknown',
                "androidVersionText": str(data.get('androidVersionText', '')).strip() or 'Unknown',
                
                # Review Distribution
                "histogram": [self._safe_int(x) or 0 for x in data.get('histogram', [0, 0, 0, 0, 0])],
                
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
            return self._get_minimal_data(data.get('appId', ''))

    def _calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional metrics"""
        try:
            metrics = {}
            
            # Review quality (0-100)
            if data['reviews'] > 0 and data['score'] > 0:
                review_quality = (data['score'] * 20) * (1 + (data['reviews'] / 100000))
                metrics['reviewQualityScore'] = min(100, review_quality)
            else:
                metrics['reviewQualityScore'] = 0
            
            # Engagement rate (0-100)
            if data['minInstalls'] > 0:
                engagement = (data['reviews'] / data['minInstalls']) * 1000
                metrics['engagementScore'] = min(100, engagement)
            else:
                metrics['engagementScore'] = 0
            
            # Growth metrics
            if data['updated'] > 0:
                days_since_update = (time.time() - data['updated']) / 86400
                if days_since_update > 0:
                    metrics['estimatedDailyInstalls'] = int(data['minInstalls'] / days_since_update)
                    metrics['estimatedMonthlyInstalls'] = metrics['estimatedDailyInstalls'] * 30
                else:
                    metrics['estimatedDailyInstalls'] = 0
                    metrics['estimatedMonthlyInstalls'] = 0
            else:
                metrics['estimatedDailyInstalls'] = 0
                metrics['estimatedMonthlyInstalls'] = 0
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return {
                'reviewQualityScore': 0,
                'engagementScore': 0,
                'estimatedDailyInstalls': 0,
                'estimatedMonthlyInstalls': 0
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
            if 0 <= data['score'] <= 5:
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

    def _extract_real_installs(self, installs_str: str, min_installs: int) -> int:
        """Extract real install count from string"""
        try:
            # Try to extract number from string (e.g., "1,000,000+" -> 1000000)
            matches = re.findall(r'[\d,]+', installs_str)
            if matches:
                # Remove commas and convert to int
                real_installs = int(matches[0].replace(',', ''))
                return max(real_installs, min_installs)
            return min_installs
        except Exception:
            return min_installs

    def _get_minimal_data(self, app_id: str) -> Dict[str, Any]:
        """Return minimal valid data structure"""
        return {
            "title": "Unknown",
            "summary": "",
            "description": "",
            "descriptionHTML": "",
            "appId": app_id,
            "url": f"https://play.google.com/store/apps/details?id={app_id}",
            "score": 0.0,
            "ratings": 0,
            "reviews": 0,
            "installs": "0+",
            "minInstalls": 0,
            "maxInstalls": 0,
            "realInstalls": 0,
            "price": 0.0,
            "free": True,
            "currency": "USD",
            "genre": "Unknown",
            "developer": "Unknown",
            "histogram": [0, 0, 0, 0, 0],
            "scrapedAt": datetime.now().isoformat(),
            "dataQuality": "minimal",
            "reviewQualityScore": 0,
            "engagementScore": 0,
            "estimatedDailyInstalls": 0,
            "estimatedMonthlyInstalls": 0
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