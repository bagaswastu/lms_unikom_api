import json

import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter

from constant import BASE_URL, API_URL, API_KEY
from schemas import LoginModel

router = APIRouter()


@router.post('/login', description="Autentikasi untuk login. Digunakan untuk men-generate session cookies")
def login(item: LoginModel):
    session_requests = requests.session()
    login_url = BASE_URL + "/login/index.php"
    result = session_requests.get(login_url)

    # Mendapatkan token XSRF
    soup = BeautifulSoup(result.text, 'html.parser')
    authenticity_token = soup.find('input', {'name': 'logintoken'}).get('value')

    payload = {
        "logintoken": authenticity_token,
        "username": item.username,
        "password": item.password,
    }

    session_requests.post(
        login_url,
        data=payload,
        headers=dict(referer=login_url)
    )

    cookies = session_requests.cookies['MoodleSession']

    # Mendapatkan token dari api unikom
    payload = {'Dashboard-Api-Key': API_KEY}
    body = {
        'nim': item.username,
        'password': item.password
    }
    res = requests.post(API_URL + '/dashboard/public/api/login', headers=payload, data=body)

    token = ''
    if res.status_code == 200:
        token = json.loads(res.text)['token']

    return {
        'cookies': cookies,
        'token': token,
    }
