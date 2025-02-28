import aiohttp
import asyncio
import random
import logging
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class PlayStoreScraper:
    def __init__(self):
        self.base_url = "https://play.google.com/store/search"
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]

    async def _get_random_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    async def search_keyword(self, keyword: str, max_results: int = 100) -> List[Dict]:
        """
        Search Play Store for a keyword and return app rankings
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "q": keyword,
                    "c": "apps",
                    "hl": "en",
                    "gl": "US"
                }
                
                headers = await self._get_random_headers()
                
                async with session.get(self.base_url, params=params, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Error searching keyword {keyword}: {response.status}")
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    results = []
                    rank = 1
                    
                    # Find app listings
                    app_elements = soup.find_all('div', {'class': 'VfPpkd-EScbFb-JIbuQc'})
                    
                    for app in app_elements[:max_results]:
                        try:
                            app_link = app.find('a')
                            if not app_link:
                                continue
                                
                            href = app_link.get('href', '')
                            if not href or 'details?id=' not in href:
                                continue
                                
                            package_name = href.split('details?id=')[1].split('&')[0]
                            
                            results.append({
                                "keyword": keyword,
                                "package_name": package_name,
                                "rank": rank,
                                "timestamp": datetime.utcnow().isoformat()
                            })
                            
                            rank += 1
                            
                        except Exception as e:
                            logger.error(f"Error parsing app element: {e}")
                            continue
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Error in search_keyword: {e}")
            return []

    async def get_app_metadata(self, package_name: str) -> Optional[Dict]:
        """
        Get metadata for a specific app
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://play.google.com/store/apps/details?id={package_name}&hl=en"
                headers = await self._get_random_headers()
                
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Error fetching app metadata for {package_name}: {response.status}")
                        return None
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    metadata = {
                        "package_name": package_name,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Extract app name
                    app_name = soup.find('h1', {'itemprop': 'name'})
                    if app_name:
                        metadata["name"] = app_name.text.strip()
                    
                    # Extract description
                    description = soup.find('div', {'itemprop': 'description'})
                    if description:
                        metadata["description"] = description.text.strip()
                    
                    # Extract category
                    category = soup.find('a', {'itemprop': 'genre'})
                    if category:
                        metadata["category"] = category.text.strip()
                    
                    return metadata
                    
        except Exception as e:
            logger.error(f"Error in get_app_metadata: {e}")
            return None

# Example usage
async def main():
    scraper = PlayStoreScraper()
    results = await scraper.search_keyword("b2b wholesale")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
