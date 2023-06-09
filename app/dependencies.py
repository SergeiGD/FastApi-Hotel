from hotel_business_module.session.session import get_session
from hotel_business_module.gateways.users_gateway import UsersGateway
from fastapi import HTTPException, status, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials
from utils import HTTPBearer401
from hotel_business_module.settings import settings
from typing import Annotated
from sqlalchemy.orm import Session
from schemas.users import User
import jwt


def get_db():
    """
    Зависимость для получения сессии sqlalchemy
    :return:
    """
    db = get_session()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
        db: Annotated[Session, Depends(get_db)],
        credentials: Annotated[HTTPAuthorizationCredentials, Security(HTTPBearer401())],
):
    """
    Зависимость для получения текущего пользователя с помощью Bearer токена
    :param db:
    :param credentials:
    :return:
    """
    token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Данные для входа не предоставлены или имеют неверную форму'
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except (jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError):
        raise token_exception

    # TODO: заменить на scopes
    if payload['is_refresh_token']:
        raise token_exception

    # TODO: заменить на sub
    current_user = UsersGateway.get_by_id(payload['id'], db)
    if current_user is None:
        raise token_exception

    return current_user


class PermissionsDependency:
    """
    Зависимость для проверки прав пользователя
    """
    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions

    def __call__(
            self,
            db: Annotated[Session, Depends(get_db)],
            current_user: Annotated[User, Depends(get_current_user)],
    ):
        if not UsersGateway.can_actions(user=current_user, db=db, codes=self.required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Недостаточно прав для совершения операции'
            )
        return True
