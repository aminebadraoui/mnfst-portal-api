from .pain import PainPerplexityClient
from .question import QuestionPerplexityClient
from .pattern import PatternPerplexityClient
from .product import ProductPerplexityClient
from .avatar import AvatarPerplexityClient

__all__ = [
    'PainPerplexityClient',
    'QuestionPerplexityClient',
    'PatternPerplexityClient',
    'ProductPerplexityClient',
    'AvatarPerplexityClient'
]

# Client mapping
CLIENT_MAP = {
    "Pain & Frustration Analysis": PainPerplexityClient,
    "Question & Advice Mapping": QuestionPerplexityClient,
    "Pattern Detection": PatternPerplexityClient,
    "Popular Products Analysis": ProductPerplexityClient,
    "Avatars": AvatarPerplexityClient
}

def get_client(section_type: str):
    """Get the appropriate Perplexity client for a section type."""
    client_class = CLIENT_MAP.get(section_type)
    if not client_class:
        raise ValueError(f"Unknown section type: {section_type}")
    return client_class() 