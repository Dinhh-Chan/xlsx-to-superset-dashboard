from fastapi import FastAPI, File, UploadFile, HTTPException
import requests 
import pandas as pd 
import json 
import os 
from dotenv import load_dotenv 
from pydantic import BaseModel, Field, validator
import io 
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tải các biến môi trường từ file .env nếu có
load_dotenv()

app = FastAPI()

# Superset config
SUPERSET_URL = os.getenv("SUPERSET_URL", "http://localhost:8088")
SUPERSET_USERNAME = os.getenv("SUPERSET_USERNAME", "admin")
SUPERSET_PASSWORD = os.getenv("SUPERSET_PASSWORD", "admin")

# PostgreSQL config
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5435")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
POSTGRES_DB = os.getenv("POSTGRES_DB", "superset_test")

# Kết nối DB 
DATABASE_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URI)

# Định nghĩa mô hình Pydantic cho yêu cầu tạo biểu đồ
class ChartRequest(BaseModel):
    cache_timeout: int = Field(..., example=0)
    certification_details: Optional[str] = Field("", example="Chi tiết chứng nhận")
    certified_by: Optional[str] = Field("", example="Người chứng nhận")
    dashboards: List[int] = Field(..., example=[17])
    datasource_id: int = Field(..., example=94)
    datasource_name: str = Field(..., example="data_example")
    datasource_type: str = Field(..., example="table")
    description: Optional[str] = Field("", example="Biểu đồ thể hiện tỷ lệ giới tính của sinh viên.")
    external_url: Optional[str] = Field("", example="http://example.com")
    is_managed_externally: bool = Field(..., example=False)
    owners: List[int] = Field(..., example=[1])
    params: str = Field(..., example="{\"datasource\":\"94__table\",\"viz_type\":\"pie\",\"groupby\":[\"Trạng thái học\"],\"metric\":\"count\",\"adhoc_filters\":[],\"row_limit\":1000,\"sort_by_metric\":true,\"color_scheme\":\"bnbColors\",\"show_labels_threshold\":5,\"show_legend\":true,\"legendType\":\"scroll\",\"legendOrientation\":\"top\",\"label_type\":\"key\",\"show_labels\":true,\"labels_outside\":true,\"outerRadius\":70,\"innerRadius\":30,\"extra_form_data\":{},\"dashboards\":[17]}")
    query_context: Optional[str] = Field("", example="Context info")
    query_context_generation: bool = Field(..., example=False)
    slice_name: str = Field(..., example="Tỷ lệ Giới Tính Sinh Viên")
    viz_type: str = Field(..., example="pie")

    @validator('params')
    def validate_params(cls, v):
        try:
            json.loads(v)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in params: {str(e)}")
        return v

# Hàm đăng nhập vào Superset và lấy token
superset_token = None 

def login_superset():
    global superset_token 
    login_url = f"{SUPERSET_URL}/api/v1/security/login"
    payload = {
        "username": SUPERSET_USERNAME,
        "password": SUPERSET_PASSWORD,
        "provider": "db",
        "refresh": True 
    }
    response = requests.post(login_url, json=payload)
    if response.status_code == 200:
        superset_token = response.json()["access_token"]
        superset_refresh_token = response.json().get("refresh_token")
        logger.info("Đăng nhập Superset thành công.")
    else:
        logger.error(f"Đăng nhập Superset thất bại: {response.text}")
        raise Exception("Failed to authenticate")

def get_header():
    if not superset_token:
        login_superset()
    return {
        "Authorization": f"Bearer {superset_token}",
        "Content-Type": "application/json"
    }

