from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from app.services.competitor_analyzer import CompetitorAnalyzer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class CompetitorRequest(BaseModel):
    app_id: str
    competitor_ids: List[str]

@router.post("/analyze/competitors/compare")
async def analyze_competitors(request: CompetitorRequest) -> Dict[str, Any]:
    """
    Analyze competitors with improved error handling
    """
    try:
        analyzer = CompetitorAnalyzer()
        result = await analyzer.analyze_competitors(request.app_id, request.competitor_ids)
        
        if result["status"] == "error":
            return {
                "status": "error",
                "message": result.get("message", "Unknown error occurred"),
                "comparison": result.get("comparison", {})
            }
        
        return {
            "status": "success",
            "comparison": result
        }
        
    except Exception as e:
        logger.error(f"Error in competitor analysis: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "comparison": analyzer._get_default_metrics()
        }