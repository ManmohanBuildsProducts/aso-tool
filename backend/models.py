from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class AppMetadata(BaseModel):
    title: str
    short_description: str
    full_description: str
    icon_url: Optional[str]
    screenshots: List[str] = []
    category: str
    developer: str
    installs_range: str
    rating: float
    reviews_count: int
    size: str
    last_updated: datetime
    content_rating: str
    price: str
    supported_languages: List[str] = []

class KeywordMetrics(BaseModel):
    keyword: str
    search_volume_score: Optional[float] = None  # 0-100 scale
    difficulty_score: Optional[float] = None     # 0-100 scale
    relevancy_score: Optional[float] = None      # 0-100 scale
    trending_score: Optional[float] = None       # -100 to 100 scale
    category_relevance: List[str] = []          # Relevant categories
    search_suggestions: List[str] = []          # Related search terms
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class RankingSnapshot(BaseModel):
    app_id: str
    keyword_id: str
    rank: int
    date: datetime = Field(default_factory=datetime.utcnow)
    search_page_data: Dict = Field(default_factory=dict)  # Stores visibility metrics
    category_rank: Optional[int] = None
    similar_apps: List[str] = []  # Package names of "Similar apps" section

class CompetitorAnalysis(BaseModel):
    app_id: str
    competitor_id: str
    date: datetime = Field(default_factory=datetime.utcnow)
    shared_keywords: List[str] = []
    keyword_opportunities: List[str] = []  # Keywords where competitor ranks better
    metadata_diff: Dict = Field(default_factory=dict)  # Differences in titles, descriptions
    visibility_score: float = 0.0  # Overall visibility comparison

class ASORecommendation(BaseModel):
    app_id: str
    date: datetime = Field(default_factory=datetime.utcnow)
    category: str  # e.g., "title", "description", "keywords", "screenshots"
    current_value: str
    suggested_value: str
    impact_score: float  # 0-100 scale
    reasoning: str
    implementation_difficulty: str  # "easy", "medium", "hard"

class KeywordOpportunity(BaseModel):
    keyword: str
    search_volume_score: float
    difficulty_score: float
    relevancy_score: float
    current_rank: Optional[int]
    estimated_traffic: float
    top_ranking_apps: List[str]
    recommendation: str
    priority: str  # "high", "medium", "low"