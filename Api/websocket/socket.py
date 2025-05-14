from fastapi import WebSocket, WebSocketDisconnect
from auth.utils import verify_token

async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    user = verify_token(token)

    if user is None:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    await websocket.send_text(f"🔐 Welcome, {user}!")

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"{user}: {data}")
    except WebSocketDisconnect:
        print(f"{user} disconnected")
