from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..services.metadata_analyzer import MetadataAnalyzer

router = APIRouter()

@router.get("/analyze/{app_id}")
async def analyze_metadata(app_id: str) -> Dict[str, Any]:
    """
    Analyze app metadata including title and description optimization
    """
    try:
        analyzer = MetadataAnalyzer()
        analysis = await analyzer.analyze_metadata(app_id)
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))