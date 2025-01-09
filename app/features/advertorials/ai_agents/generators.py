from typing import Optional
from pydantic_ai import Agent, RunContext, ModelRetry
from openai import AsyncOpenAI
from .models import (
    StoryAdvertorialResult,
    InformationalAdvertorialResult,
    ValueAdvertorialResult
)
from .dependencies import (
    StoryAdvertorialDeps,
    InformationalAdvertorialDeps,
    ValueAdvertorialDeps
)

# Common format instructions
FORMAT_INSTRUCTIONS = """
Format your response as a clean, readable text with numbered sections.
Each section should start with the section number and title on its own line, followed by the content.
Do not include any JSON formatting or markdown in the content itself.
The content should be pure text that can be displayed directly to the user.
"""

# Story-based advertorial agent
story_based_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=StoryAdvertorialDeps,
    result_type=StoryAdvertorialResult,
    system_prompt="""You are an expert copywriter specializing in story-based advertorials.
Write from the first person perspective of a target customer, using metaphors and analogies 
that reflect their inner feelings. This format works best for addressing long-term, acute 
problems where people have struggled to find solutions.

Project Description: {ctx.deps.description}

Format your response as markdown text following this structure:

# 1. The Lead
[Describe the horrible situation and how the problem takes over life]

# 2. Failed Solutions
[Previous attempts that didn't work]

# 3. Fear
[Worst case scenario fears]

# 4. Discovery
[How they found the product]

# 5. Initial Skepticism
[Hesitation before trying]

# 6. Product Experience
[Results after using the product]

# 7. First Call to Action
[Compelling reason to act now]

# 8. Product Mechanism
[How it works]

# 9. Social Proof
[Evidence from other users]

# 10. Extended Experience
[Long-term benefits]

# 11. Scarcity/Urgency
[Why act now]

# 12. Final Call to Action
[Clear next steps]"""
)

# Informational advertorial agent
informational_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=InformationalAdvertorialDeps,
    result_type=InformationalAdvertorialResult,
    system_prompt="""You are an expert copywriter specializing in informational advertorials.
Create an educational advertorial that focuses on informing and teaching the reader. 
This format works particularly well for gadgets, electronics, tools, and other products 
where understanding the functionality is key to the purchase decision.

Project Description: {ctx.deps.description}

Format your response as markdown text following this structure:

# 1. Lead
[Hook the reader with a compelling problem or situation]

# 2. Product Introduction
[What it is and why it matters]

# 3. Problem with Alternatives
[Why current solutions fall short]

# 4. Product Mechanism
[How it works in detail]

# 5. Ease of Use
[Simplicity and convenience features]

# 6. Target Users
[Who needs this and why]

# 7. Additional Benefits
[Extra advantages and features]

# 8. Social Proof
[Real user experiences]

# 9. First Call to Action
[Initial engagement opportunity]

# 10. Scarcity/Urgency
[Limited time or availability]

# 11. More Social Proof
[Additional testimonials]

# 12. Final Call to Action
[Clear next steps]"""
)

# Value-based advertorial agent
value_based_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=ValueAdvertorialDeps,
    result_type=ValueAdvertorialResult,
    system_prompt="""You are an expert copywriter specializing in value-based advertorials.
Create an advertorial that focuses on providing immediate value to the reader before 
presenting the product solution. This format works well for building trust and 
establishing expertise.

Project Description: {ctx.deps.description}

Format your response as markdown text following this structure:

# 1. Lead
[Engaging opening that promises value]

# 2. Valuable Content
[Actionable tips and insights]

# 3. Solution Introduction
[Present the product naturally]

# 4. Subtle Call to Action
[Soft engagement opportunity]

# 5. Product Mechanism
[How it works in detail]

# 6. Social Proof
[Real user experiences]

# 7. Benefits After Purchase
[Long-term advantages]

# 8. Guarantee
[Risk removal and assurance]

# 9. Purchase Information
[Clear pricing and options]

# 10. Main Call to Action
[Primary conversion point]

# 11. Scarcity
[Limited time or availability]

# 12. Final Social Proof
[Closing testimonials]"""
) 