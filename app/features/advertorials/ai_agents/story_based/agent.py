from pydantic_ai import Agent, RunContext
from openai import AsyncOpenAI
import json
from ..models import StoryAdvertorialResult
from ..dependencies import StoryAdvertorialDeps
from .section_agents import (
    lead_agent,
    failed_solutions_agent,
    fear_agent,
    discovery_agent,
    skepticism_agent,
    experience_agent,
    first_cta_agent,
    mechanism_agent,
    social_proof_agent,
    extended_experience_agent,
    scarcity_agent,
    final_cta_agent,
    SectionDeps,
    SectionResult
)

def clean_content(content: str) -> str:
    """Clean content to ensure it can be safely included in JSON."""
    # Replace newlines with spaces to prevent JSON parsing issues
    content = content.replace('\n', ' ')
    # Escape quotes
    content = content.replace('"', '\\"')
    # Truncate if too long (to prevent token limit issues)
    return content[:4000] if len(content) > 4000 else content

# Story-based advertorial agent
story_based_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=StoryAdvertorialDeps,
    result_type=StoryAdvertorialResult,
    system_prompt="""You are an expert copywriter orchestrating the creation of a story-based advertorial.
Your task is to generate a complete advertorial by using specialized tools to create each section.
Each section builds upon the previous ones to create a cohesive narrative.

Follow these steps:
1. Use generate_lead() to create the opening section
2. Use generate_failed_solutions() to add the next section
3. Use generate_fear() to add the next section
4. Continue with each section in sequence
5. Finally, use finalize_advertorial() to ensure coherence and flow

Important: Keep each section concise and focused.

The final advertorial should follow this structure:
1. The Lead (emotional hook)
2. Failed Solutions (previous attempts)
3. Fear (worst case scenarios)
4. Discovery (finding the product)
5. Initial Skepticism (hesitation)
6. Product Experience (results)
7. First Call to Action
8. Product Mechanism (how it works)
9. Social Proof (testimonials)
10. Extended Experience (long-term benefits)
11. Scarcity/Urgency (why act now)
12. Final Call to Action

Return the final content in markdown format with proper section headers."""
)

@story_based_agent.tool
async def generate_lead(ctx: RunContext[StoryAdvertorialDeps]) -> str:
    """Generate the lead section of the advertorial."""
    deps = SectionDeps(
        project_description=ctx.deps.project_description,
        product_description=ctx.deps.product_description,
        previous_sections={}
    )
    result = await lead_agent.run(
        "Generate the lead section",
        deps=deps
    )
    return "# The Lead\n\n" + result.data.content

@story_based_agent.tool
async def generate_failed_solutions(ctx: RunContext[StoryAdvertorialDeps]) -> str:
    """Generate the failed solutions section."""
    deps = SectionDeps(
        project_description=ctx.deps.project_description,
        product_description=ctx.deps.product_description,
        previous_sections={}
    )
    result = await failed_solutions_agent.run(
        "Generate the failed solutions section",
        deps=deps
    )
    return "\n\n# Failed Solutions\n\n" + result.data.content

@story_based_agent.tool
async def generate_fear(ctx: RunContext[StoryAdvertorialDeps]) -> str:
    """Generate the fear section."""
    deps = SectionDeps(
        project_description=ctx.deps.project_description,
        product_description=ctx.deps.product_description,
        previous_sections={}
    )
    result = await fear_agent.run(
        "Generate the fear section",
        deps=deps
    )
    return "\n\n# The Fear\n\n" + result.data.content

@story_based_agent.tool
async def generate_discovery(ctx: RunContext[StoryAdvertorialDeps]) -> str:
    """Generate the discovery section."""
    deps = SectionDeps(
        project_description=ctx.deps.project_description,
        product_description=ctx.deps.product_description,
        previous_sections={}
    )
    result = await discovery_agent.run(
        "Generate the discovery section",
        deps=deps
    )
    return "\n\n# The Discovery\n\n" + result.data.content

@story_based_agent.tool
async def generate_skepticism(ctx: RunContext[StoryAdvertorialDeps]) -> str:
    """Generate the skepticism section."""
    deps = SectionDeps(
        project_description=ctx.deps.project_description,
        product_description=ctx.deps.product_description,
        previous_sections={}
    )
    result = await skepticism_agent.run(
        "Generate the skepticism section",
        deps=deps
    )
    return "\n\n# Initial Skepticism\n\n" + result.data.content

