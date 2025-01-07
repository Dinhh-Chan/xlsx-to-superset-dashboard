from fastapi import APIRouter
from .v1 import api_router as v1_api_router

api_router = APIRouter()
api_router.include_router(v1_api_router, prefix="/v1")
