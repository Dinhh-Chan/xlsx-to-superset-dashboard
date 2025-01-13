from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any
import requests
from app.core.config import settings
from app.utils.logger import get_logger  
from app.utils.auth import get_superset_headers
from pydantic import BaseModel, Field

router = APIRouter()
logger = get_logger(__name__)

class FormDataRequests(BaseModel):
    slice_id: int = Field(..., example=645, description="ID của biểu đồ trong Superset")

def get_headers_dependency():
    return get_superset_headers()

@router.post("/get_embeadcode")
def get_form_data(
    request: FormDataRequests = Body(..., description="Yêu cầu chứa slice_id"),
    headers: Dict[str, str] = Depends(get_headers_dependency)
):
    """
    Lấy dữ liệu biểu mẫu từ Superset dựa trên `slice_id`.
    """
    try:
        formdata_url = f"{settings.SUPERSET_URL}/api/v1/explore/?slice_id={request.slice_id}"
        payload = {
            "slice_id": request.slice_id
        }
        response = requests.get(formdata_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Superset API trả về mã trạng thái {response.status_code}: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Không thể lấy dữ liệu từ Superset: {response.text}"
            )
        data = response.json()
        payload_permanlink = {
            "formData": data["result"]["form_data"],
            "urlParams":[]
        }
        permanlink_url = f"{settings.SUPERSET_URL}/api/v1/explore/permalink"
        response_permanlink = requests.post(permanlink_url, headers=headers, json= payload_permanlink)
        data_response_permanlink= response_permanlink.json()
        print( data_response_permanlink)
        data_response_permanlink["url"] = "http://localhost:8088"+ data_response_permanlink["url"].split("None")[1]+ "?standalone=1&height=400"
        
        return {"data": data_response_permanlink}
    
    except requests.RequestException as e:
        logger.exception("Yêu cầu đến Superset API thất bại.")
        raise HTTPException(status_code=503, detail="Dịch vụ không khả dụng.")
    
    except ValueError:
        logger.exception("Phản hồi JSON từ Superset API không hợp lệ.")
        raise HTTPException(status_code=502, detail="Bad gateway.")
    
    except Exception as e:
        logger.exception("Đã xảy ra lỗi không mong muốn.")
        raise HTTPException(status_code=500, detail="Lỗi nội bộ máy chủ.")
