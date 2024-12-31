from pydantic import BaseModel

class ContentChunk(BaseModel):
    """A chunk of content from a scraped webpage."""
    text: str
    start_index: int = 0
    end_index: int = 0
    metadata: dict = {}
    source_url: str = "" 