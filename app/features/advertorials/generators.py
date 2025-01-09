import asyncio
from .models import AdvertorialRequest
from .ai_agents.models import (
    StoryAdvertorialResult,
    InformationalAdvertorialResult,
    ValueAdvertorialResult
)
from .ai_agents.dependencies import (
    StoryAdvertorialDeps,
    InformationalAdvertorialDeps,
    ValueAdvertorialDeps
)
from .ai_agents.generators import (
    story_based_agent,
    informational_agent,
    value_based_agent
)

async def generate_advertorials(
    project_description: str,
    request: AdvertorialRequest
) -> tuple[StoryAdvertorialResult, InformationalAdvertorialResult, ValueAdvertorialResult]:
    """Generate all three types of advertorials in parallel."""
    
    # Create dependencies
    story_deps = StoryAdvertorialDeps(description=project_description)
    info_deps = InformationalAdvertorialDeps(description=project_description)
    value_deps = ValueAdvertorialDeps(description=project_description)

    # Generate advertorials in parallel
    results = await asyncio.gather(
        story_based_agent.run(request, deps=story_deps),
        informational_agent.run(request, deps=info_deps),
        value_based_agent.run(request, deps=value_deps)
    )

    return (
        results[0].data,
        results[1].data,
        results[2].data
    ) 