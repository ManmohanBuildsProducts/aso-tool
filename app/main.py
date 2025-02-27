from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routers import (
    app_analysis, keyword_analysis, competitor_analysis,
    metadata_analysis, review_analysis, text_analysis,
    metadata_tracking
)
from .core.config import settings

app = FastAPI(
    title="ASO Tool API",
    description="App Store Optimization Tool for Google Play Store",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(app_analysis.router, prefix="/api/analyze/app", tags=["App Analysis"])
app.include_router(keyword_analysis.router, prefix="/api/analyze/keywords", tags=["Keyword Analysis"])
app.include_router(competitor_analysis.router, prefix="/api/analyze/competitors", tags=["Competitor Analysis"])
app.include_router(metadata_analysis.router, prefix="/api/analyze/metadata", tags=["Metadata Analysis"])
app.include_router(review_analysis.router, prefix="/api/analyze/reviews", tags=["Review Analysis"])
app.include_router(text_analysis.router, prefix="/api/analyze/text", tags=["Text Analysis"])
app.include_router(metadata_tracking.router, prefix="/api/track", tags=["Metadata Tracking"])

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# Serve static files
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")