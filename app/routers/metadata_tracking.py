from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.metadata_tracker import MetadataTracker

router = APIRouter()

@router.get("/track/{app_id}")
async def track_metadata(app_id: str) -> Dict[str, Any]:
    """
    Track and analyze app metadata changes over time
    """
    try:
        tracker = MetadataTracker()
        tracking_data = await tracker.track_metadata(app_id)
        return {
            "status": "success",
            "tracking_data": tracking_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))