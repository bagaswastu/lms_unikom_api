import json
import string

import requests
from fastapi import APIRouter

from constant import API_URL, API_KEY

router = APIRouter()


@router.get('/profile', description='Digunakan untuk mendapatkan detail profil')
def get_profile(token, nim):
    url = API_URL + '/dashboard/public/api/profile'
    payload = {
        'Dashboard-Api-Key': API_KEY,
        'Authorization': 'Bearer ' + token
    }
    res = requests.post(url, headers=payload, data={
        'nim': nim,
    })
    res_data = json.loads(res.text)

    return {
        'nim': res_data['nim'],
        'name': string.capwords(res_data['nama']),
        'email': res_data['email'],
        'study_program': string.capwords(res_data['prodi']),
        'class': res_data['kelas']
    }
