from pydantic import BaseModel, Field, validator  
from typing import List, Optional 
import json 
class LineChartRequest(BaseModel):
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
    params: str = Field(..., example="{\"viz_type\":\"echarts_timeseries_line\",\"x_axis\":\"Trạng thái học\",\"time_grain_sqla\":\"P1D\",\"xAxisForceCategorical\":true,\"x_axis_sort\":\"count\",\"x_axis_sort_asc\":true,\"x_axis_sort_series\":\"name\",\"x_axis_sort_series_ascending\":true,\"metrics\":[\"count\"],\"groupby\":[],\"adhoc_filters\":[],\"order_desc\":true,\"row_limit\":10000,\"truncate_metric\":true,\"show_empty_columns\":true,\"comparison_type\":\"values\",\"annotation_layers\":[],\"forecastPeriods\":10,\"forecastInterval\":0.8,\"x_axis_title_margin\":15,\"y_axis_title_margin\":15,\"y_axis_title_position\":\"Left\",\"sort_series_type\":\"sum\",\"color_scheme\":\"supersetColors\",\"seriesType\":\"line\",\"only_total\":true,\"opacity\":0.2,\"markerSize\":6,\"show_legend\":true,\"legendType\":\"scroll\",\"legendOrientation\":\"top\",\"x_axis_time_format\":\"smart_date\",\"rich_tooltip\":true,\"tooltipTimeFormat\":\"smart_date\",\"y_axis_format\":\"SMART_NUMBER\",\"truncateXAxis\":true,\"y_axis_bounds\":[null,null],\"extra_form_data\":{}}")
    query_context: Optional[str] = Field("", example="Context info")
    query_context_generation: bool = Field(..., example=False)
    slice_name: str = Field(..., example="Thống kê tình trạng học tập của sinh viên")
    viz_type: str = Field(..., example="echarts_timeseries_line")

    @validator('params')
    def validate_params(cls, v):
        try:
            json.loads(v)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in params: {str(e)}")
        return v