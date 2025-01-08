from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from app.utils.auth import get_superset_headers
from app.core.config import settings
from app.utils.logger import get_logger
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import io
import os
import json
import requests

router = APIRouter()
logger = get_logger(__name__)

# Kết nối DB (Có thể di chuyển vào core/config.py hoặc dependencies.py nếu cần)
DATABASE_URI = f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_engine(DATABASE_URI)

@router.post("/upload_excel_to_create_dataset")
async def upload_excel(
    file: UploadFile = File(...),
    database_id: int = Form(...)
):
    try:
        logger.info(f"Nhận yêu cầu upload file: {file.filename} với Database ID: {database_id}")
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        table_name = os.path.splitext(file.filename)[0]
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logger.info(f"Lưu dữ liệu vào bảng: {table_name}")

        dataset_payload = {
            "database": database_id,  # Nhận từ input
            "table_name": table_name,
            "schema": "public",
            "sql": f"SELECT * FROM {table_name}"
        }
        headers = get_superset_headers()
        dataset_url = f"{settings.SUPERSET_URL}/api/v1/dataset"
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
