from fastapi import FastAPI

from routes import course, authentication, instance

app = FastAPI(title="LMS UNIKOM API")

app.include_router(course.router, tags=['Courses'], prefix='/courses')
app.include_router(instance.router, tags=['Instances'], prefix='/instances')
app.include_router(authentication.router, tags=['Authentication'])


@app.get('/')
def index():
    body = {'Hello': 'World'}
    return body
