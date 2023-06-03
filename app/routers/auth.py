from fastapi import APIRouter, Depends, Body, HTTPException, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated
from dependencies import get_db
from sqlalchemy.orm import Session
from hotel_business_module.gateways.users_gateway import UsersGateway
from hotel_business_module.models.tokens import TokenType
from hotel_business_module.models.users import Client as DbClient
from hotel_business_module.settings import settings
from tasks import send_email_to_user
from schemas.jwt_tokens import JWTToken
from schemas.users import UserLogin, UserSingUp
import logging
from logger_conf import LOGGING as LOG_CONF


logging.config.dictConfig(LOG_CONF)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/auth',
    tags=['auth', ]
)


@router.post('/login', response_model=JWTToken)
def login(
        user: UserLogin,
        db: Annotated[Session, Depends(get_db)]
):
    """
    Аутентификация
    - **email**: адрес эл. почты
    - **password**: пароль
    \f
    :param user:
    :param db:
    :return:
    """
    try:
        logger.info(f'Попытка аутентификации пользователя {user.email[0:4]}***')
        user = UsersGateway.authenticate_user(user.email, user.password, db)
    except ValueError as err:
        logger.warning(f'Ошибка при аутентификации пользователя {user.email[0:4]}***')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err))

    access_token, refresh_token = UsersGateway.generate_auth_tokens(user.id)
    return JWTToken(access_token=access_token, refresh_token=refresh_token)


@router.post('/refresh_user_token', response_model=JWTToken)
def refresh_user_token(
        token: Annotated[str, Body(embed=True)],
        db: Annotated[Session, Depends(get_db)]
):
    """
    Обноваление JWT токена
    - **token**: токен обновления
    \f
    :param token:
    :param db:
    :return:
    """
    try:
        logger.info('Попытка обновления токена доступа')
        access_token, refresh_token = UsersGateway.refresh_auth_tokens(token, db)
    except ValueError as err:
        logger.warning('Ошибка обновления токена доступа')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err))

    return JWTToken(access_token=access_token, refresh_token=refresh_token)


@router.post('/request_reset')
def request_reset(
        email: Annotated[str, Body(embed=True)],
        background_tasks: BackgroundTasks,
        db: Annotated[Session, Depends(get_db)],
):
    """
    Запрос смены пароля
    - **email**: адрес эл. почты
    \f
    :param email:
    :param background_tasks:
    :param db:
    :return:
    """
    try:
        logger.info(f'Запрос сброса пароля пользователя {email[0:4]}***')
        user, token = UsersGateway.request_reset(email, db)
    except ValueError as err:
        logger.warning(f'Ошибка при запросе сброса пароля пользователя {email[0:4]}***')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    confirm_link = f'{settings.SITE_URL}{router.url_path_for("reset_password", token=token)}'
    email_content = f'Для сброса пароля перейдите по следующей ссылке: \n {confirm_link}'
    email_subject = 'Сброс пароля'
    # добавляем отпарвку письма в бэкграунд задачи
    background_tasks.add_task(send_email_to_user, send_to=user.email, subject=email_subject, content=email_content)
    logger.debug(f'Отправка письма для сброса пароля пользователя пользователя {email[0:4]}*** поставлена в список задач')
    # для удобства вернем линк в ответе
    response = jsonable_encoder({'confirm_link': confirm_link})
    return JSONResponse(content=response)


@router.post('/reset_password/{token}')
def reset_password(
        token: str,
        password: Annotated[str, Body(embed=True)],
        db: Annotated[Session, Depends(get_db)],
):
    """
    Подтверждение смены пароля
    - **token**: токен подтверждения сброса пароля
    - **password**: новый пароль
    \f
    :param token:
    :param password:
    :param db:
    :return:
    """
    logger.info('Попытка подтверждения сброса пароля')
    reset_token = UsersGateway.check_token(token=token, token_type=TokenType.reset, db=db)
    if reset_token is None:
        logger.warning('Ошибка при подтверждении сброса пароля')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Ошибка подтврждения. Проверьте ссылку')

    UsersGateway.confirm_reset(token=reset_token, password=password, db=db)
    response = jsonable_encoder({'msg': 'Пароль успешно изменен'})
    return JSONResponse(content=response)


@router.post('/sign_up')
def sign_up(
        user: UserSingUp,
        background_tasks: BackgroundTasks,
        db: Annotated[Session, Depends(get_db)],
):
    """
    Регистрация
    - **email**: адрес эл. почты
    - **password**: пароль
    - **first_name**: имя (опционально)
    - **last_name**: фамилия (опционально)
    \f
    :param user:
    :param background_tasks:
    :param db:
    :return:
    """
    try:
        logger.info(f'Попытка регистрации пользователя {user.email[0:4]}***')
        db_client = DbClient(**user.dict())
        user, token = UsersGateway.register_user(db_client, db)
    except ValueError as err:
        logger.debug(f'Ошибка при попытке регистрации пользователя {user.email[0:4]}***')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    confirm_link = f'{settings.SITE_URL}{router.url_path_for("confirm_sign_up", token=token)}'
    email_content = f'Для подтверждения регистрации перейдите по следующей ссылке: \n {confirm_link}'
    email_subject = 'Подтверждение регистрации'
    # добавляем отпарвку письма в бэкграунд задачи
    background_tasks.add_task(send_email_to_user, send_to=user.email, subject=email_subject, content=email_content)
    logger.info(
        f'Отправка письма для подтвеждения регистрации пользователя {user.email[0:4]}*** поставлена в список задач'
    )
    # для удобства вернем линк в ответе
    response = jsonable_encoder({'confirm_link': confirm_link})
    return JSONResponse(content=response)


@router.post('/confirm_sign_up/{token}')
def confirm_sign_up(
        token: str,
        db: Annotated[Session, Depends(get_db)],
):
    """
    Подтверждение регистрации
    - **token**: токен подтверждения регистрации
    \f
    :param token:
    :param db:
    :return:
    """
    logger.info('Попытка подтверждения регистрации')
    sing_up_token = UsersGateway.check_token(token=token, token_type=TokenType.register, db=db)
    if sing_up_token is None:
        logger.warning('Ошибка при попытке подтверждения регистрации')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Ошибка подтврждения. Проверьте ссылку')

    UsersGateway.confirm_account(token=sing_up_token, db=db)
    response = jsonable_encoder({'msg': 'Регистрация завершена'})
    return JSONResponse(content=response)
