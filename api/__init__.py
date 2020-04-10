from fastapi_utils.inferring_router import InferringRouter
from . import views

router = InferringRouter()

router.include_router(views.router, prefix='/api', tags=['api'])
