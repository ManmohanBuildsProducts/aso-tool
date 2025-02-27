from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from app.services.keyword_analyzer import KeywordAnalyzer
from app.services.keyword_scorer import KeywordScorer
from app.services.visualization import Visualizer

router = APIRouter()

class KeywordAnalysisRequest(BaseModel):
    app_id: str
    competitor_ids: List[str] = []
    keywords: List[str] = []

@router.post("/discover")
async def discover_keywords(request: KeywordAnalysisRequest) -> Dict[str, Any]:
    """
    Discover and analyze keywords for an app and its competitors
    """
    try:
        # Initialize services
        analyzer = KeywordAnalyzer()
        scorer = KeywordScorer()
        visualizer = Visualizer()
        
        # Get keyword analysis
        if request.competitor_ids:
            analysis = await analyzer.compare_keywords(request.app_id, request.competitor_ids)
        else:
            analysis = await analyzer.analyze_app_keywords(request.app_id)
        
        # Get keyword difficulty scores
        keywords_to_analyze = request.keywords or analysis.get("top_keywords", {}).keys()
        keyword_trends = await scorer.analyze_keyword_trends(keywords_to_analyze)
        
        # Create visualizations
        keyword_chart = visualizer.create_keyword_comparison_chart(keyword_trends)
        
        return {
            "status": "success",
            "analysis": analysis,
            "keyword_trends": keyword_trends,
            "visualizations": {
                "keyword_comparison": keyword_chart
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analyze/{app_id}")
async def analyze_single_app(app_id: str) -> Dict[str, Any]:
    """
    Analyze keywords for a single app
    """
    try:
        analyzer = KeywordAnalyzer()
        analysis = await analyzer.analyze_app_keywords(app_id)
        
        # Get difficulty scores for top keywords
        scorer = KeywordScorer()
        top_keywords = list(analysis.get("top_keywords", {}).keys())[:10]
        keyword_trends = await scorer.analyze_keyword_trends(top_keywords)
        
        # Create visualization
        visualizer = Visualizer()
        keyword_chart = visualizer.create_keyword_comparison_chart(keyword_trends)
        
        return {
            "status": "success",
            "analysis": analysis,
            "keyword_trends": keyword_trends,
            "visualizations": {
                "keyword_comparison": keyword_chart
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))