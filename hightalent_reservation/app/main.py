import sys
from pathlib import Path
from datetime import datetime

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn

from api.routers import routers as all_routers
from settings import settings

sys.path.append(Path(__file__).parent.__str__())  # pylint: disable=C2801


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Сервис бронирования столиков в ресторане",
              description="""
# Тестовое задание для Хайталент
### Модули сервиса:
* Модуль бронирования столиков `reservation`
* Можно будет вставить *любой* другой модуль под задачу
Взаимодействие с БД производится с применением `паттерна UnitOfWork`, что позволяет гибко настраивать функции под разные задачи.
### Репозитории UnitOfWork:
* Общий репозиторий `/app/database/repository.py`
* Репозиторий управления столиками и бронями `app/modules/reservation/uow.py`
* - На каждый запрос к БД выполняется проверка на прошедшие брони, которые удаляются по завершению их временного промежутка
### Middlware:
На каждый запрос клиента производится логгирование запроса и его ответа
# """,
              lifespan=lifespan)

origins = ["*"]
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

for router in all_routers:
    app.include_router(router)


@app.middleware("http")
async def request_timer(request: Request, call_next):
    start_time = datetime.now()
    logger.debug(f"\n\t[ ]Получен запрос\n"
                 f"\n\tКлиент: {request.client.host}:{request.client.port}\n"
                 f"\tПо адресу: {request.url}\n")
    response = await call_next(request)
    process_time = datetime.now() - start_time

    logger.success(f"\n\t[X]Ответ на запрос\n"
                   f"\n\tКлиент: {request.client.host}:{request.client.port}\n"
                   f"\tПо адресу: {request.url}\n"
                   f"\tВремя выполнения запроса: {process_time}\n"
                   f"\tСтатус ответа: {response.status_code}")
    return response


@app.get("/health", tags=["Проверка состояния сервиса"])
def health():
    return {"status": "OK"}


if __name__ == '__main__':
    uvicorn.run('main:app',
                host=settings.HOST,
                port=settings.PORT,
                reload=True)
