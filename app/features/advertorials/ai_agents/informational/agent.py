from pydantic_ai import Agent, RunContext
from openai import AsyncOpenAI
from ..models import InformationalAdvertorialResult
from ..dependencies import InformationalAdvertorialDeps

# Informational advertorial agent
informational_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=InformationalAdvertorialDeps,
    result_type=InformationalAdvertorialResult,
)

@informational_agent.system_prompt
def get_info_system_prompt(ctx: RunContext[InformationalAdvertorialDeps]) -> str:
    return f"""You are an expert copywriter specializing in informational advertorials.
Create an educational advertorial that focuses on informing and teaching the reader. 
This format works particularly well for gadgets, electronics, tools, and other products 
where understanding the functionality is key to the purchase decision.

Project Description: {ctx.deps.project_description}
Product Description: {ctx.deps.product_description}

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