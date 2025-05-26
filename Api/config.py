import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:9090@localhost/cod_popedi_AI")
SECRET_KEY = os.getenv("SECRET_KEY", "secret123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
