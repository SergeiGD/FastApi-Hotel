from pydantic import BaseModel, Field
from datetime import datetime
from .categories import Category


class RoomBase(BaseModel):
    room_number: int = Field(gt=0)


class RoomCreate(RoomBase):
    room_number: int | None = Field(gt=0, default=None)
    category_id: int


class RoomUpdate(RoomBase):
    pass


class Room(RoomBase):
    id: int
    category: Category
    date_created: datetime

    class Config:
        orm_mode = True
