from pydantic import BaseModel, Field, validator
from typing import List, Optional
import json

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
    params: str = Field(..., example='{"datasource":"94__table","viz_type":"pie","groupby":["Giới tính"],"metrics":["count"],"dashboards":[17]}')
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
