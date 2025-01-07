from fastapi import FastAPI, File, UploadFile, HTTPException
import requests 
import pandas as pd 
import json 
import os 
from dotenv import load_dotenv 
from pydantic import BaseModel,Field 
import io 
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()
#superset config
SUPERSET_URL = os.getenv("SUPERSET_URL", "http://localhost:8088")
SUPERSET_USERNAME = "admin"
SUPERSET_PASSWORD ="admin"
#posgresql config
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5435")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
POSTGRES_DB = "superset_test"
#connect db 
DATABASE_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URI)
class ChartRequest(BaseModel):
    cache_timeout: int = Field(..., example=0)
    certification_details: Optional[str] = Field("", example="Chi tiết chứng nhận")
    certified_by: Optional[str] = Field("", example="Người chứng nhận")
    dashboards: List[int] = Field(..., example=[1])
    datasource_id: int = Field(..., example=94)
    datasource_name: str = Field(..., example="Your_Datasource_Name")
    datasource_type: str = Field(..., example="table")
    description: Optional[str] = Field("", example="Biểu đồ thể hiện tỷ lệ giới tính của sinh viên.")
    external_url: Optional[str] = Field("", example="http://example.com")
    is_managed_externally: bool = Field(..., example=False)
    owners: List[int] = Field(..., example=[1])
    params: str = Field(..., example='{"metrics": ["count"], "groupby": ["Giới tính"]}')
    query_context: Optional[str] = Field("", example="Context info")
    query_context_generation: bool = Field(..., example=False)
    slice_name: str = Field(..., example="Tỷ lệ Giới Tính Sinh Viên")
    viz_type: str = Field(..., example="pie")
#get token
superset_token = None 
def login_superset():
    global superset_token 
    login_url = f"{SUPERSET_URL}/api/v1/security/login"
    payload ={
        "username":SUPERSET_USERNAME,
        "password": SUPERSET_PASSWORD,
        "provider": "db",
        "refresh": True 
    }
    response = requests.post(login_url, json = payload)
    if response.status_code == 200 :
        superset_token = response.json()["access_token"]
    else :
        raise Exception("Failed to authenticate")
def get_header():
    if not superset_token :
        login_superset()
    return {
        "Authorization": f"Bearer {superset_token}",
        "Content-Type": "application/json"
    }


