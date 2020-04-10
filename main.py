from fastapi import FastAPI, Request
import api
import uvicorn
from tortoise.contrib.fastapi import register_tortoise

from utils import rebuild

app = FastAPI()


app.include_router(api.router, prefix='/v1')



register_tortoise(app,
        db_url='sqlite://db.sqlite3',
        modules={'models': ['api.models']})



@app.middleware("http")
async def rebuild_response(request: Request, call_next):
    response = await call_next(request)
    response = await rebuild(response)
    return response

if __name__ == "__main__":
    uvicorn.run(app="main:app", host='0.0.0.0', port=8888, reload=True)


