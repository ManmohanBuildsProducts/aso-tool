import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from .scraper import PlayStoreScraper
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

class RankingScheduler:
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client
        self.scraper = PlayStoreScraper()
        self.running = False
        
    async def start(self):
        """Start the ranking tracker scheduler"""
        if self.running:
            return
            
        self.running = True
        while self.running:
            try:
                await self._run_ranking_check()
                # Wait for 24 hours before next check
                await asyncio.sleep(24 * 60 * 60)
            except Exception as e:
                logger.error(f"Error in ranking scheduler: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def stop(self):
        """Stop the ranking tracker scheduler"""
        self.running = False
    
    async def _run_ranking_check(self):
        """Run a complete ranking check for all apps and keywords"""
        try:
            # Get all apps
            apps = await self.db.apps.find().to_list(length=100)
            if not apps:
                logger.warning("No apps found for tracking")
                return
                
            # Get all keywords
            keywords = await self.db.keywords.find().to_list(length=1000)
            if not keywords:
                logger.warning("No keywords found for tracking")
                return
            
            # Track rankings for each keyword
            for keyword in keywords:
                try:
                    results = await self.scraper.search_keyword(keyword["keyword"])
                    
                    # Store rankings for each app
                    for app in apps:
                        rank = next(
                            (r["rank"] for r in results 
                             if r["package_name"] == app["package_name"]),
                            None
                        )
                        
                        if rank is not None:
                            await self.db.rankings.insert_one({
                                "app_id": str(app["_id"]),
                                "keyword": keyword["keyword"],
                                "rank": rank,
                                "date": datetime.utcnow(),
                                "search_page_data": results[:10]  # Store top 10 results
                            })
                    
                    # Random delay between keywords to avoid rate limiting
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    logger.error(f"Error tracking keyword {keyword['keyword']}: {e}")
                    continue
            
            # Update app metadata
            for app in apps:
                try:
                    metadata = await self.scraper.get_app_metadata(app["package_name"])
                    if metadata:
                        await self.db.apps.update_one(
                            {"_id": app["_id"]},
                            {"$set": {"metadata": metadata}}
                        )
                except Exception as e:
                    logger.error(f"Error updating metadata for {app['package_name']}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in ranking check: {e}")
            raise

    async def force_check(self):
        """Force an immediate ranking check"""
        await self._run_ranking_check()