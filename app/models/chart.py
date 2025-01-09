from pydantic import BaseModel, Field, validator
from typing import List, Optional
import json

class PieChartRequest(BaseModel):
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
    params: str = Field(..., example="{\"viz_type\":\"pie\",\"groupby\":[\"Giới tính\"],\"metric\":\"count\",\"adhoc_filters\":[],\"row_limit\":10000,\"sort_by_metric\":true,\"color_scheme\":\"supersetColors\",\"show_labels_threshold\":1,\"show_legend\":true,\"legendType\":\"scroll\",\"legendOrientation\":\"top\",\"label_type\":\"key_value_percent\",\"number_format\":\",d\",\"date_format\":\"smart_date\",\"show_labels\":true,\"labels_outside\":true,\"label_line\":true,\"show_total\":true,\"outerRadius\":70,\"donut\":true,\"innerRadius\":30,\"extra_form_data\":{}}")
    query_context: Optional[str] = Field("", example="Context info")
    query_context_generation: bool = Field(..., example=False)
    slice_name: str = Field(..., example="Tỷ lệ Giới Tính Sinh Viên")
    viz_type: str = Field(..., example="pie")

