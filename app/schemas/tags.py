from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(min_length=3)


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    pass


class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True
