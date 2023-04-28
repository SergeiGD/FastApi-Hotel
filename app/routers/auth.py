from fastapi import APIRouter, Depends, Body, HTTPException, status
from typing import Annotated
from dependencies import get_db
from sqlalchemy.orm import Session
from hotel_business_module.gateways.users_gateway import UsersGateway
from schemas.jwt_tokens import JWTToken

router = APIRouter(
    prefix='/auth',
    tags=['auth', ]
)


@router.post('/login', response_model=JWTToken)
def login(
        user_login: Annotated[str, Body(embed=True)],
        user_password: Annotated[str, Body(embed=True)],
        db: Annotated[Session, Depends(get_db)]
):
    try:
        user = UsersGateway.authenticate_user(user_login, user_password, db)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err))

    access_token, refresh_token = UsersGateway.generate_auth_tokens(user.id)
    return JWTToken(access_token=access_token, refresh_token=refresh_token)
