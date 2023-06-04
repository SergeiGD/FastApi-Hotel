from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from datetime import datetime
from decimal import Decimal
from fastapi import Form
from dataclasses import dataclass
from hotel_business_module.models.categories import Category as DbCategory


class SaleBase(BaseModel):
    name: str = Field(min_length=3)
    description: str
    discount: float = Field(gt=0, lt=100)
    start_date: datetime
    end_date: datetime


class SaleCreate(SaleBase):
    pass


class SaleUpdate(SaleBase):
    pass


class Sale(SaleBase):
    id: int
    image_path: str
    date_created: datetime

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'id': 23,
                'name': 'Майские скидки',
                'description': 'Скидки на весь май 30%',
                'discount': 30,
                'start_date': '2023-05-01T14:10:38.350220',
                'end_date': '2023-05-30T14:10:38.350220',
                'date_created': '2023-04-27T14:10:38.350220',
                'image_path': '/home/sergei/python/hotel/app/media/eb3c13a214484b50bb3fa728970941cf.jpg'
            },
        }


@dataclass
class SaleCreateForm:
    """
    Класс преобразования форм даты в модель pydantic при создании скидки
    """
    name: Annotated[str, Form(min_length=3)]
    description: Annotated[str, Form()]
    discount: Annotated[float, Form(gt=0, lt=100)]
    start_date: Annotated[datetime, Form()]
    end_date: Annotated[datetime, Form()]

    def convert_to_model(self) -> SaleCreate:
        """
        Преобразование в модель pydantic
        :return: модель pydantic
        """
        return SaleCreate(**jsonable_encoder(self))


@dataclass
class SaleUpdateForm:
    """
    Класс преобразования форм даты в модель pydantic при изменении скидки
    """
    name: Annotated[str, Form(min_length=3)] | None = None
    description: Annotated[str, Form(gt=0, lt=100)] | None = None
    discount: Annotated[float, Form()] | None = None
    start_date: Annotated[datetime, Form()] | None = None
    end_date: Annotated[datetime, Form()] | None = None

    def convert_to_model(self, db_sale: DbCategory) -> SaleUpdate:
        """
        Преобразование в модель pydantic
        :param db_sale: скидка, которую нужно изменить
        :return: модель pydantic
        """
        return SaleUpdate(
            # если какое-то из значений не передано, то берем его из категории, которую нужно изменить
            **{attr: value if value is not None else db_sale.__dict__[attr] for attr, value in self.__dict__.items()}
        )
