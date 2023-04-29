from pydantic import BaseModel, EmailStr


class BaseUser(BaseModel):
    email: EmailStr


class UserLogin(BaseUser):
    password: str


class UserSingUp(UserLogin):
    first_name: str | None = None
    last_name: str | None = None


class User(BaseUser):
    is_confirmed: bool
