import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from fastapi.routing import APIRouter
from starlette.responses import Response

from app.constant import BASE_URL

router = APIRouter()


@router.get('/forum/{id}', description='Digunakan untuk mendapatkan konten forum')
def get_forum(id, cookies):
    cookies = {'MoodleSession': cookies}
    url = BASE_URL + '/mod/forum/view.php?id=' + id
    res = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(res.text, 'html.parser')
    title = soup.select_one('h2').text
    content = soup.select_one('.no-overflow').text
    return {
        'title': title,
        'content': content,
    }


@router.get('/url/{id}', description='Digunakan untuk mendapatkan URL instance')
def get_url(id, cookies):
    try:
        cookies = {'MoodleSession': cookies}
        url = BASE_URL + '/mod/url/view.php?id=' + id
        res = requests.get(url, cookies=cookies, stream=True)
        redirect_url = res.url
        return {
            'status_code': res.status_code,
            'url': redirect_url
        }
    except requests.exceptions.TooManyRedirects:
        raise HTTPException(status_code=401, detail={'error_message': 'Autentikasi salah'})


@router.get('/file/{id}', description='Digunakan untuk download file materi dari mata kuliah')
async def get_file(id, cookies):
    try:
        cookies = {'MoodleSession': cookies}
        url = BASE_URL + '/mod/resource/view.php?id=' + id
        res = requests.get(url, cookies=cookies, stream=True)
        if res.headers.get('Content-Disposition'):
            file = res.content
            return Response(file, headers=dict(res.headers))
    except requests.exceptions.TooManyRedirects:
        raise HTTPException(status_code=401, detail={'error_message': 'Autentikasi salah'})
