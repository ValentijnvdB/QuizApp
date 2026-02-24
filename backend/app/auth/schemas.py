from pydantic import BaseModel


class RegisterForm(BaseModel):
    email: str
    username: str
    password: str


class LoginForm(BaseModel):
    username: str
    password: str


class LogoutSchema(BaseModel):
    refresh_token: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"