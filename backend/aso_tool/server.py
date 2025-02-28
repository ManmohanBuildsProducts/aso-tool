from fastapi import FastAPI, HTTPException, BackgroundTasks, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn
import os
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4
import asyncio

# Add backend directory to Python path
sys.path.append(str(Path(__file__).parent))

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
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router
api_router = APIRouter(prefix="/api")
app.include_router(api_router)

# Initialize analyzers
deepseek = DeepseekAnalyzer()
playstore = PlayStoreScraper()

class AppMetadata(BaseModel):
    package_name: str
    competitor_package_names: Optional[List[str]] = None
    keywords: Optional[List[str]] = None

@app.get("")
async def root():
    return {"message": "ASO Tool API"}

# Store analysis results
analysis_results = {}

@app.post("/api/analyze")
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

@app.get("/api/analyze/{task_id}")
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
    try:
        # Get app metadata
        app_data = await playstore.get_app_metadata(data.package_name)
        if "error" in app_data:
            analysis_results[task_id] = {
                "status": "error",
                "error": app_data["error"]
            }
            return
            
        analysis_results[task_id]["progress"] = 20
        
        # Get competitor metadata if provided
        competitor_data = []
        if data.competitor_package_names:
            for pkg_name in data.competitor_package_names:
                comp_data = await playstore.get_app_metadata(pkg_name)
                if "error" not in comp_data:
                    competitor_data.append(comp_data)
        
        analysis_results[task_id]["progress"] = 40
        
        # Process tasks concurrently
        tasks = []
        
        # Analyze app metadata
        tasks.append(deepseek.analyze_app_metadata(app_data))
        
        # Analyze competitor data if available
        if competitor_data:
            tasks.append(deepseek.analyze_competitor_metadata(app_data, competitor_data))
        else:
            tasks.append(None)
        
        # Get keyword suggestions if provided
        if data.keywords:
            tasks.append(asyncio.gather(*[
                deepseek.generate_keyword_suggestions(keyword)
                for keyword in data.keywords
            ]))
        else:
            tasks.append(None)
        
        # Get market trends
        tasks.append(deepseek.analyze_market_trends())
        
        # Optimize description
        if data.keywords:
            tasks.append(deepseek.optimize_description(
                app_data.get("description", ""),
                data.keywords
            ))
        else:
            tasks.append(None)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*[task for task in tasks if task is not None])
        
        analysis_results[task_id]["progress"] = 80
        
        # Process results
        result_index = 0
        analysis = results[result_index]
        result_index += 1
        
        competitor_analysis = None
        if competitor_data:
            competitor_analysis = results[result_index]
            result_index += 1
        
        keyword_suggestions = None
        if data.keywords:
            keyword_suggestions = results[result_index]
            result_index += 1
        
        market_trends = results[result_index]
        result_index += 1
        
        description_optimization = None
        if data.keywords:
            description_optimization = results[result_index]
        
        # Store final results
        analysis_results[task_id] = {
            "status": "completed",
            "progress": 100,
            "timestamp": datetime.utcnow(),
            "data": {
                "app_metadata": app_data,
                "analysis": analysis,
                "competitor_analysis": competitor_analysis,
                "keyword_suggestions": keyword_suggestions,
                "market_trends": market_trends,
                "description_optimization": description_optimization
            }
        }
        
    except Exception as e:
        logger.error(f"Error in process_analysis: {e}")
        analysis_results[task_id] = {
            "status": "error",
            "error": str(e)
        }

@app.get("/api/search")
async def search_keyword(keyword: str, limit: int = 10):
    try:
        results = await playstore.search_keywords(keyword, limit)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error in search_keyword: {e}")
        return {"error": str(e)}

@app.get("/api/similar")
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