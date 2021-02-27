from pydantic.main import BaseModel


class LoginModel(BaseModel):
    username: str
    password: str