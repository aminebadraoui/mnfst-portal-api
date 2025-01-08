from typing import TypeVar, Generic, Type
from pydantic import BaseModel
import logging

T = TypeVar('T')
logger = logging.getLogger(__name__)

class BaseAnalysisParser(Generic[T]):
    def __init__(self, result_model: Type[T]):
        self.result_model = result_model

    async def process_section(self, content: str, topic_keyword: str, user_query: str) -> T:
        """Process the content and return structured insights."""
        raise NotImplementedError("Subclasses must implement process_section") 