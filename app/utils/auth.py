from app.core.security import SupersetAuth

superset_auth = SupersetAuth()

def get_superset_headers():
    return superset_auth.get_headers()
