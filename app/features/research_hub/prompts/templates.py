from typing import List
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class AnalysisType(str, Enum):
    PAIN = "pain"
    QUESTION = "question"
    PATTERN = "pattern"
    AVATAR = "avatar"
    PRODUCT = "product"

def generate_pain_prompt(
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    prompt = f"""Analyze community discussions about the following topic: `{topic_keyword}` with specific focus on: `{user_query}`. Search across Reddit and relevant forums.

Your task is to identify and analyze the most significant pain points and user frustrations in the community.

For each distinct pain point, analyze:

PAIN CONTEXT:
- What specific problem/frustration is the user experiencing?
- What makes this pain point particularly challenging?
- What have users already tried to solve it?
- How widespread is this issue in the community?

IMPACT & CONSEQUENCES:
- How does this pain point affect users' daily activities?
- What secondary problems does it cause?
- What opportunities/capabilities are users missing out on?
- What emotional impact does it have?

CURRENT SOLUTIONS:
- What workarounds have users discovered?
- Which solutions have proven most effective?
- What makes some solutions fail?
- What resources/support are users seeking?

For each pain point identified, provide:

1. Title: Clear description of the core pain point/frustration

2. Severity: Categorize as:
   - Critical (blocking core functionality/major user need)
   - Major (significantly impacts user experience)
   - Minor (inconvenient but workable)
   Include reasoning for severity level.

3. Evidence: Direct quotes showing:
   - The pain point being described
   - User's emotional response
   - Failed attempts to solve it
   - Impact on their experience

4. Impact Analysis:
   - Primary impact on user workflow
   - Secondary effects/consequences
   - Emotional/psychological impact
   - Business/productivity impact

5. Current Workarounds:
   - Most common solutions users try
   - What works partially
   - What doesn't work
   - Resources users need

6. Engagement Metrics:
   - How many users report this issue
   - Intensity of frustration
   - Discussion volume
   - Community support/agreement

Focus on:
- Pain points that significantly impact user experience
- Issues with strong emotional responses
- Problems affecting core user needs
- Frustrations without good solutions
- Issues that create cascading problems

Prioritize:
1. Critical blockers and major frustrations
2. Widespread issues affecting many users
3. Problems without good solutions
4. Issues with significant emotional impact
5. Pain points blocking key user goals

The goal is to understand the real human impact of these problems and identify where better solutions are most needed."""

    logger.debug(f"Generated pain analysis prompt for topic: {topic_keyword}")
    return prompt

def generate_question_prompt(
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    prompt = f"""Analyze community discussions about the following topic: `{topic_keyword}` with specific focus on: `{user_query}`. Search across Reddit and relevant forums.

Your task is to identify and analyze the most significant question patterns and knowledge sharing in the community. 

For each distinct question pattern, analyze:

QUESTION CONTEXT:
- What specific problem/challenge is the user trying to solve?
- What have they already tried?
- What's blocking them from finding a solution?
- How many others are facing similar issues?

SOLUTIONS & ADVICE:
- What are the most upvoted/accepted solutions?
- What specific steps or approaches worked?
- What common mistakes should be avoided?
- What alternatives were suggested?

COMMUNITY KNOWLEDGE:
- What expert insights were shared?
- What non-obvious tips emerged?
- What tools/resources were recommended?
- What best practices were emphasized?

For each question pattern identified, provide:

1. Title: Clear description of the core problem/question
2. Question Type: Categorize as:
   - Product Usage (how to use features)
   - Troubleshooting (solving problems)
   - Comparison (evaluating options)
   - Best Practices (recommended approaches)
   - Integration (working with other tools)
   - Setup/Configuration
   - Performance Optimization
   - Other (specify)

3. Evidence: Direct quotes showing:
   - The question being asked
   - Context of the problem
   - User's attempted solutions

4. Suggested Answers:
   - Most upvoted/accepted solution
   - Alternative approaches
   - Important caveats or prerequisites
   - Common pitfalls to avoid

5. Related Questions:
   - Follow-up questions
   - Common variations
   - Prerequisites to understand first
   - Next logical questions

6. Engagement Metrics:
   - Number of similar questions
   - Upvotes/agreement on solutions
   - Discussion volume
   - Success reports

Focus on:
- Questions that reveal deeper understanding gaps
- Questions with detailed, proven solutions
- Questions that generate meaningful discussion
- Questions that challenge common assumptions
- Questions that expose non-obvious insights

Prioritize:
1. Questions with high engagement and proven solutions
2. Questions that reveal systemic challenges
3. Questions with detailed, actionable answers
4. Questions that expose knowledge gaps
5. Questions that lead to best practices

The goal is to map the community's collective knowledge and create a practical guide for solving real user challenges."""

    logger.debug(f"Generated question analysis prompt for topic: {topic_keyword}")
    return prompt

def generate_pattern_prompt(
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    prompt = f"""Analyze community discussions about the following topic: `{topic_keyword}` with specific focus on: `{user_query}`. Search across Reddit and relevant forums.

Your task is to identify and analyze the most significant behavioral patterns and trends in the community. Focus on uncovering deep insights about user behaviors, preferences, and decision-making patterns.

For each distinct pattern, provide a comprehensive analysis:

PATTERN IDENTIFICATION:
- What is the core behavioral pattern or trend?
- What triggers or situations lead to this pattern?
- How consistently does this pattern appear?
- What variations of this pattern exist?

CONTEXT & MANIFESTATION:
- In what specific situations does this pattern occur?
- What user needs or goals drive this behavior?
- What external factors influence this pattern?
- How does this pattern evolve over time?

IMPACT & IMPLICATIONS:
- How does this pattern affect user success/failure?
- What opportunities does this pattern reveal?
- What risks or challenges does it indicate?
- What strategic insights can be derived?

For each pattern identified, provide:

1. Title: Clear, descriptive name for the pattern that captures its essence

2. Classification: Categorize as:
   - User Behavior (actions, habits, routines)
   - Decision Pattern (choice-making processes)
   - Interaction Model (tool/feature usage patterns)
   - Problem-Solving Approach (systematic ways of addressing challenges)
   - Social Dynamic (community interaction patterns)
   Include detailed reasoning for classification.

3. Evidence: Multiple direct quotes showing:
   - Clear pattern manifestation
   - Context and triggers
   - User awareness and reactions
   - Pattern variations
   Include source context and user sentiment.

4. Pattern Analysis:
   - Frequency and consistency
   - Trigger conditions
   - Success/failure factors
   - Evolution over time

5. Strategic Implications:
   - Product/service opportunities
   - Risk factors
   - Competitive advantages
   - Future trend projections

6. Validation Metrics:
   - Pattern frequency
   - User base distribution
   - Success correlation
   - Community validation

Focus on:
- Patterns that reveal strategic opportunities
- Behaviors indicating unmet needs
- Decision-making processes
- Emerging trends with growth potential
- Patterns suggesting market gaps

Prioritize:
1. High-impact patterns affecting core user experiences
2. Emerging trends with strategic implications
3. Patterns revealing competitive advantages
4. Counter-intuitive insights with validation
5. Behaviors indicating market evolution

The goal is to uncover actionable patterns that reveal strategic opportunities and guide product decisions. Each pattern should be thoroughly validated with multiple pieces of evidence and clear strategic implications."""

    logger.debug(f"Generated pattern analysis prompt for topic: {topic_keyword}")
    return prompt

def generate_avatar_prompt(
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    prompt = f"""Analyze the following topic: `{topic_keyword}` with specific focus on: `{user_query}`. Search across Reddit and relevant forums.

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

def generate_product_prompt(
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    prompt = f"""Analyze community discussions about the following topic: `{topic_keyword}` with specific focus on: `{user_query}`. Search across Reddit and relevant forums.

Your task is to identify and analyze significant product-related insights from community discussions. Focus on understanding product positioning, user satisfaction, and market opportunities.

For each product insight, analyze:

PRODUCT POSITIONING:
- What unique value does it offer?
- Who is the target user?
- How does it compare to alternatives?
- What is the pricing strategy?

USER EXPERIENCE:
- What features are most valued?
- What causes frustration?
- What learning curve exists?
- How reliable is the product?

MARKET DYNAMICS:
- What market gap does it fill?
- How strong is user loyalty?
- What competitive pressures exist?
- What trends affect adoption?

For each product analyzed, provide:

1. Product Overview:
   - Name and category
   - Price point and positioning
   - Target user segment
   - Unique value proposition
   Include direct quote about product positioning.

2. Feature Analysis:
   - Most praised features
   - Most criticized aspects
   - Missing capabilities
   - Competitive advantages
   Support with user quotes about features.

3. User Satisfaction:
   - Key benefits realized
   - Major pain points
   - Learning curve
   - Support experience
   Include specific user experiences.

4. Market Position:
   - Competitive strengths
   - Notable weaknesses
   - Market opportunities
   - Potential threats
   Support with market evidence.

5. Usage Patterns:
   - Common use cases
   - Integration scenarios
   - Workflow impacts
   - Success factors
   Include real usage examples.

6. Value Assessment:
   - Price-to-value ratio
   - ROI factors
   - Total cost considerations
   - Value drivers
   Support with user perspectives.

7. Validation Metrics:
   - Discussion frequency
   - Sentiment distribution
   - User adoption indicators
   - Market momentum

Focus on:
- Evidence-based insights
- User success factors
- Competitive differentiation
- Market opportunities
- Value drivers

Prioritize:
1. High-impact products
2. Growing solutions
3. Underserved needs
4. Strategic opportunities
5. Emerging alternatives

The goal is to uncover actionable product insights that reveal market opportunities and competitive advantages. Each insight should be thoroughly validated with multiple pieces of evidence and clear strategic implications."""

    logger.debug(f"Generated product analysis prompt for topic: {topic_keyword}")
    return prompt

def get_prompt(
    analysis_type: str,
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> str:
    """Get the appropriate prompt for the given analysis type."""
    generators = {
        AnalysisType.PAIN: generate_pain_prompt,
        AnalysisType.QUESTION: generate_question_prompt,
        AnalysisType.PATTERN: generate_pattern_prompt,
        AnalysisType.AVATAR: generate_avatar_prompt,
        AnalysisType.PRODUCT: generate_product_prompt
    }
    
    generator = generators.get(analysis_type)
    if not generator:
        raise ValueError(f"Invalid analysis type: {analysis_type}")
    
    return generator(
        topic_keyword=topic_keyword,
        user_query=user_query,
        source_urls=source_urls,
        product_urls=product_urls,
        use_only_specified_sources=use_only_specified_sources
    ) 