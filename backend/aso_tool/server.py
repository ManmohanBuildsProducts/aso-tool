from fastapi import FastAPI, BackgroundTasks, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import sys
import asyncio
from uuid import uuid4
import json
from bson import ObjectId
from enum import Enum
import aiohttp
from asyncio import TimeoutError
import time
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def analyze_task(task_name: str, task_data: Dict) -> Dict:
    """Helper function to run analysis tasks"""
    try:
        if task_name == "app_analysis":
            return await deepseek.analyze_app_metadata(task_data)
        elif task_name == "competitor_analysis":
            return await deepseek.analyze_competitor_metadata(
                task_data["app_data"],
                task_data["competitor_data"]
            )
        elif task_name == "keyword_suggestions":
            return await asyncio.gather(*[
                deepseek.generate_keyword_suggestions(keyword)
                for keyword in task_data["keywords"]
            ])
        elif task_name == "market_trends":
            return await deepseek.analyze_market_trends()
        elif task_name == "description_optimization":
            return await deepseek.optimize_description(
                task_data["description"],
                task_data["keywords"]
            )
        else:
            raise ValueError(f"Unknown task type: {task_name}")
    except Exception as e:
        logger.error(f"Error in {task_name}: {e}")
        return {"error": str(e)}

# Constants
RATE_LIMIT_REQUESTS = 10  # Number of requests allowed
RATE_LIMIT_WINDOW = 60    # Time window in seconds
JOB_TIMEOUT = 300        # Job timeout in seconds
CACHE_DURATION = 24 * 60 * 60  # Cache duration in seconds (24 hours)

# Rate limiting state
rate_limit_state = {
    "requests": [],
    "last_cleanup": time.time()
}

def rate_limit():
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_time = time.time()
            
            # Cleanup old requests
            if current_time - rate_limit_state["last_cleanup"] > RATE_LIMIT_WINDOW:
                rate_limit_state["requests"] = [
                    t for t in rate_limit_state["requests"]
                    if current_time - t < RATE_LIMIT_WINDOW
                ]
                rate_limit_state["last_cleanup"] = current_time
            
            # Check rate limit
            if len(rate_limit_state["requests"]) >= RATE_LIMIT_REQUESTS:
                oldest_request = min(rate_limit_state["requests"])
                if current_time - oldest_request < RATE_LIMIT_WINDOW:
                    wait_time = RATE_LIMIT_WINDOW - (current_time - oldest_request)
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Please wait {int(wait_time)} seconds."
                    )
            
            # Add current request
            rate_limit_state["requests"].append(current_time)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

