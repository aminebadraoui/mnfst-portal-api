from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class Task(BaseModel):
    id: str
    status: str
    sections: List[Dict[str, Any]] = []
    avatars: List[Dict[str, Any]] = []
    error: Optional[str] = None
    raw_response: Optional[str] = None 