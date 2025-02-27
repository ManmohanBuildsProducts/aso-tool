from fastapi import FastAPI, HTTPException, Depends, status, Body, Query
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import os
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB setup
mongo_url = os.environ.get('MONGO_URL', "")
client = AsyncIOMotorClient(mongo_url)
db = client.playstore_tracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app setup
app = FastAPI(title="Play Store Ranking Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AppBase(BaseModel):
    package_name: str
    name: str
    is_competitor: bool = False
    metadata: dict = Field(default_factory=dict)

class KeywordBase(BaseModel):
    keyword: str
    category: str
    traffic_score: Optional[float] = None
    difficulty_score: Optional[float] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class RankingBase(BaseModel):
    app_id: str
    keyword_id: str
    rank: int
    date: datetime = Field(default_factory=datetime.utcnow)

class UserBase(BaseModel):
    email: str
    name: str
    role: str = "marketing"

# API endpoints
from .aso_analyzer import ASOAnalyzer
from .scheduler import RankingScheduler
from .keyword_analyzer import KeywordAnalyzer
from .deepseek_analyzer import DeepseekAnalyzer
from .ranking_analyzer import RankingAnalyzer
from .metadata_optimizer import MetadataOptimizer

# Initialize components
deepseek_analyzer = DeepseekAnalyzer("sk-340de15952f44634804e7ae35af95cd2")
aso_analyzer = ASOAnalyzer(db)
ranking_scheduler = RankingScheduler(db)
keyword_analyzer = KeywordAnalyzer(db)
ranking_analyzer = RankingAnalyzer(db, deepseek_analyzer)
metadata_optimizer = MetadataOptimizer(db, deepseek_analyzer)

@app.on_event("startup")
async def startup_event():
    """Start the ranking scheduler on app startup"""
    asyncio.create_task(ranking_scheduler.start())

@app.get("/")
async def root():
    return {"status": "healthy", "service": "Play Store ASO Tracker"}

@app.get("/analyze/app/{app_id}")
async def analyze_app(app_id: str):
    """Get comprehensive ASO analysis for an app"""
    try:
        recommendations = await aso_analyzer.generate_aso_recommendations(app_id)
        b2b_metrics = await aso_analyzer.analyze_b2b_specific_metrics(app_id)
        
        return {
            "recommendations": recommendations,
            "b2b_metrics": b2b_metrics
        }
    except Exception as e:
        logger.error(f"Error analyzing app {app_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/keywords")
async def analyze_keywords(keywords: str):
    """Analyze keyword opportunities with enhanced insights"""
    try:
        keywords_list = keywords.split(",")
        results = []
        
        for keyword in keywords_list:
            # Get keyword suggestions
            suggestions = await keyword_analyzer.get_keyword_suggestions(keyword.strip())
            
            # Get keyword analysis
            keyword_data = {
                "keyword": keyword.strip(),
                "suggestions": suggestions[:10],  # Top 10 suggestions
                "categories": [],  # Categories this keyword belongs to
                "metrics": {
                    "search_volume_score": 0,  # To be implemented with real data
                    "difficulty_score": 0,     # To be implemented with real data
                    "relevance_score": 0,      # To be implemented with real data
                    "trend": "stable"          # Default trend
                }
            }
            
            # Find relevant categories
            for category, keywords in keyword_analyzer.keyword_categories.items():
                if any(kw in keyword.lower() for kw in keywords):
                    keyword_data["categories"].append(category)
            
            # Get opportunity analysis
            opportunity = await aso_analyzer.analyze_keyword_opportunity(keyword_data)
            keyword_data["opportunity"] = opportunity
            
            results.append(keyword_data)
        
        return results
    except Exception as e:
        logger.error(f"Error analyzing keywords: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/keywords/suggest/{base_keyword}")
async def suggest_keywords(base_keyword: str, limit: int = 50):
    """Get keyword suggestions based on a base keyword"""
    try:
        suggestions = await keyword_analyzer.get_keyword_suggestions(base_keyword)
        return {
            "base_keyword": base_keyword,
            "suggestions": suggestions[:limit],
            "total_suggestions": len(suggestions)
        }
    except Exception as e:
        logger.error(f"Error getting keyword suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/keywords/categories")
async def get_keyword_categories():
    """Get all keyword categories and their keywords"""
    try:
        return {
            "categories": keyword_analyzer.keyword_categories,
            "total_categories": len(keyword_analyzer.keyword_categories),
            "total_keywords": sum(len(kws) for kws in keyword_analyzer.keyword_categories.values())
        }
    except Exception as e:
        logger.error(f"Error getting keyword categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New AI-powered endpoints
@app.get("/ai/rankings/analyze/{app_id}")
async def analyze_rankings(app_id: str, days: int = 30):
    """Get AI analysis of ranking changes"""
    try:
        return await ranking_analyzer.analyze_ranking_changes(app_id, days)
    except Exception as e:
        logger.error(f"Error analyzing rankings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/rankings/predict/{app_id}/{keyword}")
async def predict_rankings(app_id: str, keyword: str):
    """Get AI predictions for keyword ranking"""
    try:
        return await ranking_analyzer.predict_ranking_trends(app_id, keyword)
    except Exception as e:
        logger.error(f"Error predicting rankings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/competitors/impact/{app_id}")
async def analyze_competitor_impact(app_id: str):
    """Analyze competitor impact on rankings"""
    try:
        # Get app data
        app = await db.apps.find_one({"package_name": app_id})
        if not app:
            raise HTTPException(status_code=404, detail="App not found")

        # Get competitors
        competitors = await db.apps.find({"is_competitor": True}).to_list(length=10)
        if not competitors:
            return {
                "message": "No competitors found",
                "impact": [],
                "recommendations": []
            }

        # Analyze impact
        analysis = await deepseek_analyzer.analyze_competitor_metadata(
            app.get("metadata", {}),
            [comp.get("metadata", {}) for comp in competitors]
        )

        # Get rankings data
        rankings = await db.rankings.find({
            "app_id": {"$in": [app_id] + [c["package_name"] for c in competitors]}
        }).sort("date", -1).limit(100).to_list(length=100)

        # Combine analysis
        return {
            "metadata_analysis": analysis,
            "rankings_data": rankings,
            "competitors": [
                {
                    "package_name": comp["package_name"],
                    "name": comp.get("name", "Unknown"),
                    "metrics": comp.get("metadata", {})
                }
                for comp in competitors
            ]
        }
    except Exception as e:
        logger.error(f"Error analyzing competitor impact: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/metadata/title/{app_id}")
async def optimize_title(
    app_id: str,
    keywords: List[str] = Body(...)
):
    """Get AI-optimized title suggestions"""
    try:
        return await metadata_optimizer.optimize_app_title(app_id, keywords)
    except Exception as e:
        logger.error(f"Error optimizing title: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/metadata/screenshots/{app_id}")
async def analyze_screenshots(app_id: str):
    """Get AI analysis of screenshot effectiveness"""
    try:
        return await metadata_optimizer.analyze_screenshot_impact(app_id)
    except Exception as e:
        logger.error(f"Error analyzing screenshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/metadata/features/{app_id}")
async def generate_features(
    app_id: str,
    keywords: List[str] = Body(...)
):
    """Get AI-generated feature bullets"""
    try:
        return await metadata_optimizer.generate_feature_bullets(app_id, keywords)
    except Exception as e:
        logger.error(f"Error generating features: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/reviews/analyze/{app_id}")
async def analyze_reviews(app_id: str):
    """Get AI analysis of review keywords"""
    try:
        return await metadata_optimizer.analyze_review_keywords(app_id)
    except Exception as e:
        logger.error(f"Error analyzing reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/analyze/{app_id}")
async def ai_analyze_app(app_id: str):
    """Get AI-powered app analysis"""
    try:
        # Get app data
        app = await db.apps.find_one({"package_name": app_id})
        if not app:
            raise HTTPException(status_code=404, detail="App not found")
            
        # Get competitors
        competitors = await db.apps.find({"is_competitor": True}).to_list(length=100)
        
        # Get AI analysis
        analysis = await deepseek_analyzer.analyze_app_metadata(
            app.get("metadata", {}),
            [comp.get("metadata", {}) for comp in competitors]
        )
        
        return analysis
    except Exception as e:
        logger.error(f"Error in AI analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/keywords/{keyword}")
async def ai_analyze_keyword(keyword: str):
    """Get AI-powered keyword analysis"""
    try:
        analysis = await deepseek_analyzer.generate_keyword_suggestions(keyword)
        return analysis
    except Exception as e:
        logger.error(f"Error in keyword analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/trends")
async def ai_analyze_trends():
    """Get AI-powered market trend analysis"""
    try:
        analysis = await deepseek_analyzer.analyze_market_trends()
        return analysis
    except Exception as e:
        logger.error(f"Error in trend analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/optimize/description/{app_id}")
async def ai_optimize_description(
    app_id: str,
    keywords: List[str]
):
    """Optimize app description using AI"""
    try:
        app = await db.apps.find_one({"package_name": app_id})
        if not app:
            raise HTTPException(status_code=404, detail="App not found")
            
        current_description = app.get("metadata", {}).get("full_description", "")
        optimization = await deepseek_analyzer.optimize_description(
            current_description,
            keywords
        )
        
        return optimization
    except Exception as e:
        logger.error(f"Error optimizing description: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/competitors/{app_id}")
async def analyze_competitors(app_id: str):
    """Get competitor analysis for an app"""
    try:
        app = await db.apps.find_one({"package_name": app_id})
        if not app:
            raise HTTPException(status_code=404, detail="App not found")
            
        competitors = await db.apps.find({"is_competitor": True}).to_list(length=100)
        
        analyses = []
        for competitor in competitors:
            analysis = await aso_analyzer.analyze_competitor_metadata(
                app.get("metadata", {}),
                competitor.get("metadata", {})
            )
            analyses.append({
                "competitor_id": str(competitor["_id"]),
                "competitor_name": competitor["name"],
                "analysis": analysis
            })
        
        return analyses
    except Exception as e:
        logger.error(f"Error analyzing competitors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rankings/check")
async def force_ranking_check():
    """Force an immediate ranking check"""
    try:
        await ranking_scheduler.force_check()
        return {"status": "success", "message": "Ranking check initiated"}
    except Exception as e:
        logger.error(f"Error forcing ranking check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rankings/history/{app_id}")
async def get_ranking_history(app_id: str, days: int = 30):
    """Get ranking history for an app"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        rankings = await db.rankings.find({
            "app_id": app_id,
            "date": {"$gte": cutoff_date}
        }).sort("date", -1).to_list(length=1000)
        
        return [{
            "date": r["date"].isoformat(),
            "keyword": r["keyword"],
            "rank": r["rank"]
        } for r in rankings]
    except Exception as e:
        logger.error(f"Error fetching ranking history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# App management endpoints
@app.post("/apps/", response_model=AppBase)
async def create_app(app: AppBase):
    try:
        result = await db.apps.insert_one(app.dict())
        created_app = await db.apps.find_one({"_id": result.inserted_id})
        return {**created_app, "id": str(created_app["_id"])}
    except Exception as e:
        logger.error(f"Error creating app: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/apps/", response_model=List[AppBase])
async def get_apps():
    try:
        apps = await db.apps.find().to_list(length=100)
        return [{**app, "id": str(app["_id"])} for app in apps]
    except Exception as e:
        logger.error(f"Error fetching apps: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Keyword management endpoints
@app.post("/keywords/", response_model=KeywordBase)
async def create_keyword(keyword: KeywordBase):
    try:
        result = await db.keywords.insert_one(keyword.dict())
        created_keyword = await db.keywords.find_one({"_id": result.inserted_id})
        return {**created_keyword, "id": str(created_keyword["_id"])}
    except Exception as e:
        logger.error(f"Error creating keyword: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/keywords/", response_model=List[KeywordBase])
async def get_keywords():
    try:
        keywords = await db.keywords.find().to_list(length=100)
        return [{**keyword, "id": str(keyword["_id"])} for keyword in keywords]
    except Exception as e:
        logger.error(f"Error fetching keywords: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Ranking tracking endpoints
@app.post("/rankings/", response_model=RankingBase)
async def create_ranking(ranking: RankingBase):
    try:
        result = await db.rankings.insert_one(ranking.dict())
        created_ranking = await db.rankings.find_one({"_id": result.inserted_id})
        return {**created_ranking, "id": str(created_ranking["_id"])}
    except Exception as e:
        logger.error(f"Error creating ranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rankings/{app_id}", response_model=List[RankingBase])
async def get_app_rankings(app_id: str):
    try:
        rankings = await db.rankings.find({"app_id": app_id}).to_list(length=1000)
        return [{**ranking, "id": str(ranking["_id"])} for ranking in rankings]
    except Exception as e:
        logger.error(f"Error fetching rankings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Cleanup
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
