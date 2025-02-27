from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

class ErrorHandler:
    @staticmethod
    async def handle_exception(request: Request, exc: Exception) -> JSONResponse:
        """Handle all exceptions and return appropriate responses"""
        timestamp = datetime.now().isoformat()
        
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "status": "error",
                    "timestamp": timestamp,
                    "detail": exc.detail,
                    "code": exc.status_code
                }
            )
        
        # Log unexpected errors
        logger.error(f"Unexpected error: {str(exc)}\n{traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "timestamp": timestamp,
                "detail": "An unexpected error occurred",
                "code": 500
            }
        )

    @staticmethod
    def format_error_response(message: str, code: int = 400, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format error response with consistent structure"""
        response = {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "code": code
        }
        
        if data:
            response["data"] = data
            
        return response