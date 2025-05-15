from fastapi import FastAPI, WebSocket
from auth import routes as auth_routes
from websocket.socket import websocket_endpoint
from database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

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
