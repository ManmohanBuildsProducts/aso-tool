from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.routers import (
    app_analysis, keyword_analysis, competitor_analysis,
    metadata_analysis, review_analysis, text_analysis,
    metadata_tracking
)
from app.core.config import settings
from app.core.health import HealthCheck
from app.core.error_handler import ErrorHandler

app = FastAPI(
    title="ASO Tool API",
    description="App Store Optimization Tool API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check instance
health_checker = HealthCheck()

# Mount static files
import os

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(app_analysis.router, prefix="/api", tags=["App Analysis"])
app.include_router(competitor_analysis.router, prefix="/api", tags=["Competitor Analysis"])
app.include_router(keyword_analysis.router, prefix="/api", tags=["Keyword Analysis"])
app.include_router(metadata_analysis.router, prefix="/api", tags=["Metadata Analysis"])
app.include_router(review_analysis.router, prefix="/api", tags=["Review Analysis"])
app.include_router(text_analysis.router, prefix="/api", tags=["Text Analysis"])
app.include_router(metadata_tracking.router, prefix="/api", tags=["Metadata Tracking"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return health_checker.check_health()

@app.get("/")
async def serve_spa():
    """Serve the Single Page Application"""
    return FileResponse("../frontend/dist/index.html")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return await ErrorHandler.handle_exception(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Validation error handler"""
    return JSONResponse(
        status_code=422,
        content=ErrorHandler.format_error_response(
            message="Validation error",
            code=422,
            data={"errors": exc.errors()}
        )
    )