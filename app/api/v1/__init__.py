from fastapi import APIRouter
from .database import router as database_router
from .chart import router as chart_router
from .dashboard import router as dashboard_router
from .upload import router as upload_router
from .formdata import router as form_data_router
api_router = APIRouter()
api_router.include_router(database_router, prefix="/database", tags=["Database"])
api_router.include_router(chart_router, prefix="/chart", tags=["Chart"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(upload_router, prefix="/upload", tags=["Upload"])
api_router.include_router(form_data_router, prefix="/formdata", tags=["Formdata"])

