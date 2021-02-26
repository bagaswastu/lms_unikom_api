import json
import re

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.responses import Response, HTMLResponse, JSONResponse

app = FastAPI()
BASE_URL = 'https://lms.unikom.ac.id'


class LoginModel(BaseModel):
    username: str
    password: str


@app.post('/login')
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
    return cookies


@app.get('/instance/file/{id}')
def get_file(id, cookies: str):
    cookies = {'MoodleSession', cookies}
    url = BASE_URL + '/mod/resource/view.php?id=' + id
    res = requests.get(url, cookies={'MoodleSession': cookies}, stream=True)
    if res.headers.get('Content-Disposition'):
        file = res.content
        return Response(file, headers=dict(res.headers))


@app.get('/courses/{id}')
def get_course(id, cookies: str):
    try:
        cookies = {'MoodleSession': cookies}

        url = BASE_URL + '/course/view.php?id=' + id
        res = requests.get(url, cookies=cookies)

        soup = BeautifulSoup(res.text, 'html.parser')
        containers = soup.select('.activity')
        data = []
        for container in containers:

            # filter restricted content
            restriction = container.select('.tag-info')
            if len(restriction) > 0:
                continue

            instance_name = container.select('.instancename')[0].text
            instance_type = container.select('.instancename > span')[0].text.strip()
            id_dirty = container.select('.activityinstance > a')

            # kondisi untuk id
            if len(id_dirty) > 0:
                id_dirty = container.select('.activityinstance > a')[0]['href']
                id = re.search(r'=([^&?]*)', id_dirty).group(1)
            else:
                id = ''
            data.append({
                'id': id,
                'instance_name': instance_name,
                'instance_type': instance_type,
            })

        return data
    except requests.exceptions.TooManyRedirects:
        raise HTTPException(status_code=401, detail={'error_message': 'Autentikasi salah'})


@app.get('/courses')
def get_courses(cookies):
    try:
        cookies = {'MoodleSession': cookies}
        res = requests.get(BASE_URL + '/my', cookies=cookies)

        # ambil session key
        soup = BeautifulSoup(res.text, 'html.parser')
        script = soup.find('a', {'data-title': 'logout,moodle'})['href']
        sess_key = re.search(r'[^&?]*?=([^&?]*)', script).group(1)

        url = BASE_URL + '/lib/ajax/service.php?sesskey=' + sess_key
        payload = json.dumps([{"index": 0, "methodname": "core_course_get_enrolled_courses_by_timeline_classification",
                               "args": {"offset": 0, "limit": 0, "classification": "all", "sort": "fullname",
                                        "customfieldname": "",
                                        "customfieldvalue": ""}}])
        res = requests.post(url, data=payload, headers={"Content-Type": "application/json"}, cookies=cookies)
        raw_data = json.loads(res.text)[0]

        data = []
        courses = raw_data.get('data').get('courses')
        for course in courses:
            course_name = course.get('fullname')
            course_id = course.get('id')
            progress = course.get('progress')

            # ambil informasi dari nama matkul
            meta = course_name.split(' - ')
            semester = ''
            lecturer = ''
            if len(meta) > 1:
                semester = meta[0]
                lecturer = meta[2]

            data.append({
                'course_id': course_id,
                'course_name': course_name,
                'lecturer': lecturer,
                'semester': semester,
                'progress': progress,
            })
        return data
    except requests.exceptions.TooManyRedirects:
        raise HTTPException(status_code=401, detail={'error_message': 'Autentikasi salah'})


@app.get('/')
def index():
    body = {'Hello': 'World'}
    return body
