import json
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
            try:
                message = json.loads(data)
                action = message.get("action")
                if action == "text":
                    await websocket.send_json({
                        "status": "success",
                        "message": "E"
                    })
                elif action == "image":
                    await websocket.send_json({
                        "status": "success",
                        "message": "E"
                    })
                elif action == "music":
                    await websocket.send_json({
                        "status": "success",
                        "message": "E"
                    })
                elif action == "all":
                    await websocket.send_json({
                        "status": "success",
                        "message": "E"
                    })
                else:
                    await websocket.send_json({
                        "status": "error",
                        "message": "Invalid action"
                    })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "status": "error",
                    "message": "Инвалидный джейсон стетхем"
                })
            except KeyError as e:
                await websocket.send_json({
                    "status": "error",
                    "message": f"Пупупупу ошибка: {e}"
                })
            except Exception as e:
                await websocket.send_json({
                    "status": "error",
                    "message": f"Сервер арбуз: {str(e)}"
                })
    except WebSocketDisconnect:
        print(f"{user} disconnected")
