from decimal import Decimal
from pydantic import BaseModel
from datetime import datetime


class WorkerBase(BaseModel):
    first_name: str | None
    last_name: str | None
    salary: Decimal


class WorkerCreate(WorkerBase):
    email: str


class WorkerUpdate(WorkerBase):
    pass


class Worker(WorkerBase):
    id: int
    email: str
    date_created: datetime
    is_superuser: bool

    class Config:
        orm_mode = True
