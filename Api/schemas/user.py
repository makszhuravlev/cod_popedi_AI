from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import List, Optional

class FileType(str, Enum):
    image = "image"
    music = "music"
    text = "text"
    other = "other"

class RegisterForm(BaseModel):
    email: EmailStr
    login: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class RequestCreate(BaseModel):
    text: str

class RequestOut(BaseModel):
    id: int
    user_id: int
    text: str
    status: str

class GeneratedFileCreate(BaseModel):
    file_url: str
    file_type: FileType

class GeneratedFileOut(BaseModel):
    id: int
    request_id: int
    file_url: str
    file_type: FileType