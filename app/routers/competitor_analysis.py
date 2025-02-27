from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from services.competitor_analyzer import CompetitorAnalyzer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class CompetitorRequest(BaseModel):
    app_id: str
    competitor_ids: List[str]

@router.post("/analyze/competitors/compare")
async def analyze_competitors(request: CompetitorRequest):
    try:
        analyzer = CompetitorAnalyzer()
        result = await analyzer.analyze_competitors(request.app_id, request.competitor_ids)
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