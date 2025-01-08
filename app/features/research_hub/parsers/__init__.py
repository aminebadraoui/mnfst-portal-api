from .pain import PainParser
from .question import QuestionParser
from .pattern import PatternParser
from .product import ProductParser
from .avatar import AvatarParser

__all__ = [
    'PainParser',
    'QuestionParser',
    'PatternParser',
    'ProductParser',
    'AvatarParser'
]

# Parser mapping
PARSER_MAP = {
    "Pain & Frustration Analysis": PainParser,
    "Question & Advice Mapping": QuestionParser,
    "Pattern Detection": PatternParser,
    "Popular Products Analysis": ProductParser,
    "Avatars": AvatarParser
}

def get_parser(section_type: str):
    """Get the appropriate parser for a section type."""
    parser_class = PARSER_MAP.get(section_type)
    if not parser_class:
        raise ValueError(f"Unknown section type: {section_type}")
    return parser_class() 