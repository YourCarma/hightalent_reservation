from collections.abc import AsyncGenerator, Callable

from fastapi import Depends
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from loguru import logger

from database import repository
from database.base import Base
from settings import settings

factory_engine = create_async_engine(settings.DB_URL, echo=False)
async_session_maker = async_sessionmaker(factory_engine,
                                         expire_on_commit=False)


async def migrate_tables() -> None:
    logger.info("Starting to migrate")
    engine = create_async_engine(settings.DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Done migrating")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(settings.DB_URL, echo=True)
    factory = async_sessionmaker(engine)
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except exc.SQLAlchemyError as error:
            logger.error(f"Database error occured: {error}")
            await session.rollback()
            raise error
        finally:
            await session.close()


def get_repository(
    model: type[Base],
) -> Callable[[AsyncSession], repository.DatabaseRepository]:

    def func(session: AsyncSession = Depends(get_db_session)):
        return repository.DatabaseRepository(model, session)

    return func
