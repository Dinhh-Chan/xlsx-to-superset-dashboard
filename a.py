import requests

SUPERSET_URL = "https://dashboard.ript.vn"
SUPERSET_USERNAME = "admin"
SUPERSET_PASSWORD = "admin"
SUPERSET_DB_ID = 8
POSTGRES_HOST = "192.168.30.181"
POSTGRES_PORT = "5777"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_DB = "api"

def get_superset_session():
    login_url = f"{SUPERSET_URL}/api/v1/security/login"
    payload = {
        "username": SUPERSET_USERNAME,
        "password": SUPERSET_PASSWORD,
        "provider": "db",
    }
    session = requests.Session()
    login_response = session.post(login_url, json=payload)
    access_token = login_response.json()['access_token']

    csrf_url = f"{SUPERSET_URL}/api/v1/security/csrf_token/"
    session.headers.update({"Authorization": f"Bearer {access_token}"})
    csrf_response = session.get(csrf_url)
    csrf_token = csrf_response.json()['result']

    session.headers.update({"X-CSRFToken": csrf_token, "Content-Type": "application/json"})
    return session


def create_dashboard(name):
    dashboard_payload = {
		"certified_by": "",
		"certification_details": "",
		"css": "",
		"dashboard_title": name,
		"slug": None,
		"owners": [
			1, 2
		],
		"json_metadata": {
			"chart_configuration": {},
			"global_chart_configuration": {
				"scope": {
					"rootPath": [
						"ROOT_ID"
					],
					"excluded": []
				},
				"chartsInScope": []
			},
			"color_scheme": "",
			"refresh_frequency": 0,
			"shared_label_colors": {},
			"color_scheme_domain": [],
			"expanded_slices": {},
			"label_colors": {},
			"timed_refresh_immune_slices": [],
			"cross_filters_enabled":True,
			"default_filters": "{}",
			"positions": {
				"DASHBOARD_VERSION_KEY": "v2",
				"GRID_ID": {
					"children": [],
					"id": "GRID_ID",
					"parents": [
						"ROOT_ID"
					],
					"type": "GRID"
				},
				"HEADER_ID": {
					"id": "HEADER_ID",
					"type": "HEADER",
					"meta": {
						"text": "TEST CREATE"
					}
				},
				"ROOT_ID": {
					"children": [
						"GRID_ID"
					],
					"id": "ROOT_ID",
					"type": "ROOT"
				}
			},
			"filter_scopes": {}
		}
	}
    session = get_superset_session()
    dashboard_url = f"{SUPERSET_URL}/api/v1/dashboard/"
    dashboard_response = session.post(dashboard_url, json=dashboard_payload)
    dashboard_id = dashboard_response.json().get("id", None)
    return dashboard_id


def get_chart_permalink(slice_id):
    """
    Hàm trả về permalink (URL) cho chart (slice) có ID = slice_id.
    """
    try:
        # 1. Tạo session (đã đăng nhập)
        session = get_superset_session()

        # 2. Lấy form_data
        explore_url = f"{SUPERSET_URL}/api/v1/explore/"
        response = session.get(explore_url, params={"slice_id": slice_id})
        response.raise_for_status()
        data = response.json()
        
        form_data = data.get("result", {}).get("form_data")
        if not form_data:
            raise ValueError(f"Không tìm thấy 'form_data' cho chart {slice_id}.")

        # 3. Tạo permalink
        permalink_url = f"{SUPERSET_URL}/api/v1/explore/permalink"
        payload = {
            "formData": form_data,
            "urlParams": []
        }
        res_perma = session.post(permalink_url, json=payload)
        res_perma.raise_for_status()

        perma_data = res_perma.json()
        original_url = perma_data.get("url")
        if not original_url:
            raise ValueError("Không có 'url' trong phản hồi permalink.")

        # 4. Xử lý url trả về thành link đầy đủ
        if not original_url.startswith("http"):
            original_url = SUPERSET_URL.rstrip('/') + original_url
        
        # Nếu muốn hiển thị embed, standalone = 1, height = 400
        final_url = f"{original_url}?standalone=1&height=400"

        return final_url

    except Exception as e:
        print(f"Lỗi khi tạo permalink cho chart {slice_id}: {e}")
        return None

def create_chart(request):
	dashboard_id = create_dashboard(request.chart_name)
	chart_payload = {
        "dashboards": [dashboard_id, ],
        "datasource_id": request.datasource_id,
        "datasource_type": "table",
        "params": request.params,
        "slice_name": request.chart_name,
        "viz_type": request.chart_type,
    }
	session = get_superset_session()
	chart_url = f"{SUPERSET_URL}/api/v1/chart/"
	chart_response = session.post(chart_url, json=chart_payload)
	chart_id = chart_response.json().get("id", None)
	return {
        "chart_id": chart_id,
	}

print(get_chart_permalink(365))
# print(get_dashboard(6))