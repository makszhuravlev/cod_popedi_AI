from fastapi import FastAPI, WebSocket
from auth import routes as auth_routes
from websocket.socket import websocket_endpoint
from database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Роуты
app.include_router(auth_routes.router)

# WebSocket
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)
