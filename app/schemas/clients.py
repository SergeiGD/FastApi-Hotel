from pydantic import BaseModel
from datetime import date, datetime


class ClientBase(BaseModel):
    first_name: str | None
    last_name: str | None
    date_of_birth: date | None


class ClientCreate(ClientBase):
    email: str


class ClientUpdate(ClientBase):
    pass


class Client(ClientBase):
    id: int
    email: str
    is_confirmed: bool
    date_created: datetime

    class Config:
        orm_mode = True
