import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:9090@localhost/cod_popedi_AI")
SECRET_KEY = os.getenv("SECRET_KEY", "secret123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

IP_AI = "10.0.8.15"
IP_TEXT_AI = "10.0.8.15:11434"
IP_BACK = "10.0.8.15"
PORT_BACK = "8000"
