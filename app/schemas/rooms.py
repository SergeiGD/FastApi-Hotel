from pydantic import BaseModel
from datetime import datetime
from .categories import Category


class RoomBase(BaseModel):
    room_number: int
    category: Category


class RoomCreate(RoomBase):
    pass


class Room(RoomBase):
    id: int
    date_created: datetime
    date_deleted: datetime | None = None

    class Config:
        orm_mode = True
