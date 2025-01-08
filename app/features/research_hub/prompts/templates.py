from typing import List, Dict, Callable
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class AnalysisType(str, Enum):
    PAIN = "pain"
    QUESTION = "question"
    PATTERN = "pattern"
    AVATAR = "avatar"
    PRODUCT = "product"

class PromptTemplate:
    def __init__(self, focus_points: List[str], insight_requirements: List[str], additional_instructions: List[str] = None):
        self.focus_points = focus_points
        self.insight_requirements = insight_requirements
        self.additional_instructions = additional_instructions or []

    def generate(
        self,
        topic_keyword: str,
        user_query: str,
        source_urls: List[str] = None,
        product_urls: List[str] = None,
        use_only_specified_sources: bool = False
    ) -> str:
        prompt_parts = [
            f"Analyze community discussions about the following topic: `{topic_keyword}` with specific focus on: `{user_query}`. Search across Reddit and relevant forums.",
            "\nFocus on the following aspects. Analyze:",
        ]
        prompt_parts.extend(f"- {point}" for point in self.focus_points)
        
        prompt_parts.extend([
            "\nFor each insight, provide:",
        ])
        prompt_parts.extend(f"{i+1}. {req}" for i, req in enumerate(self.insight_requirements))
        
        if self.additional_instructions:
            prompt_parts.extend(self.additional_instructions)
        
        prompt = "\n".join(prompt_parts)
        logger.debug(f"Generated prompt for topic: {topic_keyword}")
        return prompt

# Define common insight requirements
COMMON_INSIGHT_REQUIREMENTS = [
    "A clear title/description",
    "Supporting evidence (direct quotes)",
    "Source URL in plain text",
    "Engagement metrics (upvotes, comments)",
    "Frequency of occurrence",
    "Correlation with other patterns",
    "Significance/implications"
]

# Define templates for each analysis type
TEMPLATES = {
    AnalysisType.PAIN: PromptTemplate(
        focus_points=[
            "Most emotionally charged complaints",
            "Recurring sources of anger",
            "Hidden frustrations",
            "Indirect expressions of dissatisfaction",
            "Cascade effects of problems",
            "Time patterns in complaint posting"
        ],
        insight_requirements=COMMON_INSIGHT_REQUIREMENTS,
        additional_instructions=[
            "\nFocus on emotional impact and user frustrations.",
            "Organize findings by engagement level (most discussed/upvoted first)."
        ]
    ),
    
    AnalysisType.QUESTION: PromptTemplate(
        focus_points=[
            "Most frequently asked questions",
            "Most upvoted advice",
            "Most debated solutions",
            "Most repeated recommendations",
            "Success stories with details",
            "Failure patterns with context"
        ],
        insight_requirements=COMMON_INSIGHT_REQUIREMENTS,
        additional_instructions=[
            "\nFocus on what users are asking and what solutions work.",
            "Organize findings by engagement level (most discussed/upvoted first)."
        ]
    ),
    
    AnalysisType.PATTERN: PromptTemplate(
        focus_points=[
            "Unusual word combinations",
            "Vocabulary differences between users",
            "Shifts in problem descriptions",
            "Non-obvious correlations",
            "Counter-intuitive success patterns",
            "Secondary effects users overlook",
            "Unexpected relationships between issues"
        ],
        insight_requirements=COMMON_INSIGHT_REQUIREMENTS,
        additional_instructions=[
            "\nFocus on unexpected patterns and hidden relationships.",
            "Organize findings by engagement level (most discussed/upvoted first)."
        ]
    ),
    
    AnalysisType.AVATAR: PromptTemplate(
        focus_points=[
            "Demographic indicators found in discussions",
            "Primary pain points (with supporting quotes)",
            "Typical vocabulary and phrase patterns",
            "Common behaviors and usage patterns",
            "Decision-making factors",
            "Success criteria and definitions",
            "Interaction preferences",
            "Resource constraints",
            "Notable quotes that epitomize this user type"
        ],
        insight_requirements=[
            "Support characteristics with direct evidence from findings",
            "Link to specific discussion threads/comments",
            "Indicate relative size of this segment based on discussion frequency",
            "Highlight unique characteristics that distinguish this avatar",
            "Note any surprising or counter-intuitive traits"
        ],
        additional_instructions=[
            "\nFocus on creating distinct, non-overlapping avatars that capture major user segments evident in the discussions.",
            "Prioritize patterns that appeared consistently across multiple sources."
        ]
    ),
    
    AnalysisType.PRODUCT: PromptTemplate(
        focus_points=[
            "Most popular products in this category",
            "Price ranges and variations",
            "Common positive feedback themes",
            "Recurring complaints and issues",
            "Potential market gaps and opportunities",
            "Customer satisfaction patterns",
            "Feature comparisons between products"
        ],
        insight_requirements=[
            "Product name and description",
            "Platform (Amazon/eBay/Google Shopping)",
            "Price range",
            "List of positive feedback points",
            "List of negative feedback points",
            "Identified market gap or opportunity",
            "Source URL in plain text",
            "Engagement metrics (reviews, ratings)",
            "Frequency of mentions",
            "Correlation with other products",
            "Market significance"
        ],
        additional_instructions=[
            "\nFocus on identifying patterns in customer feedback and market opportunities.",
            "Organize findings by popularity and engagement level."
        ]
    )
}

def get_prompt(
    analysis_type: str,
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """Get the appropriate prompt for the given analysis type."""
    template = TEMPLATES.get(analysis_type)
    if not template:
        raise ValueError(f"Invalid analysis type: {analysis_type}")
    
    return template.generate(
        topic_keyword=topic_keyword,
        user_query=user_query,
        source_urls=source_urls,
        product_urls=product_urls,
        use_only_specified_sources=use_only_specified_sources
    ) 