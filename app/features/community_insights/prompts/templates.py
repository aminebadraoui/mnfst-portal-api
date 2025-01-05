from typing import List
import logging

logger = logging.getLogger(__name__)

def get_pain_analysis_prompt(
    topic_keyword: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """
    Generate a prompt for pain & frustration analysis.
    """
    prompt_parts = [
        f"Analyze community discussions about the following topic: `{topic_keyword}` . Search across Reddit and relevant forums.",
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
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """
    Generate a prompt for question & advice mapping.
    """
    prompt_parts = [
        f"Analyze community discussions about the following topic: `{topic_keyword}` . Search across Reddit and relevant forums.",
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
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """
    Generate a prompt for pattern detection.
    """
    prompt_parts = [
        f"Analyze community discussions about the following topic: `{topic_keyword}` . Search across Reddit and relevant forums.",
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
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """
    Generate a prompt for question & advice mapping.
    """
    prompt_parts = [
        f"Analyze community discussions about the following topic: `{topic_keyword}` . Search across Reddit and relevant forums.",
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

# For backward compatibility
def get_insights_prompt(
    topic_keyword: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """
    Generate a combined prompt for insights analysis.
    """
    pain_prompt = get_pain_analysis_prompt(topic_keyword, source_urls, product_urls, use_only_specified_sources)
    question_prompt = get_question_mapping_prompt(topic_keyword, source_urls, product_urls, use_only_specified_sources)
    pattern_prompt = get_pattern_detection_prompt(topic_keyword, source_urls, product_urls, use_only_specified_sources)
    return f"{pain_prompt}\n\n{question_prompt}\n\n{pattern_prompt}"

# For backward compatibility
def get_community_insights_prompt(
    topic_keyword: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """
    Generate a combined prompt for community insights analysis.
    """
    insights_prompt = get_insights_prompt(topic_keyword, source_urls, product_urls, use_only_specified_sources)
    avatars_prompt = get_avatars_prompt(topic_keyword, source_urls, product_urls, use_only_specified_sources)
    return f"{insights_prompt}\n\n{avatars_prompt}" 