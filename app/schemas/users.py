from pydantic import BaseModel


class BaseUser(BaseModel):
    email: str
    first_name: str | None = None
    last_name: str | None = None


class UserLogin(BaseUser):
    password: str


class User(BaseUser):
    is_confirmed: bool
