from pydantic import BaseModel


class StoryAdvertorialDeps(BaseModel):
    description: str


class InformationalAdvertorialDeps(BaseModel):
    description: str


class ValueAdvertorialDeps(BaseModel):
    description: str 