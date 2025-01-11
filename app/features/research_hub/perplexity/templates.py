from typing import List

def generate_avatar_prompt(
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """Generate a prompt for market segment analysis."""
    prompt = f"""Based on the following topic: `{topic_keyword}` with specific focus on: `{user_query}`, identify and analyze key market segments and customer personas.

You are a market research analyst. Focus on identifying distinct, actionable market segments that can inform product strategy and market positioning.

For each market segment, analyze:

1. Market Segment Profile
- Segment name and type (e.g., "Enterprise Early Adopters", "Budget-Conscious SMBs")
- Target demographics (age range, income level, company size, industry)
- Estimated segment size and growth potential
- Geographic distribution and key markets

2. Buying Behavior
- Budget range and willingness to pay
- Purchase frequency and timing
- Preferred purchase channels (direct, online, resellers)
- Decision-making process and key influencers
- Current brand preferences and loyalty factors

3. Purchase Drivers
- Primary pain points and challenges
- Must-have features and requirements
- Key buying criteria and priorities
- Deal breakers and barriers to purchase
- Price sensitivity and value perception

4. Competitive Landscape
- Current solutions being used
- Main competitors in this segment
- Competitive advantages/disadvantages
- Market gaps and opportunities
- Segment-specific market trends

Focus on:
- Actionable insights for product strategy
- Clear differentiation between segments
- Purchase behavior and decision factors
- Market size and revenue potential
- Competitive positioning opportunities

Avoid:
- Generic demographic descriptions
- Non-business-related characteristics
- Unsupported assumptions
- Technical details unless relevant to purchase decisions

Format your response to clearly distinguish between segments. Support insights with specific examples and market indicators where possible. Focus on information that directly impacts product strategy and go-to-market planning."""

    logger.debug(f"Generated avatar analysis prompt for topic: {topic_keyword}")
    return prompt 