@story_based_agent.tool
async def generate_experience(ctx: RunContext[StoryAdvertorialDeps]) -> str:
    """Generate the product experience section."""
    deps = SectionDeps(
        project_description=ctx.deps.project_description,
        product_description=ctx.deps.product_description,
        previous_sections={}
    )
    result = await experience_agent.run(
        "Generate the product experience section",
        deps=deps
    )
    return "\n\n# Product Experience\n\n" + result.data.content

@story_based_agent.tool
async def generate_first_cta(ctx: RunContext[StoryAdvertorialDeps]) -> str:
    """Generate the first call to action section."""
    deps = SectionDeps(
        project_description=ctx.deps.project_description,
        product_description=ctx.deps.product_description,
        previous_sections={}
    )
    result = await first_cta_agent.run(
        "Generate the first call to action section",
        deps=deps
    )
    return "\n\n# Take Action Now\n\n" + result.data.content

@story_based_agent.tool
async def generate_mechanism(ctx: RunContext[StoryAdvertorialDeps]) -> str:
    """Generate the product mechanism section."""
    deps = SectionDeps(
        project_description=ctx.deps.project_description,
        product_description=ctx.deps.product_description,
        previous_sections={}
    )
    result = await mechanism_agent.run(
        "Generate the product mechanism section",
        deps=deps
    )
    return "\n\n# How It Works\n\n" + result.data.content

@story_based_agent.tool
async def generate_social_proof(ctx: RunContext[StoryAdvertorialDeps]) -> str:
    """Generate the social proof section."""
    deps = SectionDeps(
        project_description=ctx.deps.project_description,
        product_description=ctx.deps.product_description,
        previous_sections={}
    )
    result = await social_proof_agent.run(
        "Generate the social proof section",
        deps=deps
    )
    return "\n\n# What Others Are Saying\n\n" + result.data.content

@story_based_agent.tool
async def generate_extended_experience(ctx: RunContext[StoryAdvertorialDeps]) -> str:
    """Generate the extended experience section."""
    deps = SectionDeps(
        project_description=ctx.deps.project_description,
        product_description=ctx.deps.product_description,
        previous_sections={}
    )
    result = await extended_experience_agent.run(
        "Generate the extended experience section",
        deps=deps
    )
    return "\n\n# Long-Term Benefits\n\n" + result.data.content

@story_based_agent.tool
async def generate_scarcity(ctx: RunContext[StoryAdvertorialDeps]) -> str:
    """Generate the scarcity/urgency section."""
    deps = SectionDeps(
        project_description=ctx.deps.project_description,
        product_description=ctx.deps.product_description,
        previous_sections={}
    )
    result = await scarcity_agent.run(
        "Generate the scarcity/urgency section",
        deps=deps
    )
    return "\n\n# Limited Time Opportunity\n\n" + result.data.content

@story_based_agent.tool
async def generate_final_cta(ctx: RunContext[StoryAdvertorialDeps]) -> str:
    """Generate the final call to action section."""
    deps = SectionDeps(
        project_description=ctx.deps.project_description,
        product_description=ctx.deps.product_description,
        previous_sections={}
    )
    result = await final_cta_agent.run(
        "Generate the final call to action section",
        deps=deps
    )
    return "\n\n# Don't Wait - Act Now\n\n" + result.data.content

@story_based_agent.tool
async def finalize_advertorial(
    ctx: RunContext[StoryAdvertorialDeps],
    raw_content: str
) -> StoryAdvertorialResult:
    """Do a final coherence pass on the complete advertorial."""
    # Create a new agent for the final pass
    coherence_agent = Agent(
        'openai:gpt-4o-mini',
        system_prompt="""You are an expert copywriter doing a final coherence pass on an advertorial.
Your task is to:
1. Ensure smooth transitions between sections
2. Maintain consistent tone and voice
3. Strengthen narrative flow
4. Fix any inconsistencies
5. Ensure all sections work together to tell a compelling story

Do not change the core message or structure, just improve coherence and flow."""
    )
    
    # Run the coherence pass
    result = await coherence_agent.run(
        f"Please improve the coherence and flow of this advertorial while maintaining its structure:\n\n{raw_content}"
    )
    
    # Extract the content string from the result
    final_content = result.data
    if not isinstance(final_content, str):
        final_content = str(final_content)
    
    return StoryAdvertorialResult(content=final_content) 