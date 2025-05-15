from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from database import get_db
from models.user import User
from schemas.user import RegisterForm, Token
from auth.utils import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/register")
def register_user(data: RegisterForm, db: Session = Depends(get_db)):
    user = db.query(User).filter((User.email == data.email) | (User.login == data.login)).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        email=data.email,
        login=data.login,
        password_hash=get_password_hash(data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered successfully"}

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect login or password")

    token = create_access_token({"sub": user.login})
    return {"access_token": token, "token_type": "bearer"}
