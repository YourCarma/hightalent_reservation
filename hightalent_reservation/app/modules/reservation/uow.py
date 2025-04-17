from database.connection import async_session_maker
from modules.reservation import models
from loguru import logger
from sqlalchemy import func
from fastapi import HTTPException, status
from sqlalchemy.exc import OperationalError

from modules.reservation.models import *
from database.repository import DatabaseRepository
from unitofwork import AbstractUnitOfWork
from exceptions import ServiceUnavailable
from settings import settings


class ReservationUnitofWork(AbstractUnitOfWork):

    def __init__(self):
        super().__init__()
        self.session = None

    async def __aenter__(self):
        try:
            self.session = self.factory()
            self.tables = DatabaseRepository(models.Table, self.session)
            self.reservations = DatabaseRepository(models.Reservation, self.session)
            await self.clean_finished_reservations()
        except OperationalError as e:
            logger.error(
                "Ошибка подключения к СУБД!"
                f"Проверьте подключение по адресу: {settings.DB_URL}"
                )
            raise ServiceUnavailable(
                "База данных"
            )
        
    async def __aexit__(self, *args):
        await self.session.close()

    async def clean_finished_reservations(self):
        logger.info("Проверка истекших броней")
        try:
            finished_reservations = await self.reservations.filter(
                self.reservations.model.reservation_time + func.make_interval(0, 
                                                                            0, 
                                                                            0, 
                                                                            0, 
                                                                            0, 
                                                                            self.reservations.model.duration_minutes) < datetime.now()
            )
            if finished_reservations:
                [await self.reservations.delete_instance(reservation) for reservation in finished_reservations]
                await self.commit()
                logger.success("Истекшие записи удалены!")
                return
            logger.warning(
                "Истекшие записи отсутсвуют!"
            )
            return
        except Exception as e:
            await self.rollback()
            logger.error(f"Ошибка при проверки активных броней!: {str(e)}")
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Ошибка при проверки активных броней!")
            
    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()