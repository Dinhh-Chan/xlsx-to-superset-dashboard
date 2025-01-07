# app/api/v1/database.py

from fastapi import APIRouter, HTTPException
from app.models.database import DatabaseRequest
from app.utils.auth import get_superset_headers
from app.core.config import settings
from app.utils.logger import get_logger  # Import get_logger từ utils/logger.py
import requests
import logging

router = APIRouter()
logger = get_logger(__name__)  # Sử dụng get_logger thay vì logging.get_logger

@router.post("/create_database")
def create_database(request: DatabaseRequest):
    try:
        logger.info(f"Nhận yêu cầu tạo database: {request.database_name}")
        headers = get_superset_headers()

        # Xây dựng sqlalchemy_uri từ parameters
        sqlalchemy_uri = f"postgresql://{request.parameters.username}:{request.parameters.password}@{request.parameters.host}:{request.parameters.port}/{request.parameters.database}"

        # Xây dựng payload cho Superset API
        database_payload = {
            "database_name": request.database_name,
            "engine": request.engine,
            "configuration_method": request.configuration_method,
            "engine_information": request.engine_information.dict(),
            "driver": request.driver,
            "sqlalchemy_uri_placeholder": request.sqlalchemy_uri_placeholder,
            "extra": request.extra,
            "expose_in_sqllab": request.expose_in_sqllab,
            "parameters": request.parameters.dict(),
            "masked_encrypted_extra": request.masked_encrypted_extra,
            "sqlalchemy_uri": sqlalchemy_uri  # Truyền sqlalchemy_uri được xây dựng
        }
        # Gửi yêu cầu tới Superset API để tạo database
        database_url = f"{settings.SUPERSET_URL}/api/v1/database/"
        database_response = requests.post(database_url, headers=headers, json=database_payload)

        if database_response.status_code != 201:
            logger.error(f"Tạo database thất bại: {database_response.text}")
            raise HTTPException(status_code=database_response.status_code, detail=database_response.text)

        database_id = database_response.json().get("id")
        if not database_id:
            logger.error("Superset không trả về database ID.")
            raise HTTPException(status_code=500, detail="Superset không trả về database ID.")

        logger.info(f"Tạo database thành công với ID: {database_id}")

        return {"message": "Database đã được tạo thành công", "database_id": database_id}

    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("Đã xảy ra lỗi không mong muốn.")
        raise HTTPException(status_code=500, detail=str(e))
