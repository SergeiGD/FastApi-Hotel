import string
import random
from time import time
from fastapi import FastAPI, Request
import uvicorn
from routers import tags, rooms, categories, auth
from hotel_business_module.models.base import Base
from hotel_business_module.session.session import engine
from logger_conf import LOGGING as LOG_CONF
import logging


logging.config.dictConfig(LOG_CONF)
logger = logging.getLogger('requests_logger')

Base.metadata.create_all(engine)
app = FastAPI()


@app.middleware('http')
async def log_requests(request: Request, call_next):
    """
    Миддлвэа для логгирования запросов
    :param request:
    :param call_next:
    :return:
    """
    request_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    start_time = time()
    logger.info(
        f'Начато выполнение запроса {request_id} по адресу {request.url.path}. Метод запроса - {request.method}'
    )
    response = await call_next(request)
    process_time = time() - start_time
    logger.info(
        f'Запрос {request_id} выполнен за {process_time}. Код ответа - {response.status_code}'
    )
    return response

app.include_router(tags.router)
app.include_router(rooms.router)
app.include_router(categories.router)
app.include_router(auth.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
