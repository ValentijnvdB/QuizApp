from pydantic import BaseModel


class User(BaseModel):
    username: str


class CreateQuiz(BaseModel):
    title: str
    description: str
    creator_id: int

class UpdateQuiz(BaseModel):
    title: str
    description: str
    is_published: bool