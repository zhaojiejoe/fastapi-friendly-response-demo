from typing import Generic, AsyncIterator, Any
from starlette.responses import StreamingResponse, Response
from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from tortoise.models import MODEL
from starlette.status import HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY
import json

def render(data, code=200, msg='') -> dict:
    return {'code': code, 'msg': msg, 'data': data}

def success(data: Any=[]) -> dict:
    return render(data)

async def get_object_or_404(model: Generic[MODEL], **kwargs):
    """
    get_object_or_404
    :param model:
    :param kwargs:
    :return:
    """
    obj = await model.filter(**kwargs).first()  # type:model
    if not obj:
        raise HTTPException(HTTP_404_NOT_FOUND, 'Not Found')
    return obj

async def read_bytes(generator: AsyncIterator[bytes]) -> bytes:
    body = b""
    async for data in generator:
        body += data
    return body

async def resolve_response(streaming: StreamingResponse) -> Response:
    content = await read_bytes(streaming.body_iterator)
    content = json.loads(content)
    if streaming.status_code == HTTP_422_UNPROCESSABLE_ENTITY:
        msg = {i["loc"][-1]: i["msg"] for i in content["detail"]}
        content = render(data=[], msg=msg, code=400)
    else:
        content = render(data=[], msg=content["detail"], code=streaming.status_code)
    content = json.dumps(content).encode()
    status_code = HTTP_200_OK
    headers = dict(streaming.headers) if streaming.headers else None
    if headers is not None:
        headers["content-length"] = str(len(content))
    media_type = "application/json"
    background = streaming.background
    return Response(content, status_code, headers, media_type, background)

async def gen_exception_response(msg: str) -> Response:
    content = render(data=[], msg="Unknow exception", code=4001)
    content = json.dumps(content).encode()
    status_code = HTTP_200_OK
    headers = dict()
    headers["content-length"] = str(len(content))
    headers["content-type"] = 'application/json'
    media_type = "application/json"
    background = None
    return Response(content, status_code, headers, media_type, background)

async def rebuild(response: StreamingResponse) -> Response:
    if response.status_code == HTTP_200_OK:
            return response
    else:
        try:
            return await resolve_response(response)
        except Exception as e:
            return await gen_exception_response(str(e))