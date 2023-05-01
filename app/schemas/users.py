from pydantic import BaseModel, EmailStr, Field


class BaseUser(BaseModel):
    email: EmailStr


class UserLogin(BaseUser):
    password: str = Field(example='pasdwqes21sd')


class UserSingUp(UserLogin):
    first_name: str | None = None
    last_name: str | None = None


class User(BaseUser):
    is_confirmed: bool
