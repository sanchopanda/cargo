import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_BASE_HOST = os.getenv('API_BASE_HOST')
API_BASE_URL = f"{API_BASE_HOST}/api/v1/"

# Создание сессии для управления куками и заголовками
session = requests.Session()
session.headers.update({
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-ApiKey": API_KEY,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
})

def check_api_access():
    url = f"{API_BASE_URL}test/ping"
    response = session.get(url)
    return response.ok

def login(login_data):
    url = f"{API_BASE_URL}account/login"
    response = session.post(url, json=login_data)
    if response.ok:
        cookie = response.cookies.get(".AspNet.ApplicationCookie")
        if cookie:
            session.headers.update({"Cookie": f".AspNet.ApplicationCookie={cookie}"})
            return True
    return False

def get_requests_data():
    url = f"{API_BASE_URL}request"
    response = session.get(url)
    if response.ok:
        return response.json()
    return None

def fetch_request(id):
    url = f"{API_BASE_URL}request/{id}"
    response = session.get(url)
    if response.ok:
        return response.json()
    return None