from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import List, Optional

class FileType(str, Enum):
    image = "image"
    music = "music"
    text = "text"
    gift = "gift"

class RegisterForm(BaseModel):
    email: EmailStr
    login: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class RequestOut(BaseModel):
    id: int
    reference_text: str
    texts: List[str] = []
    images: List[str] = []
    music: List[str] = []
    gifts: List[str] = []

class UserRequestsResponse(BaseModel):
    requests: List[RequestOut]