from database.connection import async_session_maker
from modules.reservation import models

from modules.reservation.models import *
from database.repository import DatabaseRepository
from unitofwork import AbstractUnitOfWork


class ReservationUnitofWork(AbstractUnitOfWork):

    def __init__(self):
        super().__init__()
        self.session = None

    async def __aenter__(self):
        self.session = self.factory()
        self.tables = DatabaseRepository(models.Table, self.session)
        self.reservations = DatabaseRepository(models.Reservation, self.session)
        
    async def __aexit__(self, *args):
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()