from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy import and_, or_, func
from sqlalchemy.orm.exc import NoResultFound
from datetime import timedelta

from unitofwork import AbstractUnitOfWork
from modules.reservation.schemas import payload
from api.dependencies import UOWReservation


class TableReservationService:
    
    async def get_tables(self, uow: AbstractUnitOfWork):
        logger.info(
            "\n\tПолучение списка столов"
            )
        async with uow:
            try:
                tables = await uow.tables.get_all()
                logger.success(
                    "\n\tСтолы: \n"
                    f"\t {tables}"
                    )
            except Exception as e:
                logger.error(f"Ошибка в получении списка столов: {e}")
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Ошибка в получении списка столов")
            return tables
    
    async def add_table(self, uow: AbstractUnitOfWork, table_data: payload.Table):
        data = table_data.model_dump(exclude={'id'})
        logger.info(
            f"\n\tСоздание стола:"
            f"{data}"
        )
        name = data.get("name")
        async with uow:
            try:
                table = await uow.tables.get_by_name_or_create(
                    name,
                    {
                        **data
                    }
                    )
                await uow.commit()
                logger.success(f"Стол '{data.get("name")}' успешно создан!")
            except ValueError as e:
                await uow.rollback()
                logger.error(f"Стол {data.get("name")} уже существует!")
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Стол '{data.get("name")}' уже существует!")
            except Exception as e:
                await uow.rollback()
                logger.error(f"Ошибка при создании стола: {str(e)}")
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Ошибка при валидации данных")
            return table
        
    async def delete_table(self, uow: AbstractUnitOfWork, table_id: int):
        async with uow:
            try:
                await uow.tables.delete(uow.tables.model.id == table_id)
                await uow.commit()
            except NoResultFound as e:
                await uow.rollback()
                logger.error(f"Стола с id '{table_id}' не существует!")
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Стола с id '{table_id}' не существует!")
            except Exception as e:
                await uow.rollback()
                logger.error(
                    f"Ошибка при удалении стола: {e}"
                    )
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Ошибка при удалении стола")
            
    async def get_reservations(self, uow: AbstractUnitOfWork):
        logger.info(
            "\n\tПолучение списка броней"
            )
        async with uow:
            try:
                tables = await uow.reservations.get_all()
                logger.success(
                    "\n\tБрони: \n"
                    f"\t {tables}"
                    )
            except Exception as e:
                logger.error(f"Ошибка в получении списка брони: {e}")
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Ошибка в получении списка брони")
            return tables
        
    async def add_reservation(self, uow: AbstractUnitOfWork, reservation_data: payload.Reservation):
        data = reservation_data.model_dump(exclude={'id'})
        table_id = data.get("table_id")
        reservation_time_start = data.get("reservation_time")
        reservation_time_end = reservation_time_start + timedelta(minutes=data.get("duration_minutes"))
        logger.info(
            f"\n\tСоздание брони:"
            f"{data}"
        )
        async with uow:
            try: 
                target_table_in_reservations = await uow.tables.filter(table_id == uow.tables.model.id)
                if not target_table_in_reservations:
                    raise NoResultFound()
                expression = and_(table_id == uow.reservations.model.table_id,
                    or_(
                                      and_(
                                          uow.reservations.model.reservation_time >= reservation_time_start,
                                          uow.reservations.model.reservation_time < reservation_time_end
                                  ),
                                      and_(
                                          uow.reservations.model.reservation_time + func.make_interval(0, 
                                                                                                       0, 
                                                                                                       0, 
                                                                                                       0, 
                                                                                                       0, 
                                                                                                       uow.reservations.model.duration_minutes) > reservation_time_start,
                                          uow.reservations.model.reservation_time + func.make_interval(0, 
                                                                                                       0, 
                                                                                                       0, 
                                                                                                       0,
                                                                                                       0, 
                                                                                                       uow.reservations.model.duration_minutes) <= reservation_time_end
                                      ),
                                      and_(
                                          uow.reservations.model.reservation_time <= reservation_time_start,
                                          uow.reservations.model.reservation_time + func.make_interval(0, 0, 0, 0, 0, uow.reservations.model.duration_minutes) >= reservation_time_end
                                      )
                                )
                )
                                  
                reservations = await uow.reservations.filter(expression)
                if reservations:
                    raise ValueError()
                created_reservation = await uow.reservations.create(
                    {
                        **data
                    }
                    )
                await uow.commit()
                return created_reservation
            except ValueError as e:
                await uow.rollback()
                logger.error(
                        f"Бронь для стола '{table_id}' уже занята в это время!")
                raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Бронь для стола '{table_id}' уже занята в это время!") 
            except NoResultFound as e:
                await uow.rollback()
                logger.error(
                    f"Стола с id '{table_id}' не существует")
                raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Стола с id '{table_id}' не существует") 
            except Exception as e:
                await uow.rollback()
                logger.error(f"Ошибка в создании брони: {e}")
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Ошибка в создании брони")
            
    async def delete_reservation(self, uow: AbstractUnitOfWork, reservation_id: int):
        async with uow:
            try:
                await uow.reservations.delete(uow.reservations.model.id == reservation_id)
                await uow.commit()
            except NoResultFound as e:
                await uow.rollback()
                logger.error(f"Брони с id '{reservation_id}' не существует!")
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Брони с id '{reservation_id}' не существует!")
            except Exception as e:
                await uow.rollback()
                logger.error(
                    f"Ошибка при удалении брони: {e}"
                    )
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Ошибка при удалении брони")







