"""
Main FastAPI application
"""
from fastapi import FastAPI

# Create FastAPI app
app = FastAPI(
    title="ASO Tool",
    description="App Store Optimization Tool",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to ASO Tool API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}