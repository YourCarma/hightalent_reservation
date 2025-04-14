
from itertools import chain
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Security, status, Request
from loguru import logger
from pydantic import ValidationError

from settings import settings
from unitofwork import AbstractUnitOfWork
from api.dependencies import UOWAuth



class UserManagerService:
    async def add_user(self, uow: AbstractUnitOfWork, user_data: payload.CreateUser):
        data = user_data.model_dump(exclude={'id'})
        async with uow:
            try:
                user_info = data.pop("roles")
                roles = await uow.roles.get_by_id_or_none_list(user_info)
                roles = list(filter(lambda x: x is not None, roles))
                user = await uow.users.create(
                    {
                        **data,
                        "roles": roles
                    }
                    )
                await uow.commit()
                logger.success(f"Пользователь '{data.get("username")}' успешно создан!")
            except Exception as e:
                await uow.rollback()
                logger.error(f"Ошибка при создании пользователя: {str(e)}")
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Ошибка при валидации данных")
            return user








