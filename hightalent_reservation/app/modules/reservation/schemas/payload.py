from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

class Table(BaseModel):
    id: Optional[int] = Field(
        default= None, description="ID стола", examples=[1, 2]
    )
    name: str = Field(
        description="Имя стола", examples=["Стол №1", "Стол №2"]
    )
    seats: int = Field(
        description="Количество мест за столом", ge=1, examples=[1, 2]
    )
    location: str = Field(
        description="Расположение стола", examples=["У главного входа", "У окна"]
    )
    

class Reservation(BaseModel):
    id: Optional[int] = Field(
        default= None, description="ID брони", examples=[1, 2]
    )
    customer_name: str = Field(
        description="Заказчик", examples=["Игорь", "Дон Симон", "Влад Поздняков"]
    )
    reservation_time: Optional[datetime] = Field(
        default=datetime.now(), description="Время начала бронирования"
    )
    duration_minutes: Optional[int] = Field(
        default=30, description="Продолжительность бронирования, мин"
    )
    table_id: int = Field(
        description="ID бронируемого стола"
    )