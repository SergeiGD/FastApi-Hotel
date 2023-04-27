from pydantic import BaseModel, Field
from typing import Annotated


class TagBase(BaseModel):
    name: Annotated[str, Field(description='тег', example='Панорамный вид')]


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True
