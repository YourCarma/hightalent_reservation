import sys
from pathlib import Path
from typing import Annotated
from datetime import timedelta

from fastapi.responses import JSONResponse
from fastapi import (APIRouter, Request)

sys.path.append(Path(__file__).parent.__str__())  # pylint: disable=C2801

router = APIRouter(prefix="/reservation", responses={404: {"description": "Not found"}})
