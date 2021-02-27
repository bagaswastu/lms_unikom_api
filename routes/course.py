import json
import re

import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from fastapi.routing import APIRouter

from constant import BASE_URL

router = APIRouter()


@router.get('/{id}')
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
            id_dirty = container.select('.activityinstance > a')
            description_dirty = container.select('.contentafterlink')
            # kondisi untuk deskripsi
            description = ''
            if len(description_dirty) > 0:
                description = description_dirty[0].text

            # kondisi untuk id
            id = ''
            type = ''
            if len(id_dirty) > 0:
                url = container.select('.activityinstance > a')[0]['href']
                id = re.search(r'=([^&?]*)', url).group(1)

                # mendapatkan tipe instance dari url
                type = re.search(r'/mod/(.+)/', url).group(1)

            data.append({
                'id': id,
                'name': instance_name,
                'type': type,
                'description':description
            })

        return data
    except requests.exceptions.TooManyRedirects:
        raise HTTPException(status_code=401, detail={'error_message': 'Autentikasi salah'})


@router.get('/')
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
                course_name = meta[1]
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