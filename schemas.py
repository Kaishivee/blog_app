from pydantic import BaseModel, EmailStr


class CreateUser(BaseModel):
    email: EmailStr
    password: str


class CreatePost(BaseModel):
    id: int
    title: str
    content: str


class UpdatePost(BaseModel):
    title: str
    content: str
