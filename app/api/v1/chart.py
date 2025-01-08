# app/api/v1/chart.py

from fastapi import APIRouter, HTTPException, Depends
from app.models.chart import PieChartRequest  # Ensure the path is correct
from app.models.barchat import BarChartRequest 
from app.models.linechart import LineChartRequest 
from app.models.number import NumberChartRequest  # Define this similarly to PieChartRequest
from app.utils.auth import get_superset_headers
from app.core.config import settings
from app.utils.logger import get_logger
import requests
from typing import Dict, Any

router = APIRouter()
logger = get_logger(__name__)

def create_chart(request: PieChartRequest, headers: Dict[str, str]) -> Dict[str, Any]:
    logger.info(f"Received request to create chart: {request.slice_name}")

    # Validate datasource existence
    datasource_url = f"{settings.SUPERSET_URL}/api/v1/dataset/{request.datasource_id}"
    datasource_response = requests.get(datasource_url, headers=headers)
    if datasource_response.status_code != 200:
        error_msg = f"Datasource with ID {request.datasource_id} does not exist."
        logger.error(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)

    # Validate dashboards existence
    for dashboard_id in request.dashboards:
        dashboard_url = f"{settings.SUPERSET_URL}/api/v1/dashboard/{dashboard_id}"
        dashboard_response = requests.get(dashboard_url, headers=headers)
        if dashboard_response.status_code != 200:
            error_msg = f"Dashboard with ID {dashboard_id} does not exist."
            logger.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)

    # Construct payload for Superset API
    chart_payload = {
        "slice_name": request.slice_name,
        "viz_type": request.viz_type,
        "datasource_id": request.datasource_id,
        "datasource_type": request.datasource_type,
        "params": request.params
    }

    logger.debug(f"Payload for Superset API: {chart_payload}")

    # Send request to Superset API to create chart
    chart_url = f"{settings.SUPERSET_URL}/api/v1/chart/"
    chart_response = requests.post(chart_url, headers=headers, json=chart_payload)

    if chart_response.status_code != 201:
        logger.error(f"Failed to create chart: {chart_response.text}")
        raise HTTPException(status_code=chart_response.status_code, detail=chart_response.text)

    chart_id = chart_response.json().get("id")
    if not chart_id:
        logger.error("Superset did not return a chart ID.")
        raise HTTPException(status_code=500, detail="Superset did not return a chart ID.")

    logger.info(f"Chart created successfully with ID: {chart_id}")
    return {"message": "Chart created successfully", "chart_id": chart_id}

# Dependency to fetch headers
def get_headers_dependency():
    return get_superset_headers()

@router.post("/create_chart_pie")
def create_chart_pie(
    request: PieChartRequest, 
    headers: Dict[str, str] = Depends(get_headers_dependency)
):
    try:
        return create_chart(request, headers)
    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("An unexpected error occurred.")
        raise HTTPException(status_code=500, detail=str(e))
@router.post("create_bar_chart")
def create_bar_chart(request: BarChartRequest, headers: Dict[str, str] = Depends(get_headers_dependency)):
    try :
        return create_chart(request, headers)
    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("An unexpected error occurred.")
@router.post("create_line_chart")
def create_bar_chart(request: LineChartRequest, headers: Dict[str, str] = Depends(get_headers_dependency)):
    try :
        return create_chart(request, headers)
    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("An unexpected error occurred.")
@router.post("create_number_chart")
def create_bar_chart(request: NumberChartRequest, headers: Dict[str, str] = Depends(get_headers_dependency)):
    try :
        return create_chart(request, headers)
    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("An unexpected error occurred.")
