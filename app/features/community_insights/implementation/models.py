from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class CommunityInsightsRequest(BaseModel):
    topic_keyword: str
    user_query: str
    user_id: str
    project_id: str
    source_urls: Optional[List[str]] = None
    product_urls: Optional[List[str]] = None
    use_only_specified_sources: bool = False

class CommunityInsightsResponse(BaseModel):
    status: str
    sections: Optional[List[Dict[str, Any]]] = []
    avatars: Optional[List[Dict[str, Any]]] = []
    error: Optional[str] = None
    raw_perplexity_response: Optional[str] = None 