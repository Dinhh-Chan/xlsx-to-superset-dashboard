from pydantic import BaseModel, Field, validator  
from typing import List, Optional 
import json 
class BarChartRequest(BaseModel):
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
    params: str = Field(..., example="{\"viz_type\":\"big_number_total\",\"metric\":{\"aggregate\":\"COUNT_DISTINCT\",\"column\":{\"advanced_data_type\":null,\"certification_details\":null,\"certified_by\":null,\"column_name\":\"Mã ngành\",\"description\":null,\"expression\":null,\"filterable\":true,\"groupby\":true,\"id\":1861,\"is_certified\":false,\"is_dttm\":false,\"python_date_format\":null,\"type\":\"STRING\",\"type_generic\":1,\"verbose_name\":null,\"warning_markdown\":null},\"datasourceWarning\":false,\"expressionType\":\"SIMPLE\",\"hasCustomLabel\":false,\"label\":\"COUNT_DISTINCT(Mã ngành)\",\"optionName\":\"metric_dk97n1u6zud_2997om4xj6s\",\"sqlExpression\":null},\"adhoc_filters\":[],\"header_font_size\":0.4,\"subheader_font_size\":0.15,\"y_axis_format\":\"SMART_NUMBER\",\"time_format\":\"smart_date\",\"extra_form_data\":{}}")
    query_context: Optional[str] = Field("", example="Context info")
    query_context_generation: bool = Field(..., example=False)
    slice_name: str = Field(..., example="Thống kê tình trạng học tập của sinh viên")
    viz_type: str = Field(..., example="echarts_timeseries_bar")

    @validator('params')
    def validate_params(cls, v):
        try:
            json.loads(v)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in params: {str(e)}")
        return v