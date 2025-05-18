import json
from fastapi import WebSocket, WebSocketDisconnect
from auth.utils import verify_token

from fastapi import FastAPI, HTTPException
from pathlib import Path
import base64
import uuid
import httpx
from fastapi.staticfiles import StaticFiles

# Папка для хранения изображений
IMAGES_DIR = Path("static/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
# URL внешнего сервиса генерации изображений
GENERATOR_URL = "https://ai.katuscha.ssrv.su/sdapi/v1/txt2img"


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
                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.post(
                                GENERATOR_URL,
                                json={"prompt": "puppy dog", "steps": 50}  # 👈 тут исправил на `json=...`, не `data=...`
                            )
                            response.raise_for_status()
                    except Exception as e:
                        await websocket.send_json({
                            "status": "error",
                            "message": f"Ошибка при запросе к генератору: {e}"
                        })
                        return

                    data = response.json()
                    images_b64 = data.get("images", [])
                    if not images_b64:
                        await websocket.send_json({
                            "status": "error",
                            "message": "Пустой список изображений"
                        })
                        return

                    saved_urls = []

                    for image_b64 in images_b64:
                        filename = f"{uuid.uuid4().hex}.png"
                        filepath = IMAGES_DIR / filename

                        with open(filepath, "wb") as f:
                            f.write(base64.b64decode(image_b64))

                        image_url = f"/static/images/{filename}"
                        saved_urls.append(image_url)

                    # ✅ Отправляем результат обратно через WebSocket
                    await websocket.send_json({
                        "status": "success",
                        "image_urls": saved_urls
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
