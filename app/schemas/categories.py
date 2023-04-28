from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from datetime import datetime
from decimal import Decimal
from fastapi import Form
from dataclasses import dataclass
from hotel_business_module.models.categories import Category as DbCategory


class CategoryBase(BaseModel):
    name: str = Field(min_length=3)
    description: str
    price: Decimal = Field(gt=0)
    prepayment_percent: float = Field(gt=0, lt=100)
    refund_percent: float = Field(gt=0, lt=100)
    rooms_count: int = Field(gt=0)
    floors: int = Field(gt=0, default=1)
    beds: int = Field(gt=0)
    square: float = Field(gt=20)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    is_hidden: bool
    main_photo_path: str
    date_created: datetime

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'id': 23,
                'name': 'Супею люкс',
                'description': 'Раскошные апартаменты на двоих человек',
                'price': 3999,
                'prepayment_percent': 25,
                'refund_percent': 10,
                'rooms_count': 5,
                'floors': 2,
                'beds': 3,
                'square': 115,
                'is_hidden': False,
                'date_created': '2023-03-27T14:10:38.350220',
                'main_photo_path': '/home/sergei/python/hotel/app/media/eb3c13a214484b50bb3fa728970941cf.jpg'
            },
        }


@dataclass
class CategoryCreateForm:
    """
    Класс преобразования форм даты в модель pydantic при создании категории
    """
    name: Annotated[str, Form()]
    description: Annotated[str, Form()]
    price: Annotated[Decimal, Form()]
    prepayment_percent: Annotated[float, Form()]
    refund_percent: Annotated[float, Form()]
    rooms_count: Annotated[int, Form()]
    floors: Annotated[int, Form()]
    beds: Annotated[int, Form()]
    square: Annotated[float, Form()]

    def convert_to_model(self) -> CategoryCreate:
        """
        Преобразование в модель pydantic
        :return: модель pydantic
        """
        return CategoryCreate(**jsonable_encoder(self))


@dataclass
class CategoryUpdateForm:
    """
    Класс преобразования форм даты в модель pydantic при изменении категории
    """
    name: Annotated[str, Form()] | None = None
    description: Annotated[str, Form()] | None = None
    price: Annotated[Decimal, Form()] | None = None
    prepayment_percent: Annotated[float, Form()] | None = None
    refund_percent: Annotated[float, Form()] | None = None
    rooms_count: Annotated[int, Form()] | None = None
    floors: Annotated[int, Form()] | None = None
    beds: Annotated[int, Form()] | None = None
    square: Annotated[float, Form()] | None = None

    def convert_to_model(self, db_category: DbCategory) -> CategoryUpdate:
        """
        Преобразование в модель pydantic
        :param db_category: категория, которую нужно изменить
        :return: модель pydantic
        """
        return CategoryUpdate(
            # если какое-то из значений не передано, то берем его из категории, которую нужно изменить
            **{attr: value if value is not None else db_category.__dict__[attr] for attr, value in self.__dict__.items()}
        )
