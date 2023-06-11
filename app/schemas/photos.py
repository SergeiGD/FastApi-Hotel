from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from fastapi import Form
from .categories import Category
from dataclasses import dataclass
from hotel_business_module.models.photos import Photo as DbPhoto


class PhotoCreate(BaseModel):
    category_id: int


class PhotoUpdate(BaseModel):
    order: int = Field(gt=0)


class Photo(BaseModel):
    id: int
    category: Category
    order: int
    path: str

    class Config:
        orm_mode = True


@dataclass
class PhotosCreateForm:
    """
    Класс преобразования форм даты в модель pydantic при создании фотографии
    """
    category_id: Annotated[int, Form()]

    def convert_to_model(self) -> PhotoCreate:
        """
        Преобразование в модель pydantic
        :return: модель pydantic
        """
        return PhotoCreate(**jsonable_encoder(self))


@dataclass
class PhotosUpdateForm:
    """
    Класс преобразования форм даты в модель pydantic при изменении фотографии
    """
    order: int | None = Form(gt=0, default=None)

    def convert_to_model(self, db_photo: DbPhoto) -> PhotoUpdate:
        """
        Преобразование в модель pydantic
        :param db_photo: фотография, которую нужно изменить
        :return: модель pydantic
        """
        return PhotoUpdate(
            # если какое-то из значений не передано, то берем его из категории, которую нужно изменить
            **{attr: value if value is not None else db_photo.__dict__[attr] for attr, value in self.__dict__.items()}
        )
