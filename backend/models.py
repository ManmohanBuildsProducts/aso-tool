from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class KeywordSuggestion(BaseModel):
    keyword: str
    relevance: float = Field(ge=0, le=1)
    competition: str = Field(regex="^(high|medium|low)$")
    priority: str = Field(regex="^(high|medium|low)$")

class LongTailKeyword(BaseModel):
    keyword: str
    search_intent: str = Field(regex="^(informational|transactional|navigational)$")
    opportunity: str = Field(regex="^(high|medium|low)$")

class RelatedTerm(BaseModel):
    term: str
    relevance: float = Field(ge=0, le=1)
    category: str

class KeywordAnalysis(BaseModel):
    variations: List[KeywordSuggestion]
    long_tail: List[LongTailKeyword]
    related_terms: List[RelatedTerm]
    recommendations: List[str]

class CompetitorMetrics(BaseModel):
    package_name: str
    name: str = "Unknown"
    metrics: Dict = Field(default_factory=dict)

class CompetitorAnalysis(BaseModel):
    metadata_analysis: Dict
    rankings_data: List[Dict] = Field(default_factory=list)
    competitors: List[CompetitorMetrics]

class ErrorResponse(BaseModel):
    detail: str
    code: str = "INTERNAL_ERROR"
    timestamp: datetime = Field(default_factory=datetime.utcnow)