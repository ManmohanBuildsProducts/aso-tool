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
    try:
        # Generate unique task ID
        task_id = str(uuid4())
        
        # Store initial state
        analysis_results[task_id] = {
            "status": "processing",
            "progress": 0,
            "data": None,
            "error": None
        }
        
        # Start background task
        background_tasks.add_task(process_analysis, task_id, data)
        
        return {
            "task_id": task_id,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_app: {e}")
        return {"error": str(e)}

@app.get("/analyze/{task_id}")
async def get_analysis_result(task_id: str):
    try:
        if task_id not in analysis_results:
            return {"error": "Task not found"}
            
        result = analysis_results[task_id]
        
        # Clean up completed tasks after 1 hour
        if result["status"] == "completed" and "timestamp" in result:
            if (datetime.utcnow() - result["timestamp"]).total_seconds() > 3600:
                del analysis_results[task_id]
                return {"error": "Task expired"}
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting analysis result: {e}")
        return {"error": str(e)}

async def process_analysis(task_id: str, data: AppMetadata):
    """Process app analysis task"""
    try:
        logger.info(f"Starting analysis for task {task_id}")
        
        # Update task status
        analysis_results[task_id]["status"] = "processing"
        analysis_results[task_id]["progress"] = 0
        
        # Get app metadata
        logger.info(f"Fetching app metadata for {data.package_name}")
        app_data = await playstore.get_app_metadata(data.package_name)
        if "error" in app_data:
            logger.error(f"Error fetching app metadata: {app_data['error']}")
            analysis_results[task_id].update({
                "status": "error",
                "error": app_data["error"]
            })
            return
            
        analysis_results[task_id]["progress"] = 20
        logger.info("App metadata fetched successfully")
        
        # Get competitor metadata if provided
        competitor_data = []
        if data.competitor_package_names:
            logger.info("Fetching competitor metadata")
            for pkg_name in data.competitor_package_names:
                try:
                    comp_data = await playstore.get_app_metadata(pkg_name)
                    if "error" not in comp_data:
                        competitor_data.append(comp_data)
                except Exception as e:
                    logger.warning(f"Error fetching competitor data for {pkg_name}: {e}")
        
        analysis_results[task_id]["progress"] = 40
        logger.info("Competitor metadata fetched successfully")
        
        # Process tasks concurrently
        logger.info("Starting concurrent analysis tasks")
        tasks = []
        task_results = {}
        
        # Analyze app metadata
        tasks.append(("app_analysis", deepseek.analyze_app_metadata(app_data)))
        
        # Analyze competitor data if available
        if competitor_data:
            tasks.append(("competitor_analysis", deepseek.analyze_competitor_metadata(app_data, competitor_data)))
        
        # Get keyword suggestions if provided
        if data.keywords:
            tasks.append(("keyword_suggestions", asyncio.gather(*[
                deepseek.generate_keyword_suggestions(keyword)
                for keyword in data.keywords
            ])))
        
        # Get market trends
        tasks.append(("market_trends", deepseek.analyze_market_trends()))
        
        # Optimize description
        if data.keywords and app_data.get("description"):
            tasks.append(("description_optimization", deepseek.optimize_description(
                app_data.get("description", ""),
                data.keywords
            )))
        
        # Wait for all tasks to complete with timeout
        logger.info("Waiting for analysis tasks to complete")
        try:
            for task_name, task in tasks:
                try:
                    result = await asyncio.wait_for(task, timeout=60)  # 60 seconds timeout
                    task_results[task_name] = result
                    analysis_results[task_id]["progress"] += int(40 / len(tasks))
                    logger.info(f"Task {task_name} completed successfully")
                except asyncio.TimeoutError:
                    logger.error(f"Task {task_name} timed out")
                    task_results[task_name] = {"error": "Task timed out"}
                except Exception as e:
                    logger.error(f"Error in task {task_name}: {e}")
                    task_results[task_name] = {"error": str(e)}
        except Exception as e:
            logger.error(f"Error processing tasks: {e}")
            analysis_results[task_id].update({
                "status": "error",
                "error": str(e)
            })
            return
        
        # Store final results
        logger.info("Storing final results")
        analysis_results[task_id].update({
            "status": "completed",
            "progress": 100,
            "timestamp": datetime.utcnow(),
            "data": {
                "app_metadata": app_data,
                "analysis": task_results.get("app_analysis"),
                "competitor_analysis": task_results.get("competitor_analysis"),
                "keyword_suggestions": task_results.get("keyword_suggestions"),
                "market_trends": task_results.get("market_trends"),
                "description_optimization": task_results.get("description_optimization")
            }
        })
        logger.info(f"Analysis completed for task {task_id}")
        
    except Exception as e:
        logger.error(f"Error in process_analysis: {e}")
        analysis_results[task_id].update({
            "status": "error",
            "error": str(e)
        })

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