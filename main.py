from fastapi import FastAPI

from routes import course, authentication, instance, user

app = FastAPI(title="LMS UNIKOM API")

app.include_router(course.router, tags=['Courses'], prefix='/courses')
app.include_router(instance.router, tags=['Instances'], prefix='/instances')
app.include_router(authentication.router, tags=['Authentication'])
app.include_router(user.router, tags=['User'])


@app.get('/')
def index():
    body = {'Hello': 'World'}
    return body
