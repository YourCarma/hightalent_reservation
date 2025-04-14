from abc import ABC, abstractmethod

from database.connection import async_session_maker


class AbstractUnitOfWork(ABC):

    @abstractmethod
    def __init__(self):
        self.factory = async_session_maker

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...