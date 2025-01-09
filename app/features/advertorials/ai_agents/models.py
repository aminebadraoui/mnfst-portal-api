from pydantic import BaseModel


class StoryAdvertorialResult(BaseModel):
    content: str


class InformationalAdvertorialResult(BaseModel):
    content: str


class ValueAdvertorialResult(BaseModel):
    content: str 