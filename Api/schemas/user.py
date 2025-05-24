from pydantic import BaseModel, EmailStr

class RegisterForm(BaseModel):
    email: EmailStr
    login: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

from pydantic import BaseModel

class RequestCreate(BaseModel):
    text: str

class RequestOut(BaseModel):
    id: int
    user_id: int
    text: str
    status: str