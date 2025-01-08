from pydantic import BaseModel
from typing import Dict, Any, List

class AnalysisTypeMetadata(BaseModel):
    """Metadata about an analysis type."""
    id: str  # The enum value
    name: str  # Display name
    description: str
    icon: str
    example_insights: List[str]
    capabilities: List[str]

ANALYSIS_TYPES_METADATA = {
    "Pain & Frustration Analysis": AnalysisTypeMetadata(
        id="pain",
        name="Pain & Frustration Analysis",
        description="Analyze user pain points, frustrations, and emotional responses",
        icon="FaHeartBroken",
        example_insights=[
            "Common user complaints and their frequency",
            "Emotional impact of problems",
            "Hidden frustrations and their patterns"
        ],
        capabilities=[
            "Identify emotional triggers",
            "Track complaint patterns",
            "Measure problem severity",
            "Analyze user sentiment"
        ]
    ),
    "Question & Advice Mapping": AnalysisTypeMetadata(
        id="question",
        name="Question & Advice Mapping",
        description="Map common questions, advice patterns, and solution effectiveness",
        icon="FaQuestionCircle",
        example_insights=[
            "Frequently asked questions",
            "Most effective solutions",
            "Common advice patterns"
        ],
        capabilities=[
            "Track question frequency",
            "Evaluate solution effectiveness",
            "Map advice patterns",
            "Identify knowledge gaps"
        ]
    ),
    "Pattern Detection": AnalysisTypeMetadata(
        id="pattern",
        name="Pattern Detection",
        description="Detect hidden patterns, trends, and correlations in user behavior",
        icon="FaChartLine",
        example_insights=[
            "Behavioral patterns",
            "Usage trends",
            "Feature correlations"
        ],
        capabilities=[
            "Identify usage patterns",
            "Track behavior changes",
            "Find correlations",
            "Predict trends"
        ]
    ),
    "Popular Products Analysis": AnalysisTypeMetadata(
        id="product",
        name="Popular Products Analysis",
        description="Analyze product popularity, features, and market positioning",
        icon="FaShoppingCart",
        example_insights=[
            "Popular product features",
            "Market gaps",
            "Competitive advantages"
        ],
        capabilities=[
            "Track product popularity",
            "Compare features",
            "Analyze market position",
            "Identify opportunities"
        ]
    ),
    "Avatars": AnalysisTypeMetadata(
        id="avatar",
        name="Avatars",
        description="Create and analyze user personas and their characteristics",
        icon="FaUsers",
        example_insights=[
            "User personas",
            "Behavior patterns",
            "Needs and preferences"
        ],
        capabilities=[
            "Create user personas",
            "Map behaviors",
            "Track preferences",
            "Analyze needs"
        ]
    )
} 