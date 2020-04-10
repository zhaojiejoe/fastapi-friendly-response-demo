from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from fastapi import Body
from pydantic import BaseModel
from api.models import Auth_Group, Auth_User


class LoginInPydantic(BaseModel):
    username: str = Body(..., example='zhaojie')
    password: str = Body(..., example='zhaojie')


UserRetrievePydantic = pydantic_model_creator(Auth_User, name="UserRetrieve", exclude=["password"])
UserCreatePydantic = pydantic_model_creator(Auth_User, name="UserCreate", exclude_readonly=True)
UserListPydantic = pydantic_model_creator(Auth_User, name="UserList", exclude=["password"])

GroupPydantic = pydantic_model_creator(Auth_Group, name="Group")