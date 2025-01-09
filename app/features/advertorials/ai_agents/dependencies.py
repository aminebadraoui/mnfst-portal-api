from pydantic import BaseModel


class StoryAdvertorialDeps(BaseModel):
    project_description: str
    product_description: str


class InformationalAdvertorialDeps(BaseModel):
    project_description: str
    product_description: str


class ValueAdvertorialDeps(BaseModel):
    project_description: str
    product_description: str 