from pydantic import BaseModel
from datetime import datetime
from .categories import Category


class RoomBase(BaseModel):
    room_number: int


class RoomCreate(RoomBase):
    room_number: int | None = None
    category_id: int


class RoomUpdate(RoomBase):
    pass


class Room(RoomBase):
    id: int
    category: Category
    date_created: datetime
    date_deleted: datetime | None = None

    class Config:
        orm_mode = True
