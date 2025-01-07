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