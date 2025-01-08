from typing import List
import logging

logger = logging.getLogger(__name__)

def get_pain_analysis_prompt(
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """
    Generate a prompt for pain & frustration analysis.
    """
    prompt_parts = [
        f"Analyze community discussions about the following topic: `{topic_keyword}` with specific focus on: `{user_query}`. Search across Reddit and relevant forums.",
        "\nFocus on pain points and frustrations. Analyze:",
        "- Most emotionally charged complaints",
        "- Recurring sources of anger",
        "- Hidden frustrations",
        "- Indirect expressions of dissatisfaction",
        "- Cascade effects of problems",
        "- Time patterns in complaint posting"
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
        "\nFocus on emotional impact and user frustrations.",
        "Organize findings by engagement level (most discussed/upvoted first).",
    ])

    prompt = "\n".join(prompt_parts)
    logger.debug(f"Generated pain analysis prompt for topic: {topic_keyword}")
    return prompt

def get_question_mapping_prompt(
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """
    Generate a prompt for question & advice mapping.
    """
    prompt_parts = [
        f"Analyze community discussions about the following topic: `{topic_keyword}` with specific focus on: `{user_query}`. Search across Reddit and relevant forums.",
        "\nFocus on questions and advice. Analyze:",
        "- Most frequently asked questions",
        "- Most upvoted advice",
        "- Most debated solutions",
        "- Most repeated recommendations",
        "- Success stories with details",
        "- Failure patterns with context"
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
        "\nFocus on what users are asking and what solutions work.",
        "Organize findings by engagement level (most discussed/upvoted first).",
    ])

    prompt = "\n".join(prompt_parts)
    logger.debug(f"Generated question mapping prompt for topic: {topic_keyword}")
    return prompt

def get_pattern_detection_prompt(
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """
    Generate a prompt for pattern detection.
    """
    prompt_parts = [
        f"Analyze community discussions about the following topic: `{topic_keyword}` with specific focus on: `{user_query}`. Search across Reddit and relevant forums.",
        "\nFocus on patterns and trends. Analyze:",
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
        "\nFocus on unexpected patterns and hidden relationships.",
        "Organize findings by engagement level (most discussed/upvoted first).",
    ])

    prompt = "\n".join(prompt_parts)
    logger.debug(f"Generated pattern detection prompt for topic: {topic_keyword}")
    return prompt

def get_avatars_prompt(
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """
    Generate a prompt for avatar analysis.
    """
    prompt_parts = [
        f"Analyze community discussions about the following topic: `{topic_keyword}` with specific focus on: `{user_query}`. Search across Reddit and relevant forums.",
        "\nConstruct detailed customer avatars that represent distinct user segments. For each avatar, provide:",
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
    ]

    prompt = "\n".join(prompt_parts)
    logger.debug(f"Generated avatars prompt for topic: {topic_keyword}")
    return prompt

def get_product_analysis_prompt(
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """
    Generate a prompt for product analysis.
    """
    prompt_parts = [
        f"Analyze popular products related to the following topic: `{topic_keyword}` with specific focus on: `{user_query}`. Search across Amazon, eBay, and Google Shopping.",
        "\nFocus on product analysis. For each platform, analyze:",
        "- Most popular products in this category",
        "- Price ranges and variations",
        "- Common positive feedback themes",
        "- Recurring complaints and issues",
        "- Potential market gaps and opportunities",
        "- Customer satisfaction patterns",
        "- Feature comparisons between products"
    ]

    prompt_parts.extend([
        "\nFor each product insight, provide:",
        "1. Product name and description",
        "2. Platform (Amazon/eBay/Google Shopping)",
        "3. Price range",
        "4. List of positive feedback points",
        "5. List of negative feedback points",
        "6. Identified market gap or opportunity",
        "7. Source URL in plain text",
        "8. Engagement metrics (reviews, ratings)",
        "9. Frequency of mentions",
        "10. Correlation with other products",
        "11. Market significance",
        "\nFocus on identifying patterns in customer feedback and market opportunities.",
        "Organize findings by popularity and engagement level.",
    ])

    prompt = "\n".join(prompt_parts)
    logger.debug(f"Generated product analysis prompt for topic: {topic_keyword}")
    return prompt

def get_failed_solutions_prompt(
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """
    Generate a prompt for failed solutions analysis.
    """
    prompt_parts = [
        f"Analyze community discussions about the following topic: `{topic_keyword}` with specific focus on: `{user_query}`. Search across Reddit and relevant forums.",
        "\nFocus on failed solutions and attempts. Analyze:",
        "- Most common failed approaches",
        "- Solutions that made problems worse",
        "- Abandoned treatment methods",
        "- Wasted investments",
        "- Ineffective products or services",
        "- Misguided advice that backfired",
        "- Common mistakes and pitfalls"
    ]

    prompt_parts.extend([
        "\nFor each insight, provide:",
        "1. A clear title describing the failed solution",
        "2. Direct quotes as evidence",
        "3. Source URL in plain text",
        "4. Engagement metrics (upvotes, comments)",
        "5. How frequently this failure appears",
        "6. Related patterns or correlations",
        "7. The significance or impact on users",
        "\nFocus on understanding why these solutions failed and what can be learned.",
        "Organize findings by frequency and impact level.",
    ])

    prompt = "\n".join(prompt_parts)
    logger.debug(f"Generated failed solutions prompt for topic: {topic_keyword}")
    return prompt


