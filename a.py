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


def get_shot(id):
    try:
        session = get_superset_session()
        formdata_url = f"{SUPERSET_URL}/api/v1/explore/"
        response = requests.get(formdata_url, params={
			"slice_id": id
		})
        # print(formdata_url)
        data = response.json()
        # print(data)
        payload_permanlink = {
            "formData": data["result"]["form_data"],
            "urlParams":[]
        }
        permanlink_url = f"{SUPERSET_URL}/api/v1/explore/permalink"
        response_permanlink = requests.post(permanlink_url, json=payload_permanlink)
        data_response_permanlink= response_permanlink.json()
        print(data_response_permanlink)
        data_response_permanlink["url"] = SUPERSET_URL + data_response_permanlink["url"].split("None")[1]+ "?standalone=1&height=400"
        
        return {"data": data_response_permanlink}
    except Exception as e:
        print(e)

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

print(get_shot(59))
# print(get_dashboard(6))