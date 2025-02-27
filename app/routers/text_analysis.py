from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from services.text_analyzer import TextAnalyzer

router = APIRouter()

@router.post("/analyze")
async def analyze_text(text: str, text_type: str = 'full_description') -> Dict[str, Any]:
    """
    Analyze text for character and word counts with optimization suggestions
    """
    try:
        analyzer = TextAnalyzer()
        analysis = analyzer.analyze_text(text, text_type)
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))