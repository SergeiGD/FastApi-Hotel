from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class CategoryBase(BaseModel):
    name: str
    description: str
    price: Decimal
    prepayment_percent: float
    refund_percent: float
    main_photo_path: str
    rooms_count: int
    floors: int
    beds: int
    square: float


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    is_hidden: bool
    date_created: datetime
    date_deleted: datetime | None = None

    class Config:
        orm_mode = True
