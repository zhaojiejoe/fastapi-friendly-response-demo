from pydantic import BaseModel
from typing import Any


class Response(BaseModel):
    code: int
    msg: str or None = None
    data: Any = []
