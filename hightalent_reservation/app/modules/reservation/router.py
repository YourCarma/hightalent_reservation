import sys
from pathlib import Path

from fastapi.responses import JSONResponse
from fastapi import APIRouter, status

from api.dependencies import UOWReservation
from modules.reservation.service import TableReservationService
from modules.reservation.schemas.payload import Table, Reservation
from utils import validation

sys.path.append(Path(__file__).parent.__str__())  # pylint: disable=C2801

router = APIRouter(prefix="/reservation",
                   responses={404: {
                       "description": "Not found"
                   }})


@router.get("/tables", 
            tags=["Столы"],
            summary="Получение всех столов")
async def get_tables(uow: UOWReservation) -> list[Table]:
    instance = await TableReservationService().get_tables(uow)
    return instance


@router.post("/tables", 
             tags=["Столы"],
             summary="Добавление стола",
             description="""
## Добавление стола.
### Входные данные:
*  **name** `str` - Желаемое имя (Уникальное) стола (Стол №1, Стол №2...)
*  **seats** `int` - Количество посадочных мест
*  **location** `str` - Место расположения стола (У окна, На 2 этаже...)
### Выходные данные:
* Инстанс созданного стола
             """)
async def create_table(table: Table, uow: UOWReservation) -> Table:
    instance = await TableReservationService().add_table(uow, table)
    return JSONResponse(validation(Table, instance),
                        status_code=status.HTTP_201_CREATED)


@router.delete("/tables/{id}", 
               tags=["Столы"],
               summary="Удаление стола по id",
                description="""
## Удаление стола.
### Входные данные:
*  **id** `int` - id удаляемого стола
### Выходные данные:
* **200 OK** - стол успешно удален
* **400 BAD_REQUEST** - заданного стола не существует
             """)
async def delete_table(id: int, uow: UOWReservation) -> JSONResponse:
    await TableReservationService().delete_table(uow, id)
    return JSONResponse("Стол успешно удален!", status_code=status.HTTP_200_OK)


@router.get("/reservations", 
            tags=["Брони"],
            summary="Получение всех активных броней")
async def get_reservations(uow: UOWReservation) -> list[Reservation]:
    instance = await TableReservationService().get_reservations(uow)
    return instance


@router.post("/reservations", 
             tags=["Брони"],
             summary="Добавление брони стола")
async def create_reservation(reservation: Reservation,
                             uow: UOWReservation) -> Reservation:
    instance = await TableReservationService().add_reservation(
        uow, reservation)
    return instance


@router.delete("/reservations/{id}", 
               tags=["Брони"],
               summary="Удаление брони по id")
async def delete_table(id: int, uow: UOWReservation) -> JSONResponse:
    await TableReservationService().delete_reservation(uow, id)
    return JSONResponse("Бронь успешно удалена!",
                        status_code=status.HTTP_200_OK)
