import json
from fastapi import WebSocket, WebSocketDisconnect
from auth.utils import verify_token
from database import get_db
from models.user import User
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException
from pathlib import Path
import base64
import uuid
import httpx
from fastapi.staticfiles import StaticFiles

from models.user import Request

# Папка для хранения изображений
IMAGES_DIR = Path("static/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
# URL внешнего сервиса генерации изображений
GENERATOR_URL = "https://ai.katuscha.ssrv.su/sdapi/v1/txt2img"


async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    user_login = verify_token(token)

    if user_login is None:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    await websocket.send_text(f"🔐 Welcome, {user_login}!")

    # Получаем сессию базы данных
    db: Session = next(get_db())

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                action = message.get("action")

                if action == "text":
                    text_content = message.get("text")
                    if not text_content:
                        await websocket.send_json({
                            "status": "error",
                            "message": "Текст сообщения отсутствует"
                        })
                        continue

                    # Проверяем, существует ли уже заявка с таким текстом для этого пользователя
                    user = db.query(User).filter(User.login == user_login).first()
                    if not user:
                        await websocket.send_json({
                            "status": "error",
                            "message": "Пользователь не найден"
                        })
                        continue

                    # Здесь должна быть проверка уникальности текста для этого пользователя
                    # Предположим, у нас есть модель Request (заявка), которая хранит текст и user_id
                    existing_request = db.query(Request).filter(
                        Request.user_id == user.id,
                        Request.text == text_content
                    ).first()

                    if existing_request:
                        await websocket.send_json({
                            "status": "error",
                            "message": "Заявка с таким текстом уже существует"
                        })
                        continue

                    new_request = Request(
                        user_id=user.id,
                        text=text_content,
                        status="pending"
                    )
                    db.add(new_request)
                    db.commit()

                    await websocket.send_json({
                        "status": "success",
                        "message": "Заявка успешно создана",
                        "request_id": new_request.id
                    })

                elif action == "image":
                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.post(
                                GENERATOR_URL,
                                json={"prompt": "puppy dog", "steps": 50}
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

                    for image_b64 in images_b64:
                        filename = f"{uuid.uuid4().hex}.png"
                        filepath = IMAGES_DIR / filename

                        with open(filepath, "wb") as f:
                            f.write(base64.b64decode(image_b64))

                        image_url = f"/static/images/{filename}"

                    await websocket.send_json({
                        "status": "success",
                        "image_urls": image_url
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
        print(f"{user_login} disconnected")
    finally:
        db.close()