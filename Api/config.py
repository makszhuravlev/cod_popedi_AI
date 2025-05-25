import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://test1:1234@localhost/cod_popedi_ai")
SECRET_KEY = os.getenv("SECRET_KEY", "secret123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
