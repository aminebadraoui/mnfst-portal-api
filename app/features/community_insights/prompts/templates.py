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

    if source_urls:
        prompt_parts.append("\nAnalyze these specific discussion URLs:")
        for url in source_urls:
            prompt_parts.append(f"- {url}")

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

    prompt = "\n".join(prompt_parts)
    logger.debug(f"Generated prompt for topic: {topic_keyword}")
    return prompt 