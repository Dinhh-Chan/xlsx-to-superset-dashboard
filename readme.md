# YÊU CẦU BÀI TOÁN

## Dùng superset API để thực hiện các bước tạo nên 1 biểu đồ với đầu vào là một file excel -> đầu ra là 1 biểu đồ trên superset

### Các bước chạy chương trình

* Chạy môi trường ảo

```
source/venv/bin/activate
```

* 
* Khởi động superset

  ```
  export TAG=3.1.1
  docker compose -f docker-compose-image-tag.yml up
  ```
* Khởi động database (postgres)

  ```
  docker compose up -d
  ```
* Chạy fastapi

  ```
  uvicorn main:app --reload
  ```

### Gọi các API cần thiết

#### /api/v1/database/create_database

Tác dụng: Tạo 1 database connection đến superset

Param requests

```
{
  "database_name": "abc",
  "engine": "postgresql",
  "configuration_method": "dynamic_form",
  "engine_information": {
    "disable_ssh_tunneling": true,
    "supports_file_upload": true
  },
  "driver": "psycopg2",
  "sqlalchemy_uri_placeholder": "postgresql://user:password@host:port/dbname[?key=value&key=value...]",
  "extra": "{\"allows_virtual_table_explore\":true}",
  "expose_in_sqllab": true,
  "parameters": {
    "database": "superset_test",
    "host": "172.17.0.1",
    "password": "admin",
    "port": "5435",
    "username": "admin"
  },
  "masked_encrypted_extra": "{}",
  "ssh_tunnel": {
    "id": 1,
    "password": "your_ssh_password",
    "private_key": "path_to_your_private_key",
    "private_key_password": "your_private_key_password",
    "server_address": "ssh_server_address",
    "server_port": 22,
    "username": "ssh_username"
  }
}
```

Các tham số chỉnh sửa: "database_name", "engine", "parameters"

Sau đó sẽ trả về id database, nhớ lưu lại

#### /api/v1/upload/upload_excel_to_create_dataset

Tác dụng: Tạo 1 dataset và trả về id của dataset đó

Parameter requets

{
	file
"database_id": int

}

#### /api/v1/chart/create_chart_pie

Tác dụng: Tạo 1 piechart và trả về id của piechart đó

Param requests

```
{
  "cache_timeout": 0,
  "certification_details": "",
  "certified_by": "",
  "dashboards": [
    17
  ],
  "datasource_id": 94,
  "datasource_name": "data_example",
  "datasource_type": "table",
  "description": "",
  "external_url": "",
  "is_managed_externally": false,
  "owners": [
    1
  ],
  "params": "{\"viz_type\":\"pie\",\"groupby\":[\"Giới tính\", \"Tôn giáo\"],\"metric\":\"count\",\"adhoc_filters\":[],\"row_limit\":10000,\"sort_by_metric\":true,\"color_scheme\":\"supersetColors\",\"show_labels_threshold\":1,\"show_legend\":true,\"legendType\":\"scroll\",\"legendOrientation\":\"top\",\"label_type\":\"key_value_percent\",\"number_format\":\",d\",\"date_format\":\"smart_date\",\"show_labels\":true,\"labels_outside\":true,\"label_line\":true,\"show_total\":true,\"outerRadius\":70,\"donut\":true,\"innerRadius\":30,\"extra_form_data\":{}}",
  "query_context": "",
  "query_context_generation": false,
  "slice_name": "Tỷ lệ Giới Tính Sinh Viên",
  "viz_type": "pie"
}
```

Tham số cần chỉnh sửa :

* \"groupby\":[\"Giới tính\", \"Tôn giáo\"] (có thể thêm 1 số các trường thông tin khác vào)
* "slice_name": "Tỷ lệ Giới Tính Sinh Viên" (tên của biểu đồ)

#### /api/v1/chartcreate_bar_chart

Chức năng: Tạo barchart và trả về id của biểu đồ

Param Requests

```
{
  "cache_timeout": 0,
  "certification_details": "",
  "certified_by": "",
  "dashboards": [
    17
  ],
  "datasource_id": 94,
  "datasource_name": "data_example",
  "datasource_type": "table",
  "description": "",
  "external_url": "",
  "is_managed_externally": false,
  "owners": [
    1
  ],
  "params": "{\"viz_type\":\"echarts_timeseries_bar\",\"x_axis\":\"Trạng thái học\",\"time_grain_sqla\":\"P1D\",\"x_axis_sort_asc\":true,\"x_axis_sort_series\":\"name\",\"x_axis_sort_series_ascending\":true,\"metrics\":[\"count\"],\"groupby\":[],\"adhoc_filters\":[],\"order_desc\":true,\"row_limit\":10000,\"truncate_metric\":true,\"show_empty_columns\":true,\"comparison_type\":\"values\",\"annotation_layers\":[],\"forecastPeriods\":10,\"forecastInterval\":0.8,\"orientation\":\"vertical\",\"x_axis_title_margin\":15,\"y_axis_title_margin\":15,\"y_axis_title_position\":\"Left\",\"sort_series_type\":\"sum\",\"color_scheme\":\"supersetColors\",\"only_total\":true,\"show_legend\":true,\"legendType\":\"scroll\",\"legendOrientation\":\"top\",\"x_axis_time_format\":\"smart_date\",\"y_axis_format\":\"SMART_NUMBER\",\"truncateXAxis\":true,\"y_axis_bounds\":[null,null],\"rich_tooltip\":true,\"tooltipTimeFormat\":\"smart_date\",\"extra_form_data\":{}}",
  "query_context": "",
  "query_context_generation": false,
  "slice_name": "Tỷ lệ Giới Tính Sinh Viên",
  "viz_type": "echarts_timeseries_bar"
}
```

