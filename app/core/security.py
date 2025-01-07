import requests
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SupersetAuth:
    def __init__(self):
        self.token = None

    def login(self):
        login_url = f"{settings.SUPERSET_URL}/api/v1/security/login"
        payload = {
            "username": settings.SUPERSET_USERNAME,
            "password": settings.SUPERSET_PASSWORD,
            "provider": "db",
            "refresh": True 
        }
        response = requests.post(login_url, json=payload)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.refresh_token = response.json().get("refresh_token")
            logger.info("Đăng nhập Superset thành công.")
        else:
            logger.error(f"Đăng nhập Superset thất bại: {response.text}")
            raise Exception("Failed to authenticate")

    def get_headers(self):
        if not self.token:
            self.login()
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
