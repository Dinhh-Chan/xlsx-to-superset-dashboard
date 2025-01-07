from fastapi import FastAPI, File, UploadFile, HTTPException
import requests 
import pandas as pd 
import json 
import os 
from dotenv import load_dotenv 
import io 
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
app = FastAPI()
#superset config
SUPERSET_URL = os.getenv("SUPERSET_URL", "http://localhost:8088")
SUPERSET_USERNAME = os.getenv("SUPERSET_USERNAME")
SUPERSET_PASSWORD =os.getenv("SUPERSET_PASSWORD")
#posgresql config
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5435")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
POSTGRES_DB = os.getenv("POSTGRES_DB", "superset_test")
#connect db 
DATABASE_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URI)
#get token
superset_token = None 
def login_superset():
    global superset_token 
    login_url = f"{SUPERSET_URL}"
    payload ={
        "username":SUPERSET_USERNAME,
        "password": SUPERSET_PASSWORD,
        "provider": "db",
        "refresh": True 
    }
    response = requests.post(login_url, json = payload)
    if response.status_code == 200 :
        superset_token = response["access_token"]
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
            "databse": 1 ,
            "table_name":table_name,
            "schema":"public",
            "sql":f"SELECT * FROM {table_name}"
        }
        header = get_header()
        dataset_url = f"{SUPERSET_URL}/api/v1/dataset/"
        dataset_response = requests.post(dataset_url, headers= header, data=json.dumps(dataset_payload))
        if dataset_response.status_code!= 200 :
            raise HTTPException(status_code= dataset_response.status_code, detail= dataset_response.text)
        dataset_id = dataset_response.json()["id"]
        return {"message":"make dataset completed", "dataset_id": dataset_id}
    except SQLAlchemyError as db_err:
        raise HTTPException(status_code=500, detail=str(db_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/create_chart")
def create_chart(
    dataset_id: int,
    chart_type: str,
    chart_name: str,
    metrics: list, 
    dimensions: list,
    additional_params: dict= None 
):
    try :
        headers = get_header 
        params = {
            "metrics": metrics,
            "groupby": dimensions,
            "adhoc_filters": [],
            "row_limit": 1000,
            "order_desc": True,
            "since": "100 years ago",
            "until": "now",
        }
        if chart_type == "pie":
            params.update({
                "color_scheme": "bnbColors",
                "donut": False,
                "show_legend": True,
            })
        elif chart_type == "pie_donut":
            params.update({
                "color_scheme": "bnbColors",
                "donut": True,
                "show_legend": True,
            })
        elif chart_type == "bar":
            params.update({
                "color_scheme": "bnbColors",
                "show_legend": True,
                "bar_stacked": False,  # False cho cột đơn, True cho cột chồng
            })
        elif chart_type == "bar_stacked":
            params.update({
                "color_scheme": "bnbColors",
                "show_legend": True,
                "bar_stacked": True,
            })
        elif chart_type == "line":
            params.update({
                "color_scheme": "bnbColors",
                "show_legend": True,
            })
        elif chart_type == "number":
            params = {  # Các tham số cụ thể cho biểu đồ số
                "metric": metrics[0],
                "number_format": "SMART_NUMBER",
                "label": chart_name
            }
        else:
            raise HTTPException(status_code=400, detail="Loại biểu đồ không được hỗ trợ")

        if additional_params:
            params.update(additional_params)

        chart_payload = {
            "slice_name": chart_name,
            "viz_type": chart_type,
            "datasource_id": dataset_id,
            "datasource_type": "table",
            "params": params
        }

        chart_url = f"{SUPERSET_URL}/api/v1/chart/"
        chart_response = requests.post(chart_url, headers=headers, data=json.dumps(chart_payload))

        if chart_response.status_code != 201:
            raise HTTPException(status_code=chart_response.status_code, detail=chart_response.text)

        chart_id = chart_response.json()["id"]

        return {"message": "Biểu đồ đã được tạo thành công", "chart_id": chart_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
