from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from services.review_analyzer import ReviewAnalyzer

router = APIRouter()

@router.post("/analyze")
async def analyze_reviews(reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze app reviews for sentiment and insights
    """
    if not reviews:
        raise HTTPException(status_code=400, detail="No reviews provided")
        
    # Validate review format
    required_fields = {'text', 'score', 'timestamp'}
    for review in reviews:
        missing_fields = required_fields - set(review.keys())
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
    
    try:
        analyzer = ReviewAnalyzer()
        analysis = await analyzer.analyze_reviews(reviews)
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))