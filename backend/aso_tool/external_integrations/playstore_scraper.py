import aiohttp
import logging
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
import json

logger = logging.getLogger(__name__)

class PlayStoreScraper:
    def __init__(self):
        """Initialize Play Store scraper"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = "https://play.google.com"

    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content from Play Store"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.error(f"Error fetching page: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error in _fetch_page: {e}")
            return None

    def _extract_app_data(self, html_content: str) -> Dict:
        """Extract app metadata from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract app name
            app_name = soup.find('h1', {'itemprop': 'name'})
            app_name = app_name.text.strip() if app_name else ""
            
            # Extract description
            description = soup.find('div', {'data-g-id': 'description'})
            description = description.text.strip() if description else ""
            
            # Extract rating
            rating = soup.find('div', {'class': 'BHMmbe'})
            rating = float(rating.text.replace(',', '.')) if rating else 0.0
            
            # Extract reviews count
            reviews = soup.find('span', {'class': 'AYi5wd TBRnV'})
            reviews = int(re.sub(r'[^\d]', '', reviews.text)) if reviews else 0
            
            # Extract category
            category = soup.find('a', {'itemprop': 'genre'})
            category = category.text.strip() if category else ""
            
            # Extract installs
            installs = soup.find('div', text=re.compile(r'.*installs'))
            installs = installs.find_next('span').text.strip() if installs else "0+"
            
            # Extract developer name
            developer = soup.find('div', {'class': 'qQKdcc'})
            developer = developer.text.strip() if developer else ""
            
            # Extract screenshots
            screenshots = []
            screenshot_div = soup.find('div', {'class': 'SgoUSc'})
            if screenshot_div:
                for img in screenshot_div.find_all('img'):
                    if 'src' in img.attrs:
                        screenshots.append(img['src'])
            
            return {
                "title": app_name,
                "description": description,
                "rating": rating,
                "reviews_count": reviews,
                "category": category,
                "installs": installs,
                "developer": developer,
                "screenshots": screenshots[:5]  # Limit to first 5 screenshots
            }
            
        except Exception as e:
            logger.error(f"Error extracting app data: {e}")
            return {}

    async def get_app_metadata(self, package_name: str) -> Dict:
        """Get app metadata from Play Store"""
        try:
            url = f"{self.base_url}/store/apps/details?id={package_name}"
            html_content = await self._fetch_page(url)
            
            if not html_content:
                return {"error": "Failed to fetch app page"}
            
            return self._extract_app_data(html_content)
            
        except Exception as e:
            logger.error(f"Error getting app metadata: {e}")
            return {"error": str(e)}

    async def search_keywords(self, keyword: str, limit: int = 10) -> List[Dict]:
        """Search Play Store for keyword and return top results"""
        try:
            url = f"{self.base_url}/store/search?q={keyword}&c=apps"
            html_content = await self._fetch_page(url)
            
            if not html_content:
                return []
            
            soup = BeautifulSoup(html_content, 'html.parser')
            results = []
            
            # Find app cards
            app_cards = soup.find_all('div', {'class': 'VfPpkd-EScbFb-JIbuQc'})
            
            for card in app_cards[:limit]:
                try:
                    # Extract app name
                    name = card.find('div', {'class': 'WsMG1c'})
                    name = name.text.strip() if name else ""
                    
                    # Extract package name from link
                    link = card.find('a', {'class': 'poRVub'})
                    package_name = ""
                    if link and 'href' in link.attrs:
                        match = re.search(r'id=([^&]+)', link['href'])
                        if match:
                            package_name = match.group(1)
                    
                    # Extract rating
                    rating = card.find('div', {'class': 'pf5lIe'})
                    rating = float(rating.find('div')['aria-label'].split()[1]) if rating else 0.0
                    
                    results.append({
                        "name": name,
                        "package_name": package_name,
                        "rating": rating
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing app card: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching keywords: {e}")
            return []

    async def get_similar_apps(self, package_name: str, limit: int = 5) -> List[Dict]:
        """Get similar apps from Play Store"""
        try:
            url = f"{self.base_url}/store/apps/details?id={package_name}"
            html_content = await self._fetch_page(url)
            
            if not html_content:
                return []
            
            soup = BeautifulSoup(html_content, 'html.parser')
            results = []
            
            # Find similar apps section
            similar_section = soup.find('div', text=re.compile(r'Similar apps'))
            if similar_section:
                similar_apps = similar_section.find_next('div').find_all('div', {'class': 'VfPpkd-EScbFb-JIbuQc'})
                
                for app in similar_apps[:limit]:
                    try:
                        # Extract app name
                        name = app.find('div', {'class': 'WsMG1c'})
                        name = name.text.strip() if name else ""
                        
                        # Extract package name from link
                        link = app.find('a', {'class': 'poRVub'})
                        package_name = ""
                        if link and 'href' in link.attrs:
                            match = re.search(r'id=([^&]+)', link['href'])
                            if match:
                                package_name = match.group(1)
                        
                        # Extract rating
                        rating = app.find('div', {'class': 'pf5lIe'})
                        rating = float(rating.find('div')['aria-label'].split()[1]) if rating else 0.0
                        
                        results.append({
                            "name": name,
                            "package_name": package_name,
                            "rating": rating
                        })
                        
                    except Exception as e:
                        logger.error(f"Error processing similar app: {e}")
                        continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting similar apps: {e}")
            return []