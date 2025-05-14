from pydantic import BaseModel, EmailStr

class RegisterForm(BaseModel):
    email: EmailStr
    login: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
