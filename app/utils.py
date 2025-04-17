from typing import List, Any, Union, Annotated

from loguru import logger
from pydantic import BaseModel


def validation(
        validation_model: BaseModel,
        instance_object: Union[List, Any, None]) -> Union[List[dict], dict]:
    """
    Функция для валидации объектов по заданной pydantic-схеме
    """
    try:
        if isinstance(instance_object, list):
            return [
                validation_model.model_validate(
                    instance, from_attributes=True).model_dump()
                for instance in instance_object
            ]
        elif instance_object is None:
            return {"detail": "no data provided due to status code"}
        else:
            return validation_model.model_validate(
                instance_object, from_attributes=True).model_dump()
    except Exception as e:
        logger.error(f"Validation error occured, {e}")
        return {"detail": "error occured"}
