from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from services.app_scraper import AppScraper

router = APIRouter()

@router.get("/{app_id}")
async def analyze_app(app_id: str, lang: str = 'en', country: str = 'us') -> Dict[str, Any]:
    """
    Analyze an app by its Google Play Store ID
    """
    try:
        scraper = AppScraper()
        app_details = await scraper.get_app_details(app_id, lang, country)
        return {
            "status": "success",
            "data": app_details
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))