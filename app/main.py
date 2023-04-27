from fastapi import FastAPI
from routers import tags, rooms
from hotel_business_module.models.base import Base
from hotel_business_module.session.session import engine


Base.metadata.create_all(engine)
app = FastAPI()

app.include_router(tags.router)
app.include_router(rooms.router)

