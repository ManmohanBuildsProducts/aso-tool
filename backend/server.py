from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel

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

# Initialize DeepSeek analyzer
from deepseek_analyzer import DeepseekAnalyzer
analyzer = DeepseekAnalyzer()

# Pydantic models
class AppMetadata(BaseModel):
    title: str
    description: str
    category: str
    keywords: List[str]
    package_name: Optional[str] = None
    ratings: Optional[Dict] = None
    installs: Optional[str] = None

class KeywordRequest(BaseModel):
    base_keyword: str
    industry: Optional[str] = "B2B wholesale"

class CompetitorRequest(BaseModel):
    app_metadata: Dict
    competitor_metadata: List[Dict]

class DescriptionRequest(BaseModel):
    current_description: str
    keywords: List[str]

class TrendRequest(BaseModel):
    category: Optional[str] = "B2B wholesale"

@app.post("/api/analyze/app/{app_id}")
async def analyze_app(app_id: str, metadata: AppMetadata):
    """Analyze app metadata and provide ASO recommendations"""
    try:
        logger.info(f"Analyzing app: {app_id}")
        result = await analyzer.analyze_app_metadata(metadata.dict())
        return result
    except Exception as e:
        logger.error(f"Error analyzing app: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/keywords")
async def analyze_keywords(request: KeywordRequest):
    """Generate keyword suggestions and analysis"""
    try:
        logger.info(f"Analyzing keywords: {request.base_keyword}")
        result = await analyzer.generate_keyword_suggestions(
            request.base_keyword,
            request.industry
        )
        return result
    except Exception as e:
        logger.error(f"Error analyzing keywords: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/competitors")
async def analyze_competitors(request: CompetitorRequest):
    """Analyze competitor metadata and provide insights"""
    try:
        logger.info("Analyzing competitors")
        result = await analyzer.analyze_competitor_metadata(
            request.app_metadata,
            request.competitor_metadata
        )
        return result
    except Exception as e:
        logger.error(f"Error analyzing competitors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize/description")
async def optimize_description(request: DescriptionRequest):
    """Optimize app description using AI analysis"""
    try:
        logger.info("Optimizing description")
        result = await analyzer.optimize_description(
            request.current_description,
            request.keywords
        )
        return result
    except Exception as e:
        logger.error(f"Error optimizing description: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/trends")
async def analyze_trends(request: TrendRequest):
    """Analyze market trends and provide insights"""
    try:
        logger.info(f"Analyzing trends for category: {request.category}")
        result = await analyzer.analyze_market_trends(request.category)
        return result
    except Exception as e:
        logger.error(f"Error analyzing trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "aso-tool-backend"}

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Starting ASO Tool backend service...")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Shutdown event handler"""
    logger.info("Shutting down ASO Tool backend service...")
    client.close()