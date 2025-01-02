"""
Models module initialization.
"""

from ..core.database import Base
from .user import User, UserCreate, UserResponse, UserBase
from .community_analysis import (
    CommunityInsight, CommunityTrend, AnalysisRequest,
    CommunityAnalysisResponse, CommunityTrendsInput, CommunityTrendsResponse
)
from .market_research import (
    MarketingResearch, MarketingResearchCreate, MarketingResearchUpdate,
    MarketingResearchResponse, CommunityAnalysisModel, MarketAnalysisModel
)
from .market_analysis import MarketOpportunity
from .scraper import ContentChunk

__all__ = [
    'Base',
    'User', 'UserCreate', 'UserResponse', 'UserBase',
    'CommunityInsight', 'CommunityTrend', 'AnalysisRequest',
    'CommunityAnalysisResponse', 'CommunityTrendsInput', 'CommunityTrendsResponse',
    'MarketingResearch', 'MarketingResearchCreate', 'MarketingResearchUpdate',
    'MarketingResearchResponse', 'CommunityAnalysisModel', 'MarketAnalysisModel',
    'MarketOpportunity', 'ContentChunk'
]
