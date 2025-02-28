import aiohttp
import asyncio
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }
        self.base_url = "https://play.google.com"

    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content from Play Store"""
        try:
            timeout = aiohttp.ClientTimeout(total=30)  # 30 seconds timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=self.headers, allow_redirects=True) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 404:
                        logger.error(f"App not found: {url}")
                        return None
                    elif response.status == 429:
                        logger.error("Rate limit exceeded")
                        await asyncio.sleep(5)  # Wait 5 seconds before retry
                        return await self._fetch_page(url)  # Retry once
                    else:
                        logger.error(f"Error fetching page: {response.status}")
                        return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching page: {url}")
            return None
        except Exception as e:
            logger.error(f"Error in _fetch_page: {e}")
            return None

    def _extract_app_data(self, html_content: str) -> Dict:
        """Extract app metadata from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract app name
            app_name = ""
            name_tag = soup.find('h1', {'itemprop': 'name'})
            if not name_tag:
                name_tag = soup.find('h1', {'class': 'Fd93Bb'})
            if name_tag:
                app_name = name_tag.text.strip()
            
            # Extract description
            description = ""
            desc_tag = soup.find('div', {'data-g-id': 'description'})
            if not desc_tag:
                desc_tag = soup.find('div', {'class': 'bARER'})
            if desc_tag:
                description = desc_tag.text.strip()
            
            # Extract rating
            rating = 0.0
            rating_tag = soup.find('div', {'class': 'BHMmbe'})
            if not rating_tag:
                rating_tag = soup.find('div', {'class': 'jILTFe'})
            if rating_tag:
                try:
                    rating = float(rating_tag.text.replace(',', '.'))
                except ValueError:
                    pass
            
            # Extract reviews count
            reviews = 0
            reviews_tag = soup.find('span', {'class': 'AYi5wd TBRnV'})
            if not reviews_tag:
                reviews_tag = soup.find('div', {'class': 'wVqUob'})
            if reviews_tag:
                try:
                    reviews = int(re.sub(r'[^\d]', '', reviews_tag.text))
                except ValueError:
                    pass
            
            # Extract category
            category = ""
            category_tag = soup.find('a', {'itemprop': 'genre'})
            if not category_tag:
                category_tag = soup.find('a', {'class': 'wXUyZd'})
            if category_tag:
                category = category_tag.text.strip()
            
            # Extract installs
            installs = "0+"
            installs_tag = soup.find('div', text=re.compile(r'.*installs', re.IGNORECASE))
            if installs_tag:
                next_span = installs_tag.find_next('span')
                if next_span:
                    installs = next_span.text.strip()
            
            # Extract developer name
            developer = ""
            dev_tag = soup.find('div', {'class': 'qQKdcc'})
            if not dev_tag:
                dev_tag = soup.find('span', {'class': 'T32cc'})
            if dev_tag:
                developer = dev_tag.text.strip()
            
            # Extract screenshots
            screenshots = []
            screenshot_div = soup.find('div', {'class': 'SgoUSc'})
            if not screenshot_div:
                screenshot_div = soup.find('div', {'class': 'TdqJUe'})
            if screenshot_div:
                for img in screenshot_div.find_all('img'):
                    if 'src' in img.attrs:
                        src = img['src']
                        if src.startswith('//'):
                            src = 'https:' + src
                        screenshots.append(src)
            
            # Extract additional metadata
            metadata = {
                "title": app_name,
                "description": description,
                "rating": rating,
                "reviews_count": reviews,
                "category": category,
                "installs": installs,
                "developer": developer,
                "screenshots": screenshots[:5]  # Limit to first 5 screenshots
            }
            
            # Extract update date
            update_tag = soup.find('div', text=re.compile(r'Updated', re.IGNORECASE))
            if update_tag:
                next_span = update_tag.find_next('span')
                if next_span:
                    metadata["last_updated"] = next_span.text.strip()
            
            # Extract size
            size_tag = soup.find('div', text=re.compile(r'Size', re.IGNORECASE))
            if size_tag:
                next_span = size_tag.find_next('span')
                if next_span:
                    metadata["size"] = next_span.text.strip()
            
            # Extract version
            version_tag = soup.find('div', text=re.compile(r'Version', re.IGNORECASE))
            if version_tag:
                next_span = version_tag.find_next('span')
                if next_span:
                    metadata["version"] = next_span.text.strip()
            
            # Extract content rating
            content_rating_tag = soup.find('div', text=re.compile(r'Content Rating', re.IGNORECASE))
            if content_rating_tag:
                next_span = content_rating_tag.find_next('span')
                if next_span:
                    metadata["content_rating"] = next_span.text.strip()
            
            # Extract what's new
            whats_new_tag = soup.find('div', {'class': 'W4P4ne'})
            if whats_new_tag:
                metadata["whats_new"] = whats_new_tag.text.strip()
            
            return metadata
            
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
            app_cards = soup.find_all('div', {'class': 'VfPpkd-aGsRMb'})
            if not app_cards:
                app_cards = soup.find_all('div', {'class': 'ULeU3b'})
            
            for card in app_cards[:limit]:
                try:
                    # Extract app name
                    name = ""
                    name_tag = card.find('div', {'class': 'Epkrse'})
                    if not name_tag:
                        name_tag = card.find('div', {'class': 'ubGTjb'})
                    if name_tag:
                        name = name_tag.text.strip()
                    
                    # Extract package name from link
                    package_name = ""
                    link = card.find('a', {'class': 'Si6A0c'})
                    if not link:
                        link = card.find('a', {'class': 'poRVub'})
                    if link and 'href' in link.attrs:
                        match = re.search(r'id=([^&]+)', link['href'])
                        if match:
                            package_name = match.group(1)
                    
                    # Extract rating
                    rating = 0.0
                    rating_tag = card.find('div', {'class': 'LrNMN'})
                    if not rating_tag:
                        rating_tag = card.find('div', {'class': 'pf5lIe'})
                    if rating_tag:
                        try:
                            rating_text = rating_tag.find('div')['aria-label']
                            rating = float(re.search(r'(\d+(\.\d+)?)', rating_text).group(1))
                        except (AttributeError, ValueError, TypeError):
                            pass
                    
                    # Extract additional metadata
                    metadata = {
                        "name": name,
                        "package_name": package_name,
                        "rating": rating
                    }
                    
                    # Extract developer name
                    dev_tag = card.find('div', {'class': 'wMUdtb'})
                    if dev_tag:
                        metadata["developer"] = dev_tag.text.strip()
                    
                    # Extract price
                    price_tag = card.find('span', {'class': 'VfPpfd'})
                    if price_tag:
                        metadata["price"] = price_tag.text.strip()
                    
                    # Extract icon URL
                    icon_tag = card.find('img', {'class': 'T75of'})
                    if icon_tag and 'src' in icon_tag.attrs:
                        src = icon_tag['src']
                        if src.startswith('//'):
                            src = 'https:' + src
                        metadata["icon_url"] = src
                    
                    results.append(metadata)
                    
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
            similar_section = soup.find('div', text=re.compile(r'Similar apps', re.IGNORECASE))
            if similar_section:
                # Try different class names for similar apps container
                similar_container = similar_section.find_parent('div')
                if similar_container:
                    similar_apps = similar_container.find_all('div', {'class': ['VfPpkd-aGsRMb', 'ULeU3b']})
                    
                    for app in similar_apps[:limit]:
                        try:
                            # Extract app name
                            name = ""
                            name_tag = app.find('div', {'class': ['Epkrse', 'ubGTjb']})
                            if name_tag:
                                name = name_tag.text.strip()
                            
                            # Extract package name from link
                            package_name = ""
                            link = app.find('a', {'class': ['Si6A0c', 'poRVub']})
                            if link and 'href' in link.attrs:
                                match = re.search(r'id=([^&]+)', link['href'])
                                if match:
                                    package_name = match.group(1)
                            
                            # Extract rating
                            rating = 0.0
                            rating_tag = app.find('div', {'class': ['LrNMN', 'pf5lIe']})
                            if rating_tag:
                                try:
                                    rating_text = rating_tag.find('div')['aria-label']
                                    rating = float(re.search(r'(\d+(\.\d+)?)', rating_text).group(1))
                                except (AttributeError, ValueError, TypeError):
                                    pass
                            
                            # Extract additional metadata
                            metadata = {
                                "name": name,
                                "package_name": package_name,
                                "rating": rating
                            }
                            
                            # Extract developer name
                            dev_tag = app.find('div', {'class': 'wMUdtb'})
                            if dev_tag:
                                metadata["developer"] = dev_tag.text.strip()
                            
                            # Extract price
                            price_tag = app.find('span', {'class': 'VfPpfd'})
                            if price_tag:
                                metadata["price"] = price_tag.text.strip()
                            
                            # Extract icon URL
                            icon_tag = app.find('img', {'class': 'T75of'})
                            if icon_tag and 'src' in icon_tag.attrs:
                                src = icon_tag['src']
                                if src.startswith('//'):
                                    src = 'https:' + src
                                metadata["icon_url"] = src
                            
                            results.append(metadata)
                            
                        except Exception as e:
                            logger.error(f"Error processing similar app: {e}")
                            continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting similar apps: {e}")
            return []