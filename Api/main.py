from fastapi import FastAPI, WebSocket
from auth import routes as auth_routes
from websocket.socket import websocket_endpoint
from database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from pathlib import Path
from fastapi.staticfiles import StaticFiles




Base.metadata.create_all(bind=engine)

app = FastAPI()

# Монтируем папку static
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [

]

# Добавление CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                # разрешённые источники
    allow_credentials=True,
    allow_methods=["*"],                  # разрешённые HTTP методы
    allow_headers=["*"],                  # разрешённые заголовки
)
# Роуты
app.include_router(auth_routes.router)

# WebSocket
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)
