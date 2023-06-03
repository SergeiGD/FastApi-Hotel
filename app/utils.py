from hotel_business_module.models.base import Base
from fastapi import HTTPException, status


def update_model_fields(obj: Base, data: dict):
    """
    Автоматическое обновление полей модели
    :param obj: объект, который нужно обновить
    :param data: словарь значений, которые нужно обновить
    :return:
    """
    for attr, value in data.items():
        if value is not None:
            setattr(obj, attr, value)


def raise_not_fount(model_name: str):
    """
    Генерация ошибки 404
    :param model_name: наименование модели
    :return:
    """
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'{model_name} не найден')
