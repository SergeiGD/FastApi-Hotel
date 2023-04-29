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
from hotel_business_module.utils.email_sender import send_email
from schemas.jwt_tokens import JWTToken
from schemas.users import UserLogin, UserSingUp

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
    :param user:
    :param db:
    :return:
    """
    try:
        user = UsersGateway.authenticate_user(user.email, user.password, db)
    except ValueError as err:
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
    :param token:
    :param db:
    :return:
    """
    try:
        access_token, refresh_token = UsersGateway.refresh_auth_tokens(token, db)
    except ValueError as err:
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
    :param email:
    :param background_tasks:
    :param db:
    :return:
    """
    try:
        user, token = UsersGateway.request_reset(email, db)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    confirm_link = f'{settings.SITE_URL}{router.url_path_for("reset_password", token=token)}'
    email_content = f'Для сброса пароля перейдите по следующей ссылке: \n {confirm_link}'
    email_subject = 'Сброс пароля'
    # добавляем отпарвку письма в бэкграунд задачи
    background_tasks.add_task(send_email, send_to=user.email, subject=email_subject, content=email_content)
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
    :param token:
    :param password:
    :param db:
    :return:
    """
    reset_token = UsersGateway.check_token(token=token, token_type=TokenType.reset, db=db)
    if reset_token is None:
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
    :param user:
    :param background_tasks:
    :param db:
    :return:
    """
    try:
        db_client = DbClient(**user.dict())
        user, token = UsersGateway.register_user(db_client, db)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    confirm_link = f'{settings.SITE_URL}{router.url_path_for("confirm_sign_up", token=token)}'
    email_content = f'Для подтверждения регистрации перейдите по следующей ссылке: \n {confirm_link}'
    email_subject = 'Подтверждение регистрации'
    # добавляем отпарвку письма в бэкграунд задачи
    background_tasks.add_task(send_email, send_to=user.email, subject=email_subject, content=email_content)
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
    :param token:
    :param db:
    :return:
    """
    sing_up_token = UsersGateway.check_token(token=token, token_type=TokenType.register, db=db)
    if sing_up_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Ошибка подтврждения. Проверьте ссылку')

    UsersGateway.confirm_account(token=sing_up_token, db=db)
    response = jsonable_encoder({'msg': 'Регистрация завершена'})
    return JSONResponse(content=response)
