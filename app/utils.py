from typing import Optional

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
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
        setattr(obj, attr, value)


def raise_not_fount(model_name: str):
    """
    Генерация ошибки 404
    :param model_name: наименование модели
    :return:
    """
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'{model_name} не найден')


class HTTPBearer401(HTTPBearer):
    """
    Переопределенная зависимость HTTPBearer, что возврата 401 вместо 403
    """
    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.headers.get('Authorization')
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, detail='Не предоставлены данные аутентификации'
                )
            else:
                return None
        if scheme.lower() != 'bearer':
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail='Неверный формат данных аутентификации',
                )
            else:
                return None
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)