# Endpoint upload_excel
@app.post("/upload_excel")
async def upload_excel(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        table_name = os.path.splitext(file.filename)[0]
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        dataset_payload = {
            "database": 110,  # Thay đổi ID cơ sở dữ liệu nếu cần
            "table_name": table_name,
            "schema": "public",
            "sql": f"SELECT * FROM {table_name}"
        }
        headers = get_header()
        dataset_url = f"{SUPERSET_URL}/api/v1/dataset"
        dataset_response = requests.post(dataset_url, headers=headers, data=json.dumps(dataset_payload))
        if dataset_response.status_code != 201:
            logger.error(f"Tạo dataset thất bại: {dataset_response.text}")
            raise HTTPException(status_code=dataset_response.status_code, detail=dataset_response.text)
        dataset_id = dataset_response.json()["id"]
        logger.info(f"Tạo dataset thành công với ID: {dataset_id}")
        return {"message": "Tạo dataset thành công", "dataset_id": dataset_id}
    except SQLAlchemyError as db_err:
        logger.error(f"Lỗi cơ sở dữ liệu: {db_err}")
        raise HTTPException(status_code=500, detail=str(db_err))
    except Exception as e:
        logger.error(f"Lỗi không mong muốn: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Hàm kiểm tra datasource tồn tại
def check_datasource_exists(datasource_id: int) -> bool:
    datasource_url = f"{SUPERSET_URL}/api/v1/dataset/{datasource_id}"
    response = requests.get(datasource_url, headers=get_header())
    exists = response.status_code == 200
    logger.info(f"Datasource ID {datasource_id} tồn tại: {exists}")
    return exists

# Hàm kiểm tra dashboard tồn tại
def check_dashboard_exists(dashboard_id: int) -> bool:
    dashboard_url = f"{SUPERSET_URL}/api/v1/dashboard/{dashboard_id}"
    response = requests.get(dashboard_url, headers=get_header())
    exists = response.status_code == 200
    logger.info(f"Dashboard ID {dashboard_id} tồn tại: {exists}")
    return exists

# Endpoint tạo biểu đồ
@app.post("/create_chart")
def create_chart(request: ChartRequest):
    try:
        logger.info(f"Nhận yêu cầu tạo biểu đồ: {request.slice_name}")
        headers = get_header()

        # Kiểm tra datasource tồn tại
        if not check_datasource_exists(request.datasource_id):
            raise HTTPException(status_code=404, detail=f"Datasource với ID {request.datasource_id} không tồn tại.")

        # Kiểm tra dashboards tồn tại
        for dashboard_id in request.dashboards:
            if not check_dashboard_exists(dashboard_id):
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
        chart_url = f"{SUPERSET_URL}/api/v1/chart/"
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

# Endpoint tạo dashboard
@app.post("/create_dashboard")
def create_dashboard(dashboard_name: str):
    try:
        headers = get_header()
        dashboard_payload = {
            "dashboard_title": dashboard_name
        }

        dashboard_url = f"{SUPERSET_URL}/api/v1/dashboard/"
        dashboard_response = requests.post(dashboard_url, headers=headers, data=json.dumps(dashboard_payload))

        if dashboard_response.status_code != 201:
            logger.error(f"Tạo dashboard thất bại: {dashboard_response.text}")
            raise HTTPException(status_code=dashboard_response.status_code, detail=dashboard_response.text)

        dashboard_id = dashboard_response.json()["id"]
        logger.info(f"Tạo dashboard thành công với ID: {dashboard_id}")

        return {"message": "Dashboard đã được tạo thành công", "dashboard_id": dashboard_id}

    except Exception as e:
        logger.error(f"Lỗi không mong muốn: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint xuất bản dashboard
@app.post("/publish_dashboard")
def publish_dashboard(dashboard_id: int):
    try:
        headers = get_header()
        publish_url = f"{SUPERSET_URL}/api/v1/dashboard/{dashboard_id}/publish"
        publish_response = requests.post(publish_url, headers=headers)
        if publish_response.status_code != 200:
            logger.error(f"Xuất bản dashboard thất bại: {publish_response.text}")
            raise HTTPException(status_code=publish_response.status_code, detail=publish_response.text)
        logger.info(f"Xuất bản dashboard ID {dashboard_id} thành công.")
        return {"message": "Dashboard đã được xuất bản thành công"}

    except Exception as e:
        logger.error(f"Lỗi không mong muốn: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint lấy link nhúng dashboard
@app.get("/get_embed_link")
def get_embed_link(dashboard_id: int):
    try:
        # Tạo link nhúng cho dashboard
        embed_url = f"{SUPERSET_URL}/superset/dashboard/{dashboard_id}/?standalone=true"

        # Bạn có thể cần cấu hình thêm các tham số bảo mật hoặc token

        logger.info(f"Tạo link nhúng cho dashboard ID {dashboard_id}: {embed_url}")
        return {"embed_link": embed_url}

    except Exception as e:
        logger.error(f"Lỗi không mong muốn: {e}")
        raise HTTPException(status_code=500, detail=str(e))
