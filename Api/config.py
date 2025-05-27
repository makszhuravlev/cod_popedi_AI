import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://adept0msimerol1s:AveImperium!@10.0.8.15/cod_popedi_ai")
SECRET_KEY = os.getenv("SECRET_KEY", "secret123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
