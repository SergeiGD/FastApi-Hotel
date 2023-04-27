from pydantic import BaseModel, Field
from typing import Annotated


class Item(BaseModel):
    name: str
    description: str | None = None
    # price: float = Field(description='qweasd', default=500)
    # НЕЛЬЗЯ СТАВИТЬ ПАРАМЕТР DEFAULT, КОГДА ДЕЛАЕШЬ ЧЕРЕЗ Annotated
    price: Annotated[float, Field(description='qwe', example=300)] = 800
    tax: float | None = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            },
            "title": "cool title"
        }

