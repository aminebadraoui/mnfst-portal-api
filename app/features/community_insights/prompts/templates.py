from typing import List
import logging

logger = logging.getLogger(__name__)

def get_community_insights_prompt(
    topic_keyword: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """
    Generate a prompt for community insights analysis.
    """
    prompt_parts = [
        f"Analyze community discussions about the following topic: `{topic_keyword}` . Search across Reddit and relevant forums.",
        "\nProvide a comprehensive analysis with the following sections:",
        "\n1. PAIN & FRUSTRATION ANALYSIS",
        "- Most emotionally charged complaints",
        "- Recurring sources of anger",
        "- Hidden frustrations",
        "- Indirect expressions of dissatisfaction",
        "- Cascade effects of problems",
        "- Time patterns in complaint posting",
        "\n2. QUESTION & ADVICE MAPPING",
        "- Most frequently asked questions",
        "- Most upvoted advice",
        "- Most debated solutions",
        "- Most repeated recommendations",
        "- Success stories with details",
        "- Failure patterns with context",
        "\n3. PATTERN DETECTION",
        "- Unusual word combinations",
        "- Vocabulary differences between users",
        "- Shifts in problem descriptions",
        "- Non-obvious correlations",
        "- Counter-intuitive success patterns",
        "- Secondary effects users overlook",
        "- Unexpected relationships between issues"
    ]

    prompt_parts.extend([
        "\nFor each insight, provide:",
        "1. A clear title/description",
        "2. Supporting evidence (direct quotes)",
        "3. Source URL in plain text",
        "4. Engagement metrics (upvotes, comments)",
        "5. Frequency of occurrence",
        "6. Correlation with other patterns",
        "7. Significance/implications",
        "\nFocus on counter-intuitive insights that aren't immediately obvious.",
        "Organize findings by engagement level (most discussed/upvoted first).",
    ])

    prompt_parts.extend([
    "\n4. CUSTOMER AVATAR SYNTHESIS",
    "Based on the above analysis, construct detailed customer avatars that represent distinct user segments. For each avatar, provide:",
    "- Demographic indicators found in discussions",
    "- Primary pain points (with supporting quotes)",
    "- Typical vocabulary and phrase patterns",
    "- Common behaviors and usage patterns",
    "- Decision-making factors",
    "- Success criteria and definitions",
    "- Interaction preferences",
    "- Resource constraints",
    "- Notable quotes that epitomize this user type",
    "\nFor each avatar:",
    "1. Support characteristics with direct evidence from findings",
    "2. Link to specific discussion threads/comments",
    "3. Indicate relative size of this segment based on discussion frequency",
    "4. Highlight unique characteristics that distinguish this avatar",
    "5. Note any surprising or counter-intuitive traits",
    "\nFocus on creating distinct, non-overlapping avatars that capture major user segments evident in the discussions.",
    "Prioritize patterns that appeared consistently across multiple sources."
])

    prompt = "\n".join(prompt_parts)
    logger.debug(f"Generated prompt for topic: {topic_keyword}")
    return prompt 