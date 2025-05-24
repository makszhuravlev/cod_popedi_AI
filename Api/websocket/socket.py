import json
from fastapi import WebSocket, WebSocketDisconnect
from auth.utils import verify_token
from database import get_db
from models.user import User, Request, GeneratedFile
from schemas.user import FileType
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pathlib import Path
import base64
import uuid
import httpx
from datetime import datetime

IMAGES_DIR = Path("static/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
GENERATOR_URL = "https://ai.katuscha.ssrv.su/sdapi/v1/txt2img"

async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    user_login = verify_token(token)

    if user_login is None:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    await websocket.send_text(f"🔐 Welcome, {user_login}!")

    db: Session = next(get_db())
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                action = message.get("action")
                text_content = message.get("text")  # Текст теперь обязателен для всех действий
                
                if not text_content:
                    await websocket.send_json({
                        "status": "error",
                        "message": "Текст сообщения обязателен"
                    })
                    continue
                
                user = db.query(User).filter(User.login == user_login).first()
                if not user:
                    await websocket.send_json({
                        "status": "error",
                        "message": "Пользователь не найден"
                    })
                    continue
                
                # Пытаемся найти существующую заявку с таким текстом
                request = db.query(Request).filter(
                    Request.user_id == user.id,
                    Request.text == text_content
                ).first()
                
                # Если заявки нет - создаем новую
                if not request:
                    try:
                        request = Request(
                            user_id=user.id,
                            text=text_content,
                            status="pending"
                        )
                        db.add(request)
                        db.commit()
                        db.refresh(request)
                        await websocket.send_json({
                            "status": "info",
                            "message": "Создана новая заявка",
                            "request_text": text_content
                        })
                    except IntegrityError:
                        db.rollback()
                        request = db.query(Request).filter(
                            Request.user_id == user.id,
                            Request.text == text_content
                        ).first()
                
                # Обработка разных типов действий
                if action == "text":
                    await websocket.send_json({
                        "status": "success",
                        "message": "Текст сохранен в заявке",
                        "request_text": request.text
                    })
                
                elif action == "image":
                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.post(
                                GENERATOR_URL,
                                json={"prompt": text_content, "steps": 50}  # Используем текст как prompt
                            )
                            response.raise_for_status()
                    except Exception as e:
                        await websocket.send_json({
                            "status": "error",
                            "message": f"Ошибка при генерации изображения: {e}"
                        })
                        continue

                    data = response.json()
                    images_b64 = data.get("images", [])
                    if not images_b64:
                        await websocket.send_json({
                            "status": "error",
                            "message": "Не удалось сгенерировать изображения"
                        })
                        continue
                    
                    image_urls = []
                    for image_b64 in images_b64:
                        filename = f"{uuid.uuid4().hex}.png"
                        filepath = IMAGES_DIR / filename

                        with open(filepath, "wb") as f:
                            f.write(base64.b64decode(image_b64))

                        image_url = f"/static/images/{filename}"
                        
                        # Сохраняем файл в заявку
                        new_file = GeneratedFile(
                            request_id=request.id,
                            file_url=image_url,
                            file_type=FileType.image
                        )
                        db.add(new_file)
                    
                    db.commit()
                    
                    await websocket.send_json({
                        "status": "success",
                        "message": "Изображения сгенерированы и сохранены",
                        "image_url": image_url,
                        "request_text": request.text
                    })
                
                elif action == "music":
                    # Генерация музыки (заглушка)
                    music_url = f"/static/music/{uuid.uuid4().hex}.mp3"
                    
                    # Сохраняем файл в заявку
                    new_file = GeneratedFile(
                        request_id=request.id,
                        file_url=music_url,
                        file_type=FileType.music
                    )
                    db.add(new_file)
                    db.commit()
                    
                    await websocket.send_json({
                        "status": "success",
                        "message": "Музыка сгенерирована (заглушка)",
                        "music_url": music_url,
                        "request_text": request.text
                    })
                
                elif action == "get_files":
                    # Получаем все файлы для этой заявки
                    files = db.query(GeneratedFile).filter(
                        GeneratedFile.request_id == request.id
                    ).all()
                    
                    await websocket.send_json({
                        "status": "success",
                        "files": [{
                            "url": file.file_url,
                            "type": file.file_type
                        } for file in files],
                        "request_text": request.text
                    })
                
                else:
                    await websocket.send_json({
                        "status": "error",
                        "message": "Неизвестное действие"
                    })
            
            except json.JSONDecodeError:
                await websocket.send_json({
                    "status": "error",
                    "message": "Неверный формат JSON"
                })
            except Exception as e:
                await websocket.send_json({
                    "status": "error",
                    "message": f"Ошибка сервера: {str(e)}"
                })
    
    except WebSocketDisconnect:
        print(f"{user_login} отключился")
    finally:
        db.close()