@app.post("/upload_excel")
async def upload_excel(file: UploadFile = File(...)):
    try :
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        table_name = os.path.splitext(file.filename)[0]
        df.to_sql(table_name,engine, if_exists= 'replace', index=False)
        dataset_payload = {
            "database": 110 ,
            "table_name":table_name,
            "schema":"public",
            "sql":f"SELECT * FROM {table_name}"
        }
        header = get_header()
        dataset_url = f"{SUPERSET_URL}/api/v1/dataset"
        dataset_response = requests.post(dataset_url, headers= header, data=json.dumps(dataset_payload))
        if dataset_response.status_code!= 201 :
            raise HTTPException(status_code= dataset_response.status_code, detail= dataset_response.text)
        dataset_id = dataset_response.json()["id"]
        return {"message":"make dataset completed", "dataset_id": dataset_id}
    except SQLAlchemyError as db_err:
        raise HTTPException(status_code=500, detail=str(db_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
def check_datasource_exists(datasource_id: int) -> bool:
    datasource_url = f"{SUPERSET_URL}/api/v1/dataset/{datasource_id}"
    response = requests.get(datasource_url, headers=get_header())
    return response.status_code == 200

def check_dashboard_exists(dashboard_id: int) -> bool:
    dashboard_url = f"{SUPERSET_URL}/api/v1/dashboard/{dashboard_id}"
    response = requests.get(dashboard_url, headers=get_header())
    return response.status_code == 200
@app.post("/create_chart")
def create_chart(request: ChartRequest):
    try:
        logger.info(f"Received request to create chart: {request.slice_name}")
        headers = get_header()

        # Kiểm tra datasource tồn tại
        if not check_datasource_exists(request.datasource_id):
            # raise HTTPException(status_code=404, detail=f"Datasource with ID {request.datasource_id} does not exist.")
            pass 

        # Kiểm tra dashboards tồn tại
        for dashboard_id in request.dashboards:
            if not check_dashboard_exists(dashboard_id):
                pass
                # raise HTTPException(status_code=404, detail=f"Dashboard with ID {dashboard_id} does not exist.")

        # Kiểm tra định dạng của params (chuỗi JSON hợp lệ)
        try:
            # Nếu params không phải là chuỗi JSON hợp lệ, sẽ phát sinh lỗi
            json.loads(request.params)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON in params: {str(e)}")

        # Xây dựng payload cho Superset API
        chart_payload = {
            "slice_name": request.slice_name,
            "viz_type": request.viz_type,
            "datasource_id": request.datasource_id,
            "datasource_type": request.datasource_type,
            "params": request.params  # Truyền trực tiếp chuỗi JSON
        }

        # Gửi yêu cầu tới Superset API
        chart_url = f"{SUPERSET_URL}/api/v1/chart/"
        chart_response = requests.post(chart_url, headers=headers, json=chart_payload)

        if chart_response.status_code != 201:
            logger.error(f"Failed to create chart: {chart_response.text}")
            raise HTTPException(status_code=chart_response.status_code, detail=chart_response.text)

        chart_id = chart_response.json().get("id")
        if not chart_id:
            logger.error("Superset did not return chart ID.")
            raise HTTPException(status_code=500, detail="Superset did not return chart ID.")

        # Thêm biểu đồ vào các dashboard đã chỉ định
        for dashboard_id in request.dashboards:
            add_chart_to_dashboard(dashboard_id, chart_id)

        logger.info(f"Chart created successfully with ID: {chart_id}")
        return {"message": "Biểu đồ đã được tạo thành công", "chart_id": chart_id}

    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("An unexpected error occurred.")
        raise HTTPException(status_code=500, detail=str(e))
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
            raise HTTPException(status_code=dashboard_response.status_code, detail=dashboard_response.text)

        dashboard_id = dashboard_response.json()["id"]

        return {"message": "Dashboard đã được tạo thành công", "dashboard_id": dashboard_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/add_chart_to_dashboard")
def add_chart_to_dashboard(dashboard_id: int, chart_id: int):
    try:
        headers = get_header()
        dashboard_url = f"{SUPERSET_URL}/api/v1/dashboard/{dashboard_id}"
        dashboard_response = requests.get(dashboard_url, headers=headers)
        if dashboard_response.status_code != 200:
            raise HTTPException(status_code=dashboard_response.status_code, detail=dashboard_response.text)

        dashboard_data = dashboard_response.json()
        layout = dashboard_data.get("position_json", {})
        if not layout:
            layout = {"DASHBOARD_VERSION_KEY": "v2", "version": 2, "layout": {}}
        new_slice = {
            "type": "CHART",
            "id": chart_id,
            "children": [],
            "meta": {
                "chartId": chart_id,
                "width": 4,
                "height": 4
            }
        }

        # Thêm slice vào layout
        # Đối với Superset v2, layout thường là dạng grid
        # Ở đây đơn giản là thêm slice vào root layout
        if "ROOT_ID" not in layout["layout"]:
            layout["layout"]["ROOT_ID"] = {
                "children": [],
                "type": "ROOT",
                "id": "ROOT_ID",
                "children_v": []
            }

        # Tạo một ID duy nhất cho grid
        new_grid_id = f"GRID_ID_{chart_id}"

        # Thêm grid mới vào root
        layout["layout"]["ROOT_ID"]["children"].append(new_grid_id)
        layout["layout"][new_grid_id] = {
            "children": [chart_id],
            "type": "ROW",
            "id": new_grid_id,
            "children_v": []
        }

        # Cập nhật lại position_json
        dashboard_data["position_json"] = json.dumps(layout)

        # Gửi lại cập nhật
        update_response = requests.put(dashboard_url, headers=headers, data=json.dumps(dashboard_data))
        if update_response.status_code != 200:
            raise HTTPException(status_code=update_response.status_code, detail=update_response.text)

        return {"message": "Biểu đồ đã được thêm vào dashboard thành công"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/publish_dashboard")
def publish_dashboard(dashboard_id: int):
    try:
        headers = get_header()
        publish_url = f"{SUPERSET_URL}/api/v1/dashboard/{dashboard_id}/publish"
        publish_response = requests.post(publish_url, headers=headers)
        if publish_response.status_code != 200:
            raise HTTPException(status_code=publish_response.status_code, detail=publish_response.text)
        return {"message": "Dashboard đã được xuất bản thành công"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_embed_link")
def get_embed_link(dashboard_id: int):
    try:
        # Tạo link nhúng cho dashboard
        embed_url = f"{SUPERSET_URL}/superset/dashboard/{dashboard_id}/?standalone=true"

        # Bạn có thể cần cấu hình thêm các tham số bảo mật hoặc token

        return {"embed_link": embed_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))