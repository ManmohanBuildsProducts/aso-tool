from fastapi import FastAPI, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import sys
import asyncio
from uuid import uuid4
import json
from bson import ObjectId

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from aso_tool.external_integrations.deepseek_analyzer import DeepseekAnalyzer
from aso_tool.external_integrations.playstore_scraper import PlayStoreScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', "")
client = AsyncIOMotorClient(mongo_url)
db = client.aso_tool

# Create indexes
async def setup_db():
    """Setup MongoDB indexes"""
    try:
        # Jobs collection
        await db.jobs.create_index("job_id", unique=True)
        await db.jobs.create_index("updated_at")
        await db.jobs.create_index("status")
        
        # App cache collection
        await db.app_cache.create_index("package_name", unique=True)
        await db.app_cache.create_index("updated_at")
        
        logger.info("MongoDB indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating MongoDB indexes: {e}")

# Setup database
asyncio.create_task(setup_db())

# FastAPI app setup
app = FastAPI(root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
deepseek = DeepseekAnalyzer()
playstore = PlayStoreScraper()

class AppMetadata(BaseModel):
    package_name: str
    competitor_package_names: Optional[List[str]] = None
    keywords: Optional[List[str]] = None

class JobStatus(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    app_data: Optional[Dict] = None
    competitor_data: Optional[List[Dict]] = None
    analysis: Optional[Dict] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "ASO Tool API"}

# Store analysis results
analysis_results = {}

@app.post("/analyze")
async def analyze_app(data: AppMetadata, background_tasks: BackgroundTasks):
    """Start app analysis job"""
    try:
        # Generate job ID
        job_id = str(uuid4())
        now = datetime.utcnow()
        
        # Create job document
        job = {
            "job_id": job_id,
            "status": "processing",
            "created_at": now,
            "updated_at": now,
            "package_name": data.package_name,
            "competitor_package_names": data.competitor_package_names,
            "keywords": data.keywords
        }
        
        # Store in MongoDB
        await db.jobs.insert_one(job)
        logger.info(f"Created job {job_id} for {data.package_name}")
        
        # Start background processing
        background_tasks.add_task(process_analysis, job_id, data)
        
        return {
            "job_id": job_id,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error creating analysis job: {e}")
        return {"error": str(e)}

@app.get("/analyze/{job_id}")
async def get_analysis_result(job_id: str):
    """Get analysis job status and results"""
    try:
        # Get job from MongoDB
        job = await db.jobs.find_one({"job_id": job_id})
        if not job:
            return {"error": "Job not found"}
            
        # Convert ObjectId to string for JSON serialization
        if "_id" in job:
            job["_id"] = str(job["_id"])
            
        # Check if job has expired (older than 24 hours)
        if job["status"] == "completed":
            age = datetime.utcnow() - job["updated_at"]
            if age > timedelta(hours=24):
                await db.jobs.delete_one({"job_id": job_id})
                return {"error": "Job results expired"}
        
        return job
        
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        return {"error": str(e)}

async def process_analysis(job_id: str, data: AppMetadata):
    """Process app analysis job"""
    try:
        logger.info(f"Starting analysis for job {job_id}")
        
        # Get app metadata with cache check
        logger.info(f"Fetching app metadata for {data.package_name}")
        cached_app = await db.app_cache.find_one({
            "package_name": data.package_name,
            "updated_at": {"$gte": datetime.utcnow() - timedelta(hours=24)}
        })
        
        if cached_app:
            logger.info("Using cached app metadata")
            app_data = cached_app["data"]
        else:
            logger.info("Fetching fresh app metadata")
            app_data = await playstore.get_app_metadata(data.package_name)
            if "error" in app_data:
                logger.error(f"Error fetching app metadata: {app_data['error']}")
                await db.jobs.update_one(
                    {"job_id": job_id},
                    {
                        "$set": {
                            "status": "error",
                            "error": app_data["error"],
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                return
            
            # Cache app data
            await db.app_cache.update_one(
                {"package_name": data.package_name},
                {
                    "$set": {
                        "data": app_data,
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
        
        # Get competitor metadata if provided
        competitor_data = []
        if data.competitor_package_names:
            logger.info("Fetching competitor metadata")
            for pkg_name in data.competitor_package_names:
                try:
                    # Check cache first
                    cached_competitor = await db.app_cache.find_one({
                        "package_name": pkg_name,
                        "updated_at": {"$gte": datetime.utcnow() - timedelta(hours=24)}
                    })
                    
                    if cached_competitor:
                        logger.info(f"Using cached data for {pkg_name}")
                        competitor_data.append(cached_competitor["data"])
                    else:
                        logger.info(f"Fetching fresh data for {pkg_name}")
                        await asyncio.sleep(2)  # Rate limiting
                        comp_data = await playstore.get_app_metadata(pkg_name)
                        if "error" not in comp_data:
                            competitor_data.append(comp_data)
                            # Cache competitor data
                            await db.app_cache.update_one(
                                {"package_name": pkg_name},
                                {
                                    "$set": {
                                        "data": comp_data,
                                        "updated_at": datetime.utcnow()
                                    }
                                },
                                upsert=True
                            )
                except Exception as e:
                    logger.warning(f"Error fetching competitor data for {pkg_name}: {e}")
        
        # Update job with app and competitor data
        await db.jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "app_data": app_data,
                    "competitor_data": competitor_data,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Run analysis with DeepSeek
        logger.info("Starting DeepSeek analysis")
        analysis_results = {}
        
        try:
            # Analyze app metadata
            app_analysis = await deepseek.analyze_app_metadata(app_data)
            analysis_results["app_analysis"] = app_analysis
            
            # Analyze competitor data if available
            if competitor_data:
                competitor_analysis = await deepseek.analyze_competitor_metadata(app_data, competitor_data)
                analysis_results["competitor_analysis"] = competitor_analysis
            
            # Get keyword suggestions if provided
            if data.keywords:
                keyword_suggestions = await asyncio.gather(*[
                    deepseek.generate_keyword_suggestions(keyword)
                    for keyword in data.keywords
                ])
                analysis_results["keyword_suggestions"] = keyword_suggestions
            
            # Get market trends
            market_trends = await deepseek.analyze_market_trends()
            analysis_results["market_trends"] = market_trends
            
            # Optimize description if keywords provided
            if data.keywords and app_data.get("description"):
                description_optimization = await deepseek.optimize_description(
                    app_data.get("description", ""),
                    data.keywords
                )
                analysis_results["description_optimization"] = description_optimization
            
        except Exception as e:
            logger.error(f"Error in DeepSeek analysis: {e}")
            analysis_results["error"] = str(e)
        
        # Update job with analysis results
        await db.jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "completed",
                    "analysis": analysis_results,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        logger.info(f"Analysis completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Error in process_analysis: {e}")
        await db.jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "error",
                    "error": str(e),
                    "updated_at": datetime.utcnow()
                }
            }
        )

@app.get("/search")
async def search_keyword(keyword: str, limit: int = 10):
    try:
        results = await playstore.search_keywords(keyword, limit)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error in search_keyword: {e}")
        return {"error": str(e)}

@app.get("/similar")
async def get_similar_apps(package_name: str, limit: int = 5):
    try:
        results = await playstore.get_similar_apps(package_name, limit)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error in get_similar_apps: {e}")
        return {"error": str(e)}

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()