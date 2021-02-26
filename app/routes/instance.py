import requests
from fastapi.openapi.models import Response
from fastapi.routing import APIRouter

from app.constant import BASE_URL

router = APIRouter()


@router.get('/instance/file/{id}', description="Untuk download file materi dari mata kuliah")
async def get_file(id, cookies: str):
    cookies = {'MoodleSession', cookies}
    url = BASE_URL + '/mod/resource/view.php?id=' + id
    res = requests.get(url, cookies={'MoodleSession': cookies}, stream=True)
    if res.headers.get('Content-Disposition'):
        file = res.content
        return Response(file, headers=dict(res.headers))
