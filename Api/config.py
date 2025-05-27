import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://Adept0mSimerol1S:AveImperium!@10.0.8.15/cod_pobedi_ai")
SECRET_KEY = os.getenv("SECRET_KEY", "secret123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
