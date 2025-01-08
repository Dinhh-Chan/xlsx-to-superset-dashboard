# app/api/v1/chart.py

from fastapi import APIRouter, HTTPException
from app.models.chart import ChartRequest
from app.utils.auth import get_superset_headers
from app.core.config import settings
from app.utils.logger import get_logger  # Import get_logger
import requests
import logging

router = APIRouter()
logger = get_logger(__name__)  # Sử dụng get_logger

@router.post("/create_chart_pie")
def create_chart(request: ChartRequest):
    try:
        logger.info(f"Nhận yêu cầu tạo biểu đồ: {request.slice_name}")
        headers = get_superset_headers()

        # Kiểm tra datasource tồn tại
        datasource_url = f"{settings.SUPERSET_URL}/api/v1/dataset/{request.datasource_id}"
        datasource_response = requests.get(datasource_url, headers=headers)
        if datasource_response.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Datasource với ID {request.datasource_id} không tồn tại.")

        # Kiểm tra dashboards tồn tại
        for dashboard_id in request.dashboards:
            dashboard_url = f"{settings.SUPERSET_URL}/api/v1/dashboard/{dashboard_id}"
            dashboard_response = requests.get(dashboard_url, headers=headers)
            if dashboard_response.status_code != 200:
                raise HTTPException(status_code=404, detail=f"Dashboard với ID {dashboard_id} không tồn tại.")

        # Xây dựng payload cho Superset API
        chart_payload = {
            "slice_name": request.slice_name,
            "viz_type": request.viz_type,
            "datasource_id": request.datasource_id,
            "datasource_type": request.datasource_type,
            "params": request.params  # Truyền trực tiếp chuỗi JSON
        }

        # Gửi yêu cầu tới Superset API để tạo biểu đồ
        chart_url = f"{settings.SUPERSET_URL}/api/v1/chart/"
        chart_response = requests.post(chart_url, headers=headers, json=chart_payload)

        if chart_response.status_code != 201:
            logger.error(f"Tạo biểu đồ thất bại: {chart_response.text}")
            raise HTTPException(status_code=chart_response.status_code, detail=chart_response.text)

        chart_id = chart_response.json().get("id")
        if not chart_id:
            logger.error("Superset không trả về chart ID.")
            raise HTTPException(status_code=500, detail="Superset không trả về chart ID.")

        logger.info(f"Tạo biểu đồ thành công với ID: {chart_id}")

        return {"message": "Biểu đồ đã được tạo thành công", "chart_id": chart_id}

    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("Đã xảy ra lỗi không mong muốn.")
        raise HTTPException(status_code=500, detail=str(e))