Các thông số có thể chỉnh sửa

* \"x_axis\":\"Trạng thái học\" (có thể thay bằng trường thông tin khác trong bảng)
* \"groupby\":[] (Có thể thêm 1 số trường thông tin khác cho biểu đồ)
* "viz_type": "echarts_timeseries_bar" (Tên của biểu đồ)

#### /api/v1/chartcreate_line_chart

Tác dụng: Tạo biểu đồ đường

Param requests

```
{
  "cache_timeout": 0,
  "certification_details": "",
  "certified_by": "",
  "dashboards": [
    17
  ],
  "datasource_id": 94,
  "datasource_name": "data_example",
  "datasource_type": "table",
  "description": "",
  "external_url": "",
  "is_managed_externally": false,
  "owners": [
    1
  ],
  "params": "{\"viz_type\":\"echarts_timeseries_line\",\"x_axis\":\"Trạng thái học\",\"time_grain_sqla\":\"P1D\",\"xAxisForceCategorical\":true,\"x_axis_sort\":\"count\",\"x_axis_sort_asc\":true,\"x_axis_sort_series\":\"name\",\"x_axis_sort_series_ascending\":true,\"metrics\":[\"count\"],\"groupby\":[],\"adhoc_filters\":[],\"order_desc\":true,\"row_limit\":10000,\"truncate_metric\":true,\"show_empty_columns\":true,\"comparison_type\":\"values\",\"annotation_layers\":[],\"forecastPeriods\":10,\"forecastInterval\":0.8,\"x_axis_title_margin\":15,\"y_axis_title_margin\":15,\"y_axis_title_position\":\"Left\",\"sort_series_type\":\"sum\",\"color_scheme\":\"supersetColors\",\"seriesType\":\"line\",\"only_total\":true,\"opacity\":0.2,\"markerSize\":6,\"show_legend\":true,\"legendType\":\"scroll\",\"legendOrientation\":\"top\",\"x_axis_time_format\":\"smart_date\",\"rich_tooltip\":true,\"tooltipTimeFormat\":\"smart_date\",\"y_axis_format\":\"SMART_NUMBER\",\"truncateXAxis\":true,\"y_axis_bounds\":[null,null],\"extra_form_data\":{}}",
  "query_context": "",
  "query_context_generation": false,
  "slice_name": "Thống kê tình trạng học tập của sinh viên",
  "viz_type": "echarts_timeseries_line"
}

```

Các tham số có thể chỉnh sửa:

* "x_axis\":\"Trạng thái học\" (có thể thay bằng trường thông tin khác trong bảng)
* \"groupby\":[] (Có thể thêm 1 số trường thông tin khác cho biểu đồ)
* "viz_type": "echarts_timeseries_bar" (Tên của biểu đồ)

#### /api/v1/chartcreate_number_chart

Tác dụng: Tạo number

Param Requests

```
{
  "cache_timeout": 0,
  "certification_details": "",
  "certified_by": "",
  "dashboards": [
    17
  ],
  "datasource_id": 94,
  "datasource_name": "data_example",
  "datasource_type": "table",
  "description": "",
  "external_url": "",
  "is_managed_externally": false,
  "owners": [
    1
  ],
  "params": "{\"viz_type\":\"big_number_total\",\"metric\":{\"aggregate\":\"COUNT_DISTINCT\",\"column\":{\"advanced_data_type\":null,\"certification_details\":null,\"certified_by\":null,\"column_name\":\"Mã ngành\",\"description\":null,\"expression\":null,\"filterable\":true,\"groupby\":true,\"id\":1861,\"is_certified\":false,\"is_dttm\":false,\"python_date_format\":null,\"type\":\"STRING\",\"type_generic\":1,\"verbose_name\":null,\"warning_markdown\":null},\"datasourceWarning\":false,\"expressionType\":\"SIMPLE\",\"hasCustomLabel\":false,\"label\":\"COUNT_DISTINCT(Mã ngành)\",\"optionName\":\"metric_dk97n1u6zud_2997om4xj6s\",\"sqlExpression\":null},\"adhoc_filters\":[],\"header_font_size\":0.4,\"subheader_font_size\":0.15,\"y_axis_format\":\"SMART_NUMBER\",\"time_format\":\"smart_date\",\"extra_form_data\":{}}",
  "query_context": "",
  "query_context_generation": false,
  "slice_name": "Thống kê tình trạng học tập của sinh viên",
  "viz_type": "big_number_total"
}

```

Các thông số có thể chỉnh sửa

```json
 \"metric\":{\"aggregate\":\"COUNT_DISTINCT\"
```

Có thể thay đổi thành các phương thức khác như count, avg v.v...

```json
\"column\":{\"advanced_data_type\":null,\"certification_details\":null,\"certified_by\":null,\"column_name\":\"Mã ngành\",\"description\":null,\"expression\":null,\"filterable\":true,\"groupby\":true,\"id\":1861,\"is_certified\":false,\"is_dttm\":false,\"python_date_format\":null,\"type\":\"STRING\",\"type_generic\":1,\"verbose_name\":null,\"warning_markdown\":null},\"datasourceWarning\":false,\"expressionType\":\"SIMPLE\",\"hasCustomLabel\":false,\"label\":\"COUNT_DISTINCT(Mã ngành)\",\"optionName\":\"metric_dk97n1u6zud_2997om4xj6s\",\"sqlExpression\":null},
```

Có thể thay Colume_name để thay đổi các trường thông tin cần thống kê

#### /api/v1/embeadcode/get_embeadcode

Param truyền vào: id của chart
