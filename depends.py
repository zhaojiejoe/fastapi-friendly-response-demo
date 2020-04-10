from collections import namedtuple
from tortoise import QuerySet
from typing import Any
import math
import jwt
from fastapi import Query, Path, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi import Security

from settings import SECERT

security = HTTPBearer()

Page = namedtuple('OrderPage', 'page limit')

async def page_params(page: int = 1, limit: int = 30) -> Page:
    page = page - 1
    if page < 0:
        page = 0
    return Page(page, limit)

async def build_with_order_page(query: QuerySet, page: Page) -> (int, int, int, QuerySet):
    count = await query.count()
    current_page = page.page + 1
    pages = math.ceil(count/page.limit)
    result = query.offset(page.page * page.limit).limit(page.limit)
    return count, current_page, pages, result

async def get_jwt_user(request: Request, token: HTTPAuthorizationCredentials = Security(security)):
    credentials_exception = HTTPException(HTTP_401_UNAUTHORIZED)
    try:
        payload = jwt.decode(token.credentials, SECERT)
        user_id = payload.get('user_id')
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    request.scope['user_id'] = user_id
    return user_id
