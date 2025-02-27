from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from ..services.competitor_analyzer import CompetitorAnalyzer
from ..services.historical_tracker import HistoricalTracker
from ..services.visualization import Visualizer

router = APIRouter()

class CompetitorAnalysisRequest(BaseModel):
    app_id: str
    competitor_ids: List[str]

@router.post("/compare")
async def compare_apps(request: CompetitorAnalysisRequest) -> Dict[str, Any]:
    """
    Compare an app with its competitors
    """
    # Validate app_id
    if not request.app_id:
        raise HTTPException(status_code=400, detail="App ID is required")
    
    # Validate competitor_ids
    if not request.competitor_ids:
        raise HTTPException(status_code=400, detail="At least one competitor ID is required")
    
    # Check for duplicate IDs
    if request.app_id in request.competitor_ids:
        raise HTTPException(status_code=400, detail="Main app ID cannot be in competitor IDs")
    
    if len(request.competitor_ids) != len(set(request.competitor_ids)):
        raise HTTPException(status_code=400, detail="Duplicate competitor IDs are not allowed")
    
    try:
        analyzer = CompetitorAnalyzer()
        comparison = await analyzer.analyze_competitors(request.app_id, request.competitor_ids)
        
        # Check if any data was retrieved
        if not comparison or not comparison.get("main_app"):
            raise HTTPException(status_code=400, detail="Failed to retrieve app data")
        
        return {
            "status": "success",
            "comparison": comparison
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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