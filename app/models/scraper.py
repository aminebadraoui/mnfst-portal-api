from pydantic import BaseModel

class ContentChunk(BaseModel):
    """A chunk of content from a scraped webpage."""
    text: str
    source_url: str
    chunk_number: int = 1
    total_chunks: int = 1
    start_index: int = 0
    end_index: int = 0
    metadata: dict = {} 