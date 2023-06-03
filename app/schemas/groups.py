from pydantic import BaseModel, Field


class GroupBase(BaseModel):
    name: str = Field(min_length=3)


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    pass


class Group(GroupBase):
    id: int

    class Config:
        orm_mode = True
