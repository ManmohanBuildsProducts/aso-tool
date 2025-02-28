from fastapi import FastAPI, HTTPException
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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

@app.get("/")
async def root():
    return {"message": "ASO Tool API"}

@app.post("/api/analyze")
async def analyze_app(data: AppMetadata):
    try:
        # Get app metadata
        app_data = await playstore.get_app_metadata(data.package_name)
        if "error" in app_data:
            return {"error": app_data["error"]}
            
        # Get competitor metadata if provided
        competitor_data = []
        if data.competitor_package_names:
            for pkg_name in data.competitor_package_names:
                comp_data = await playstore.get_app_metadata(pkg_name)
                if "error" not in comp_data:
                    competitor_data.append(comp_data)
        
        # Analyze app metadata
        analysis = await deepseek.analyze_app_metadata(app_data)
        
        # Analyze competitor data if available
        competitor_analysis = None
        if competitor_data:
            competitor_analysis = await deepseek.analyze_competitor_metadata(app_data, competitor_data)
        
        # Get keyword suggestions if provided
        keyword_suggestions = []
        if data.keywords:
            for keyword in data.keywords:
                suggestion = await deepseek.generate_keyword_suggestions(keyword)
                if "error" not in suggestion:
                    keyword_suggestions.append(suggestion)
        
        # Get market trends
        market_trends = await deepseek.analyze_market_trends()
        
        # Optimize description
        description_optimization = None
        if data.keywords:
            description_optimization = await deepseek.optimize_description(
                app_data.get("description", ""),
                data.keywords
            )
        
        return {
            "app_metadata": app_data,
            "analysis": analysis,
            "competitor_analysis": competitor_analysis,
            "keyword_suggestions": keyword_suggestions,
            "market_trends": market_trends,
            "description_optimization": description_optimization
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_app: {e}")
        return {"error": str(e)}

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