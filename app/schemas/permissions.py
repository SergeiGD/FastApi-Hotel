from pydantic import BaseModel


class Permission(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        orm_mode = True
