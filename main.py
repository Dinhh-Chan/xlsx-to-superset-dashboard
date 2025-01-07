from fastapi import FastAPI, File, UploadFile, HTTPException
import requests 
import pandas as pd 
import json 
app = FastAPI()
SUPERSET_URL ="http://localhost:8088"
SUPERSET_USERNAME = "admin"
SUPERSET_PASSWORD ="admin"
superset_token = None 
def login_superset():
    global superset_token 
    login_url = f"{SUPERSET_URL}"
    payload ={
        "username":SUPERSET_USERNAME,
        "password": SUPERSET_PASSWORD,
        "provider": "db",
        "refresh": True 
    }
    response = requests.post(login_url, json = payload)
    if response.status_code == 200 :
        superset_token = response["access_token"]
    else :
        raise Exception("Failed to authenticate")
def get_header():
    if not superset_token :
        login_superset()
    return {
        "Authorization": f"Bearer {superset_token}",
        "Content-Type": "application/json"
    }
