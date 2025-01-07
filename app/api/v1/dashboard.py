# app/api/v1/dashboard.py

from fastapi import APIRouter, HTTPException
from app.utils.auth import get_superset_headers
from app.core.config import settings
from app.utils.logger import get_logger  # Import get_logger từ utils/logger.py
import requests
import logging

router = APIRouter()
logger = get_logger(__name__)  # Sử dụng get_logger thay vì logging.get_logger

@router.post("/create_dashboard")
def create_dashboard(dashboard_name: str):
    try:
        logger.info(f"Nhận yêu cầu tạo dashboard: {dashboard_name}")
        headers = get_superset_headers()
        dashboard_payload = {
            "dashboard_title": dashboard_name
        }

        dashboard_url = f"{settings.SUPERSET_URL}/api/v1/dashboard/"
        dashboard_response = requests.post(dashboard_url, headers=headers, json=dashboard_payload)

        if dashboard_response.status_code != 201:
            logger.error(f"Tạo dashboard thất bại: {dashboard_response.text}")
            raise HTTPException(status_code=dashboard_response.status_code, detail=dashboard_response.text)

        dashboard_id = dashboard_response.json()["id"]
        logger.info(f"Tạo dashboard thành công với ID: {dashboard_id}")

        return {"message": "Dashboard đã được tạo thành công", "dashboard_id": dashboard_id}

    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("Đã xảy ra lỗi không mong muốn.")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/publish_dashboard")
def publish_dashboard(dashboard_id: int):
    try:
        logger.info(f"Nhận yêu cầu xuất bản dashboard ID: {dashboard_id}")
        headers = get_superset_headers()
        publish_url = f"{settings.SUPERSET_URL}/api/v1/dashboard/{dashboard_id}/publish"
        publish_response = requests.post(publish_url, headers=headers)
        if publish_response.status_code != 200:
            logger.error(f"Xuất bản dashboard thất bại: {publish_response.text}")
            raise HTTPException(status_code=publish_response.status_code, detail=publish_response.text)
        logger.info(f"Xuất bản dashboard ID {dashboard_id} thành công.")
        return {"message": "Dashboard đã được xuất bản thành công"}

    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("Đã xảy ra lỗi không mong muốn.")
        raise HTTPException(status_code=500, detail=str(e))
