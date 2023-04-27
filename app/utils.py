from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from hotel_business_module.models.base import Base
from fastapi import HTTPException, status, Form
from typing import Annotated
from schemas.categories import Category


def update_model_fields(obj: Base, data: dict):
    """
    Автоматическое обновление полей модели
    :param obj: объект, который нужно обновить
    :param data: словарь значений, которые нужно обновить
    :return:
    """
    for attr, value in data.items():
        setattr(obj, attr, value)


def raise_not_fount(model_name: str):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'{model_name} не найден')


def convert_form_data(data: Annotated[str, Form]):
    try:
        model = Category.parse_raw(data)
    except ValidationError as e:
        raise HTTPException(
            detail=jsonable_encoder(e.errors()),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    return model
