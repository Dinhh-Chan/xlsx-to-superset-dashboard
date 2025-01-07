import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SUPERSET_URL: str = os.getenv("SUPERSET_URL", "http://localhost:8088")
    SUPERSET_USERNAME: str = os.getenv("SUPERSET_USERNAME", "admin")
    SUPERSET_PASSWORD: str = os.getenv("SUPERSET_PASSWORD", "admin")
    
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5435")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "admin")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "superset_test")

settings = Settings()
