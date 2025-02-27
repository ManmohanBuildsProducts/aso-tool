from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from services.competitor_analyzer import CompetitorAnalyzer
from services.historical_tracker import HistoricalTracker
from services.visualization import Visualizer

router = APIRouter()

class CompetitorAnalysisRequest(BaseModel):
    app_id: str
    competitor_ids: List[str]

@router.post("/compare")
async def compare_apps(request: CompetitorAnalysisRequest) -> Dict[str, Any]:
    """
    Compare an app with its competitors
    """
    try:
        # Validate input
        if not request.app_id:
            raise HTTPException(status_code=400, detail="App ID is required")
        if not request.competitor_ids:
            raise HTTPException(status_code=400, detail="At least one competitor ID is required")
        
        analyzer = CompetitorAnalyzer()
        comparison = await analyzer.analyze_competitors(request.app_id, request.competitor_ids)
        
        # Clean up None values in the response
        def clean_value(value):
            if value is None:
                return "N/A"
            return value
        
        # Clean up the comparison data
        if comparison.get("main_app"):
            for key in ["score", "ratings", "reviews"]:
                if key in comparison["main_app"]["details"]:
                    comparison["main_app"]["details"][key] = clean_value(comparison["main_app"]["details"][key])
        
        if comparison.get("competitors"):
            for comp in comparison["competitors"]:
                for key in ["score", "ratings", "reviews"]:
                    if key in comp["details"]:
                        comp["details"][key] = clean_value(comp["details"][key])
        
        return {
            "status": "success",
            "comparison": comparison
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error analyzing competitors: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error analyzing competitors: {str(e)}")

@router.get("/history/{app_id}")
async def get_app_history(app_id: str) -> Dict[str, Any]:
    """
    Get historical data for an app
    """
    try:
        tracker = HistoricalTracker()
        historical_data = await tracker.track_app_metrics(app_id)
        
        visualizer = Visualizer()
        historical_chart = visualizer.create_historical_trend_chart(historical_data["historical_data"])
        
        return {
            "status": "success",
            "historical_data": historical_data,
            "visualizations": {
                "historical_trends": historical_chart
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))