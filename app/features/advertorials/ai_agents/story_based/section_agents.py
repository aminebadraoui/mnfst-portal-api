from pydantic_ai import Agent, RunContext
from pydantic import BaseModel

class SectionDeps(BaseModel):
    project_description: str
    product_description: str
    previous_sections: dict[str, str]  # To maintain context between sections

class SectionResult(BaseModel):
    content: str

# Lead Section Agent
lead_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SectionDeps,
    result_type=SectionResult,
)

@lead_agent.system_prompt
def get_lead_prompt(ctx: RunContext[SectionDeps]) -> str:
    return f"""You are an expert copywriter specializing in story-based advertorials.
Write the lead section that describes a horrible situation and how the problem takes over life.
Use first person perspective and emotional language.

Project Description: {ctx.deps.project_description}
Product Description: {ctx.deps.product_description}

Previous sections written: {ctx.deps.previous_sections}"""

# Failed Solutions Agent
failed_solutions_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SectionDeps,
    result_type=SectionResult,
)

@failed_solutions_agent.system_prompt
def get_failed_solutions_prompt(ctx: RunContext[SectionDeps]) -> str:
    return f"""You are an expert copywriter specializing in story-based advertorials.
Write about previous attempts that didn't work, building on the lead section.
Use first person perspective and emotional language.

Project Description: {ctx.deps.project_description}
Product Description: {ctx.deps.product_description}

Previous sections written: {ctx.deps.previous_sections}"""

# Fear Agent
fear_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SectionDeps,
    result_type=SectionResult,
)

@fear_agent.system_prompt
def get_fear_prompt(ctx: RunContext[SectionDeps]) -> str:
    return f"""You are an expert copywriter specializing in story-based advertorials.
Write about worst case scenario fears, building on previous sections.
Use first person perspective and emotional language.

Project Description: {ctx.deps.project_description}
Product Description: {ctx.deps.product_description}

Previous sections written: {ctx.deps.previous_sections}"""

# Discovery Agent
discovery_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SectionDeps,
    result_type=SectionResult,
)

@discovery_agent.system_prompt
def get_discovery_prompt(ctx: RunContext[SectionDeps]) -> str:
    return f"""You are an expert copywriter specializing in story-based advertorials.
Write about how the protagonist discovered the product, making it feel like a moment of hope.
Use first person perspective and emotional language.

Project Description: {ctx.deps.project_description}
Product Description: {ctx.deps.product_description}

Previous sections written: {ctx.deps.previous_sections}"""

# Initial Skepticism Agent
skepticism_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SectionDeps,
    result_type=SectionResult,
)

@skepticism_agent.system_prompt
def get_skepticism_prompt(ctx: RunContext[SectionDeps]) -> str:
    return f"""You are an expert copywriter specializing in story-based advertorials.
Write about initial hesitation and doubts before trying the product.
Use first person perspective and emotional language.

Project Description: {ctx.deps.project_description}
Product Description: {ctx.deps.product_description}

Previous sections written: {ctx.deps.previous_sections}"""

# Product Experience Agent
experience_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SectionDeps,
    result_type=SectionResult,
)

@experience_agent.system_prompt
def get_experience_prompt(ctx: RunContext[SectionDeps]) -> str:
    return f"""You are an expert copywriter specializing in story-based advertorials.
Write about the immediate results and positive experience after using the product.
Use first person perspective and emotional language.

Project Description: {ctx.deps.project_description}
Product Description: {ctx.deps.product_description}

Previous sections written: {ctx.deps.previous_sections}"""

# First Call to Action Agent
first_cta_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SectionDeps,
    result_type=SectionResult,
)

@first_cta_agent.system_prompt
def get_first_cta_prompt(ctx: RunContext[SectionDeps]) -> str:
    return f"""You are an expert copywriter specializing in story-based advertorials.
Write a compelling first call to action that creates urgency to act now.
Use emotional triggers and clear benefits.

Project Description: {ctx.deps.project_description}
Product Description: {ctx.deps.product_description}

Previous sections written: {ctx.deps.previous_sections}"""

# Product Mechanism Agent
mechanism_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SectionDeps,
    result_type=SectionResult,
)

@mechanism_agent.system_prompt
def get_mechanism_prompt(ctx: RunContext[SectionDeps]) -> str:
    return f"""You are an expert copywriter specializing in story-based advertorials.
Write about how the product works in an engaging way that builds credibility.
Balance technical details with accessibility.

Project Description: {ctx.deps.project_description}
Product Description: {ctx.deps.product_description}

Previous sections written: {ctx.deps.previous_sections}"""

# Social Proof Agent
social_proof_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SectionDeps,
    result_type=SectionResult,
)

@social_proof_agent.system_prompt
def get_social_proof_prompt(ctx: RunContext[SectionDeps]) -> str:
    return f"""You are an expert copywriter specializing in story-based advertorials.
Write compelling social proof with specific examples and testimonials.
Make the evidence feel authentic and relatable.

Project Description: {ctx.deps.project_description}
Product Description: {ctx.deps.product_description}

Previous sections written: {ctx.deps.previous_sections}"""

# Extended Experience Agent
extended_experience_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SectionDeps,
    result_type=SectionResult,
)

@extended_experience_agent.system_prompt
def get_extended_experience_prompt(ctx: RunContext[SectionDeps]) -> str:
    return f"""You are an expert copywriter specializing in story-based advertorials.
Write about the long-term benefits and positive life changes from using the product.
Use first person perspective and focus on transformation.

Project Description: {ctx.deps.project_description}
Product Description: {ctx.deps.product_description}

Previous sections written: {ctx.deps.previous_sections}"""

# Scarcity/Urgency Agent
scarcity_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SectionDeps,
    result_type=SectionResult,
)

@scarcity_agent.system_prompt
def get_scarcity_prompt(ctx: RunContext[SectionDeps]) -> str:
    return f"""You are an expert copywriter specializing in story-based advertorials.
Write about why the reader needs to act now, creating genuine urgency.
Focus on what they might lose by waiting.

Project Description: {ctx.deps.project_description}
Product Description: {ctx.deps.product_description}

Previous sections written: {ctx.deps.previous_sections}"""

# Final Call to Action Agent
final_cta_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SectionDeps,
    result_type=SectionResult,
)

@final_cta_agent.system_prompt
def get_final_cta_prompt(ctx: RunContext[SectionDeps]) -> str:
    return f"""You are an expert copywriter specializing in story-based advertorials.
Write the final call to action with clear next steps.
Make it powerful and impossible to ignore.

Project Description: {ctx.deps.project_description}
Product Description: {ctx.deps.product_description}

Previous sections written: {ctx.deps.previous_sections}"""

# Export all agents
__all__ = [
    'lead_agent',
    'failed_solutions_agent',
    'fear_agent',
    'discovery_agent',
    'skepticism_agent',
    'experience_agent',
    'first_cta_agent',
    'mechanism_agent',
    'social_proof_agent',
    'extended_experience_agent',
    'scarcity_agent',
    'final_cta_agent',
    'SectionDeps',
    'SectionResult'
] 