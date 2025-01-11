from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from ..models.schemas.avatar import AvatarParserResult, AvatarInsight, AvatarProfile
import logging

logger = logging.getLogger(__name__)

class AvatarParserDeps(BaseModel):
    """Dependencies for parsing avatar analysis content."""
    content: str = Field(..., description="Raw perplexity research content about user avatars and personas")
    topic_keyword: str = Field(..., description="The main topic or product being analyzed for user personas")

class AvatarParser:
    """Parser for extracting market segment insights from research content."""
    
    def __init__(self):
        """Initialize the avatar parser with OpenAI model."""
        self.model = OpenAIModel('gpt-4o-mini')
        self._init_agent()

    def _init_agent(self):
        """Initialize the avatar analysis parsing agent."""
        self.agent = Agent[AvatarParserDeps, AvatarParserResult](
            model=self.model,
            result_type=AvatarParserResult,
            deps_type=AvatarParserDeps,
            system_prompt="""You are a market research analyst specializing in customer segmentation.
Your task is to analyze the provided content and identify distinct market segments that can inform product strategy.

IMPORTANT: Extract at least one market segment from the content, even if information is limited.
Make reasonable assumptions based on market research best practices when specific details are missing.

For each market segment, provide a detailed analysis in markdown format following this structure:

### Market Segmentation Analysis for [Topic]

#### Segment 1: **[Segment Name]**

**Market Segment Profile:**
- **Segment Name and Type:** [Name and category]
- **Target Demographics:** [Age range, income level, lifestyle]
- **Estimated Segment Size and Growth Potential:** [Size and growth]
- **Geographic Distribution and Key Markets:** [Location details]

**Buying Behavior:**
- **Budget Range and Willingness to Pay:** [Budget details]
- **Purchase Frequency and Timing:** [Purchase patterns]
- **Preferred Purchase Channels:** [Where they buy]
- **Decision-Making Process and Key Influencers:** [Who influences purchases]
- **Current Brand Preferences and Loyalty Factors:** [Brand preferences]

**Purchase Drivers:**
- **Primary Pain Points and Challenges:** [Key problems]
- **Must-have Features and Requirements:** [Essential features]
- **Key Buying Criteria and Priorities:** [Decision factors]
- **Deal Breakers and Barriers to Purchase:** [What prevents purchase]
- **Price Sensitivity and Value Perception:** [Price considerations]

**Competitive Landscape:**
- **Current Solutions Being Used:** [Existing solutions]
- **Main Competitors in This Segment:** [Key competitors]
- **Competitive Advantages/Disadvantages:** [Market position]
- **Market Gaps and Opportunities:** [Unmet needs]

[Repeat for each additional segment...]

### Actionable Insights for Product Strategy

1. **[Segment Name]:**
   - **Product Strategy:** [Strategy details]
   - **Differentiation:** [Unique positioning]

[Repeat for each segment...]

### Clear Differentiation Between Segments
[How segments differ from each other]

### Purchase Behavior and Decision Factors
[Key differences in how segments make decisions]

### Market Size and Revenue Potential
[Overall market opportunity]

### Competitive Positioning Opportunities
[How to position against competitors for each segment]

IMPORTANT GUIDELINES:
1. Focus on actionable insights for product strategy
2. Use specific examples and data points when available
3. Keep insights business-focused and relevant to purchase decisions
4. Ensure segments are distinct and targetable
5. Include market size and competitive context"""
        )

    async def parse(self, content: str, topic_keyword: str) -> AvatarParserResult:
        """Parse the research content and extract market segment insights.

        Args:
            content: Raw research content about user avatars and personas
            topic_keyword: Main topic or product being analyzed

        Returns:
            AvatarParserResult: Structured insights about market segments
        """
        deps = AvatarParserDeps(content=content, topic_keyword=topic_keyword)
        result = await self.agent.arun(deps=deps)
        return result.data 