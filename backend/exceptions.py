from fastapi import HTTPException
from datetime import datetime

class ASOException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str = "INTERNAL_ERROR"
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "detail": detail,
                "code": code,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

class AppNotFoundException(ASOException):
    def __init__(self, app_id: str):
        super().__init__(
            status_code=404,
            detail=f"App {app_id} not found",
            code="APP_NOT_FOUND"
        )

class CompetitorNotFoundException(ASOException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="No competitors found",
            code="COMPETITORS_NOT_FOUND"
        )

class AIAnalysisException(ASOException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=500,
            detail=f"AI analysis failed: {detail}",
            code="AI_ANALYSIS_ERROR"
        )

class ValidationException(ASOException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=422,
            detail=f"Validation error: {detail}",
            code="VALIDATION_ERROR"
        )