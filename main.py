from fastapi import FastAPI
from bs4 import BeautifulSoup
import requests

app = FastAPI()
url = 'https://lms.unikom.ac.id/login/index.php'
req = requests.get(url)


@app.get('/')
def index():
    soup = BeautifulSoup(req.text, 'html.parser')
    return {'title': soup.title.text}