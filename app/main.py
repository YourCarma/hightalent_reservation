import sys
from pathlib import Path

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn

from api.routers import routers as all_routers
from settings import settings

sys.path.append(Path(__file__).parent.__str__())  # pylint: disable=C2801


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Сервис бронирования столиков в ресторане", 
    description="""
# Тестовое задание для Хайталент""", 
    lifespan=lifespan
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

for router in all_routers:
    app.include_router(router)


@app.get("/health", tags=["Проверка состояния сервиса"])
def health():
    return {"status": "OK"}


if __name__ == '__main__':
    uvicorn.run('main:app', host=settings.HOST, port=settings.PORT, reload=True)
