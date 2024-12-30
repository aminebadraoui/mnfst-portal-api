from typing import List
from pydantic import BaseModel, Field, HttpUrl

class ChunkInsight(BaseModel):
    source: HttpUrl = Field(description="The URL this insight was extracted from")
    top_keyword: str = Field(description="The most frequently occurring or significant keyword/phrase in the chunk")
    key_insight: str = Field(description="The most important insight or takeaway from this chunk of text")
    key_quote: str = Field(description="A verbatim quote from the text that best represents the key insight or pain point")

    @classmethod
    def create_empty(cls, source: HttpUrl) -> "ChunkInsight":
        """Create an empty insight when analysis fails."""
        return cls(
            source=source,
            top_keyword="No content available",
            key_insight="No content available",
            key_quote="No content available"
        )

class URLAnalysisResult(BaseModel):
    url: HttpUrl
    insights: List[ChunkInsight]

class AnalysisRequest(BaseModel):
    urls: List[HttpUrl] = Field(description="List of URLs to analyze")

class BatchAnalysisResponse(BaseModel):
    results: List[URLAnalysisResult]
    failed_urls: List[str] = [] 