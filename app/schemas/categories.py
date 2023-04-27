from pydantic import BaseModel
from typing import Annotated
from datetime import datetime
from decimal import Decimal
from fastapi import Form
from dataclasses import dataclass


class CategoryBase(BaseModel):
    name: str
    description: str
    price: Decimal
    prepayment_percent: float
    refund_percent: float
    rooms_count: int
    floors: int
    beds: int
    square: float


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    is_hidden: bool
    main_photo_path: str
    date_created: datetime
    date_deleted: datetime | None = None

    class Config:
        orm_mode = True


@dataclass
class CategoryCreateForm:
    name: Annotated[str, Form()]
    description: Annotated[str, Form()]
    price: Annotated[Decimal, Form()]
    prepayment_percent: Annotated[float, Form()]
    refund_percent: Annotated[float, Form()]
    rooms_count: Annotated[int, Form()]
    floors: Annotated[int, Form()]
    beds: Annotated[int, Form()]
    square: Annotated[float, Form()]

    def convert_to_model(self):
        return CategoryCreate(**self.__dict__)


@dataclass
class CategoryUpdateForm(CategoryCreateForm):
    def convert_to_model(self):
        return CategoryUpdate(**self.__dict__)
