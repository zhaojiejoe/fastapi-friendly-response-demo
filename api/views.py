from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel, Schema
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from tortoise.models import MODEL
from typing import Any, TypeVar, ClassVar, Generic, NewType
from tortoise import QuerySet
import jwt

from api.serializers import (Auth_User, UserListPydantic, UserCreatePydantic, 
                            UserRetrievePydantic, GroupPydantic, Auth_Group, LoginInPydantic)
from depends import page_params, Page, build_with_order_page, get_jwt_user
from response import Response
from settings import SECERT
from utils import get_object_or_404, success

from uuid import UUID

router = InferringRouter()

T = TypeVar('T')
UserID = NewType("UserID", UUID)

@cbv(router)
class AbstractCBV(object):
    #page: Page = Depends(page_params)
    model_class: ClassVar[T] = None
    pydantic_list_class: ClassVar[T] = None
    pydantic_retrieve_class: ClassVar[T] = None
    pydantic_create_class: ClassVar[T] = None
    pydantic_update_class: ClassVar[T] = None
    url_list: ClassVar[str] = "/"
    url_retrieve: ClassVar[str] = "/{pk}"
    user_id: UserID = Depends(get_jwt_user)

    def get_queryset(self) -> QuerySet:
        return self.model_class.all()

    async def get_object(self, pk) -> QuerySet:
        return await get_object_or_404(self.model_class, id=pk)

    async def list(self, page: Page = Depends(page_params)) -> dict:
        count, current_page, pages, result = await build_with_order_page(self.get_queryset(), page)
        result = await self.pydantic_list_class.from_queryset(result)
        return success({"count": count, "current_page": current_page, "pages": pages, "result": result})

    async def retrieve(self, pk: int) -> dict:
        obj = await self.get_object(pk)
        result = await self.pydantic_list_class.from_tortoise_orm(obj)
        return success(result)

    async def create(self, obj: Generic[MODEL]) -> dict:
        obj = await self.model_class.create(**obj.dict(exclude_unset=True))
        result = await self.pydantic_retrieve_class.from_tortoise_orm(obj)
        return success(result)

    async def destroy(self, pk: int) -> dict:
        deleted_count = await self.get_object(pk).delete()
        if not deleted_count:
            print("404")
        return success()

    async def update(self, pk: int, obj: Generic[MODEL]) -> dict:
        print(obj)
        await self.model_class.filter(id=pk).update(**obj.dict(exclude_unset=True))
        result = await self.pydantic_retrieve_class.from_queryset_single(self.get_object(pk))
        return success(result)


@cbv(router)
class UsersCBV(AbstractCBV):
    model_class = Auth_User
    pydantic_list_class = UserListPydantic
    pydantic_retrieve_class = UserRetrievePydantic
    pydantic_create_class = UserCreatePydantic
    url_list = "/users"
    url_retrive = "users/{pk}"

    @router.get(url_list, response_model=Response, summary='获取所有users',)
    async def list(self, page: Page = Depends(page_params)) -> dict:
        return await super(UsersCBV, self).list(page)

    @router.get(url_retrive, response_model=Response, summary='获取单个user',)
    async def retrieve(self, pk: int) -> dict:
        return await super(UsersCBV, self).retrieve(pk)

    @router.post(url_list, response_model=Response, summary='新建单个user',)
    async def create(self, obj: UserCreatePydantic) -> dict:
        return await super(UsersCBV, self).create(obj)

    @router.delete(url_retrive, response_model=Response, summary='删除单个user',)
    async def destroy(self, pk: int) -> dict:
        return await super(UsersCBV, self).destroy(pk)

    @router.patch(url_retrive, response_model=Response, summary='修改单个user',)
    @router.put(url_retrive, response_model=Response, summary='修改单个user',)
    async def update(self, pk: int, obj: UserCreatePydantic) -> dict:
        return await super(UsersCBV, self).update(pk, obj)


@cbv(router)
class Group2CBV(AbstractCBV):
    model_class = Auth_Group
    pydantic_list_class = GroupPydantic
    url_list = "/groups"

    @router.get(url_list, response_model=Response, summary='获取所有groups', )
    async def list(self, page: Page = Depends(page_params)) -> dict:
        return await super(Group2CBV, self).list(page)


@router.post('/login', response_model=Response, summary='登录',)
async def login(
        login_form: LoginInPydantic
):
    user = await get_object_or_404(Auth_User, username=login_form.username)
    # todo 这里需要验证密码相关
    return success({
        'user': {
            'username': user.username
        },
        'token': jwt.encode({'user_id': user.pk}, SECERT)
    })