async def cache_result(key: str, data: Any, db: AsyncIOMotorClient):
    """Cache result in MongoDB"""
    try:
        await db.cache.update_one(
            {"key": key},
            {
                "$set": {
                    "data": data,
                    "timestamp": datetime.utcnow()
                }
            },
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error caching result: {e}")

async def get_cached_result(key: str, db: AsyncIOMotorClient) -> Optional[Any]:
    """Get cached result from MongoDB"""
    try:
        result = await db.cache.find_one({
            "key": key,
            "timestamp": {
                "$gte": datetime.utcnow() - timedelta(seconds=CACHE_DURATION)
            }
        })
        return result["data"] if result else None
    except Exception as e:
        logger.error(f"Error getting cached result: {e}")
        return None

class JobStatus(str, Enum):
    """Job status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    TIMEOUT = "timeout"

class JobResponse(BaseModel):
    """Job response model"""
    job_id: str
    status: JobStatus
    progress: Optional[int] = 0
    data: Optional[Dict] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class AnalysisRequest(BaseModel):
    """Analysis request model"""
    package_name: str
    competitor_package_names: Optional[List[str]] = Field(default_factory=list)
    keywords: Optional[List[str]] = Field(default_factory=list)

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

@app.post("/analyze", response_model=JobResponse)
@rate_limit()
async def analyze_app(data: AnalysisRequest, background_tasks: BackgroundTasks) -> JobResponse:
    """Start app analysis job"""
    try:
        # Generate job ID and timestamps
        job_id = str(uuid4())
        now = datetime.utcnow()
        
        # Create job document
        job = {
            "job_id": job_id,
            "status": JobStatus.PENDING,
            "progress": 0,
            "created_at": now,
            "updated_at": now,
            "package_name": data.package_name,
            "competitor_package_names": data.competitor_package_names,
            "keywords": data.keywords,
            "timeout_at": now + timedelta(seconds=JOB_TIMEOUT)
        }
        
        # Check cache first
        cache_key = f"analysis_{data.package_name}"
        cached_result = await get_cached_result(cache_key, db)
        
        if cached_result:
            logger.info(f"Using cached result for {data.package_name}")
            job.update({
                "status": JobStatus.COMPLETED,
                "progress": 100,
                "data": cached_result
            })
        else:
            logger.info(f"Starting new analysis for {data.package_name}")
            job["status"] = JobStatus.PROCESSING
            background_tasks.add_task(process_analysis, job_id, data)
        
        # Store in MongoDB
        await db.jobs.insert_one(job)
        logger.info(f"Created job {job_id} for {data.package_name}")
        
        # Convert to response model
        response = JobResponse(
            job_id=job_id,
            status=job["status"],
            progress=job["progress"],
            data=job.get("data"),
            error=job.get("error"),
            created_at=job["created_at"],
            updated_at=job["updated_at"]
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating analysis job: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/analyze/{job_id}", response_model=JobResponse)
@rate_limit()
async def get_analysis_result(job_id: str) -> JobResponse:
    """Get analysis job status and results"""
    try:
        # Get job from MongoDB
        job = await db.jobs.find_one({"job_id": job_id})
        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )
            
        # Convert ObjectId to string for JSON serialization
        if "_id" in job:
            job["_id"] = str(job["_id"])
            
        # Check if job has expired
        if job["status"] == JobStatus.COMPLETED:
            age = datetime.utcnow() - job["updated_at"]
            if age > timedelta(seconds=CACHE_DURATION):
                await db.jobs.delete_one({"job_id": job_id})
                raise HTTPException(
                    status_code=404,
                    detail="Job results expired"
                )
        
        # Check for timeout
        if job["status"] == JobStatus.PROCESSING:
            if datetime.utcnow() > job["timeout_at"]:
                # Update job status to timeout
                await db.jobs.update_one(
                    {"job_id": job_id},
                    {
                        "$set": {
                            "status": JobStatus.TIMEOUT,
                            "error": "Job timed out",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                job.update({
                    "status": JobStatus.TIMEOUT,
                    "error": "Job timed out",
                    "updated_at": datetime.utcnow()
                })
        
        # Convert to response model
        response = JobResponse(
            job_id=job["job_id"],
            status=JobStatus(job["status"]),
            progress=job.get("progress", 0),
            data=job.get("data"),
            error=job.get("error"),
            created_at=job["created_at"],
            updated_at=job["updated_at"]
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

async def process_analysis(job_id: str, data: AnalysisRequest):
    """Process app analysis job"""
    try:
        logger.info(f"Starting analysis for job {job_id}")
        
        # Update job status to processing
        await db.jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": JobStatus.PROCESSING,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Get app metadata with cache check
        logger.info(f"Fetching app metadata for {data.package_name}")
        cache_key = f"app_{data.package_name}"
        app_data = await get_cached_result(cache_key, db)
        
        if not app_data:
            logger.info("Fetching fresh app metadata")
            try:
                app_data = await asyncio.wait_for(
                    playstore.get_app_metadata(data.package_name),
                    timeout=30  # 30 seconds timeout
                )
                if "error" in app_data:
                    raise Exception(app_data["error"])
                
                # Cache app data
                await cache_result(cache_key, app_data, db)
            except TimeoutError:
                raise Exception("Timeout fetching app metadata")
            except Exception as e:
                logger.error(f"Error fetching app metadata: {e}")
                await db.jobs.update_one(
                    {"job_id": job_id},
                    {
                        "$set": {
                            "status": JobStatus.ERROR,
                            "error": str(e),
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                return
        
        # Update progress
        await db.jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "progress": 20,
                    "app_data": app_data,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Get competitor metadata if provided
        competitor_data = []
        if data.competitor_package_names:
            logger.info("Fetching competitor metadata")
            for pkg_name in data.competitor_package_names:
                try:
                    # Check cache first
                    cache_key = f"app_{pkg_name}"
                    comp_data = await get_cached_result(cache_key, db)
                    
                    if not comp_data:
                        logger.info(f"Fetching fresh data for {pkg_name}")
                        await asyncio.sleep(2)  # Rate limiting
                        comp_data = await asyncio.wait_for(
                            playstore.get_app_metadata(pkg_name),
                            timeout=30  # 30 seconds timeout
                        )
                        if "error" in comp_data:
                            logger.warning(f"Error in competitor data: {comp_data['error']}")
                            continue
                        
                        # Cache competitor data
                        await cache_result(cache_key, comp_data, db)
                    
                    competitor_data.append(comp_data)
                    
                except TimeoutError:
                    logger.warning(f"Timeout fetching competitor data for {pkg_name}")
                    continue
                except Exception as e:
                    logger.warning(f"Error fetching competitor data for {pkg_name}: {e}")
                    continue
        
        # Update progress
        await db.jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "progress": 40,
                    "competitor_data": competitor_data,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Run analysis with DeepSeek
        logger.info("Starting DeepSeek analysis")
        analysis_results = {}
        
        try:
            # Prepare analysis tasks
            tasks = []
            
            # App analysis
            tasks.append(("app_analysis", app_data))
            
            # Competitor analysis
            if competitor_data:
                tasks.append(("competitor_analysis", {
                    "app_data": app_data,
                    "competitor_data": competitor_data
                }))
            
            # Keyword suggestions
            if data.keywords:
                tasks.append(("keyword_suggestions", {
                    "keywords": data.keywords
                }))
            
            # Market trends
            tasks.append(("market_trends", {}))
            
            # Description optimization
            if data.keywords and app_data.get("description"):
                tasks.append(("description_optimization", {
                    "description": app_data["description"],
                    "keywords": data.keywords
                }))
            
            # Process tasks with proper error handling
            total_tasks = len(tasks)
            completed_tasks = 0
            
            for task_name, task_data in tasks:
                try:
                    # Check cache first
                    cache_key = f"analysis_{task_name}_{data.package_name}"
                    result = await get_cached_result(cache_key, db)
                    
                    if not result:
                        # Run analysis with timeout
                        result = await asyncio.wait_for(
                            analyze_task(task_name, task_data),
                            timeout=60
                        )
                        
                        # Cache successful results
                        if "error" not in result:
                            await cache_result(cache_key, result, db)
                    
                    analysis_results[task_name] = result
                    
                    # Update progress
                    completed_tasks += 1
                    progress = 40 + (completed_tasks * 60 // total_tasks)
                    
                    await db.jobs.update_one(
                        {"job_id": job_id},
                        {
                            "$set": {
                                "progress": progress,
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                    
                except TimeoutError:
                    logger.error(f"Timeout in {task_name}")
                    analysis_results[task_name] = {"error": "Analysis timed out"}
                except Exception as e:
                    logger.error(f"Error in {task_name}: {e}")
                    analysis_results[task_name] = {"error": str(e)}
            
        except Exception as e:
            logger.error(f"Error in DeepSeek analysis: {e}")
            analysis_results["error"] = str(e)
        
        # Cache final results
        cache_key = f"analysis_{data.package_name}"
        await cache_result(cache_key, {
            "app_data": app_data,
            "competitor_data": competitor_data,
            "analysis": analysis_results
        }, db)
        
        # Update job with final results
        await db.jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": JobStatus.COMPLETED,
                    "progress": 100,
                    "data": {
                        "app_data": app_data,
                        "competitor_data": competitor_data,
                        "analysis": analysis_results
                    },
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
                    "status": JobStatus.ERROR,
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