from time import time
from fastapi import FastAPI, Request
import uvicorn
from routers import tags, rooms, categories, auth, clients, workers, groups, permissions
from hotel_business_module.models.base import Base
from hotel_business_module.session.session import engine
from logger_conf import LOGGING as LOG_CONF
import logging
import uuid


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
    # генерируем идентификатор запроса
    request_id = uuid.uuid4().hex
    # фиксируем время начала выполнения
    start_time = time()
    # пишем в логи информацию о начале обработки
    logger.info(
        f'Начато выполнение запроса {request_id} по адресу {request.url.path}. Метод запроса - {request.method}'
    )
    # выполнеяем запрос
    response = await call_next(request)
    # высчитываем время выполения
    process_time = time() - start_time
    # пишем в логи информацию о результате обработки
    logger.info(
        f'Запрос {request_id} выполнен за {process_time}. Код ответа - {response.status_code}'
    )
    return response

app.include_router(tags.router)
app.include_router(rooms.router)
app.include_router(categories.router)
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(workers.router)
app.include_router(groups.router)
app.include_router(permissions.router)

if __name__ == "__main__":
    uvicorn.run('main:app', host='0.0.0.0', reload=True)
