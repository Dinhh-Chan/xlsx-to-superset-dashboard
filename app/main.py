from fastapi import FastAPI
from app.api import api_router
from app.utils.logger import get_logger

app = FastAPI()

# Include API router
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

# Configure logger
logger = get_logger()

# Optional: Handle startup and shutdown events
@app.on_event("startup")
def on_startup():
    logger.info("Ứng dụng đã khởi động.")

@app.on_event("shutdown")
def on_shutdown():
    logger.info("Ứng dụng đang tắt.")
