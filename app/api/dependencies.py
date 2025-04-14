from typing import Annotated

from fastapi import Depends

from unitofwork import AbstractUnitOfWork
from modules.reservation.uow import ReservationUnitofWork

UOWAuth = Annotated[AbstractUnitOfWork, Depends(ReservationUnitofWork)]
