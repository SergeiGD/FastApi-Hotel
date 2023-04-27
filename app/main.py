from fastapi import FastAPI
import uvicorn
from routers import tags, rooms, categories
from hotel_business_module.models.base import Base
from hotel_business_module.session.session import engine

# TODO: pydantic первичная валидация
# TODO: async работа с файлами
# TODO: мб patch в категориях вместо put

Base.metadata.create_all(engine)
app = FastAPI()

app.include_router(tags.router)
app.include_router(rooms.router)
app.include_router(categories.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
