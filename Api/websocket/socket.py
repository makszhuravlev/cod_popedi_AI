import json
from schemas.user import FileType
from fastapi import WebSocket, WebSocketDisconnect
from auth.utils import verify_token
from database import get_db
from models.user import User, Request, GeneratedFile
from sqlalchemy.orm import Session
from pathlib import Path
import base64
import uuid
import httpx
from typing import Dict, List
import random
import asyncio


IMAGES_DIR = Path("static/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
GENERATOR_IMG_URL = "http://10.0.8.15/sdapi/v1/txt2img"
GENERATOR_TEXT_URL = "http://10.0.8.15:11434/api/generate"

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

                if action == "get_history":
                    # Получаем все заявки пользователя
                    user = db.query(User).filter(User.login == user_login).first()
                    if not user:
                        await websocket.send_json({
                            "status": "error",
                            "message": "User not found"
                        })
                        continue

                    requests = db.query(Request).filter(
                        Request.user_id == user.id
                    ).order_by(Request.id.desc()).all()

                    response = {"requests": []}

                    for req in requests:
                        files = db.query(GeneratedFile).filter(
                            GeneratedFile.request_id == req.id
                        ).all()

                        request_data = {
                            "id": req.id,
                            "reference_text": req.text,
                            "texts": [],
                            "images": [],
                            "music": [],
                            "gifts": []
                        }

                        for file in files:
                            if file.file_type == "text":
                                request_data["texts"].append(file.file_url)
                            elif file.file_type == "image":
                                request_data["images"].append(file.file_url)
                            elif file.file_type == "music":
                                request_data["music"].append(file.file_url)
                            elif file.file_type == "gift":
                                request_data["gifts"].append(file.file_url)

                        response["requests"].append(request_data)

                    await websocket.send_json({
                        "status": "success",
                        "data": response
                    })

                elif action == "get_request":
                    request_id = message.get("request_id")
                    if not request_id:
                        await websocket.send_json({
                            "status": "error",
                            "message": "Request ID is required"
                        })
                        continue

                    request = db.query(Request).filter(
                        Request.id == request_id,
                        Request.user_id == db.query(User.id).filter(User.login == user_login).scalar_subquery()
                    ).first()

                    if not request:
                        await websocket.send_json({
                            "status": "error",
                            "message": "Request not found"
                        })
                        continue

                    files = db.query(GeneratedFile).filter(
                        GeneratedFile.request_id == request.id
                    ).all()

                    request_data = {
                        "id": request.id,
                        "reference_text": request.text,
                        "texts": [],
                        "images": [],
                        "music": [],
                        "gifts": []
                    }

                    for file in files:
                        if file.file_type == "text":
                            request_data["texts"].append(file.file_url)
                        elif file.file_type == "image":
                            request_data["images"].append(file.file_url)
                        elif file.file_type == "music":
                            request_data["music"].append(file.file_url)
                        elif file.file_type == "gift":
                            request_data["gifts"].append(file.file_url)

                    await websocket.send_json({
                        "status": "success",
                        "data": {"requests": [request_data]}
                    })

                elif action == "text":
                    input_text = message.get("text")

                    # Получаем пользователя
                    user = db.query(User).filter(User.login == user_login).first()
                    if not user:
                        await websocket.send_json({
                            "status": "error",
                            "message": "Пользователь не найден"
                        })
                        continue

                    # Проверяем, существует ли такая заявка у пользователя
                    existing_request = db.query(Request).filter_by(user_id=user.id, text=input_text).first()

                    if existing_request:
                        request = existing_request
                    else:
                        request = Request(user_id=user.id, text=input_text)
                        db.add(request)
                        db.commit()
                        db.refresh(request)

                    current_request_id = request.id

                    # Генерация текста
                    try:
                        raw_json = json.dumps({
                            "model": "cnshenyang/qwen3-nothink:14b",
                            "prompt": f"Я сейчас передам тебе текст введённый пользователем. Ты должен вывести стилистический текст в виде письма военнослужащего/военнослужащей. Соблюдай мораль и старайся соблюсти полную стилисту Великой Отечественной войны. Не пиши от лица немцев. Пиши от лица советских солдат. {input_text}. ОГРАНИЧЕНИЕ ПО сиволам в 200 симвовлов",
                            "stream": False
                        })

                        headers = {"Content-Type": "application/json"}

                        async with httpx.AsyncClient() as client:
                            response = await client.post(GENERATOR_TEXT_URL, content=raw_json, headers=headers, timeout=300)
                            response.raise_for_status()
                            data = response.json()

                        # Сохраняем сгенерированный текст
                        generated_text = data.get("response")
                        file = GeneratedFile(
                            request_id=request.id,
                            file_url=generated_text,  # можно сохранять как текст в file_url, если нет URL
                            file_type=FileType.text
                        )
                        db.add(file)
                        db.commit()

                        await websocket.send_json({
                            "status": "success",
                            "message": "Текст сгенерирован и сохранён в заявке",
                            "request_text": generated_text
                        })

                    except Exception as e:
                        await websocket.send_json({
                            "status": "error",
                            "message": f"Ошибка при генерации текста: {e}"
                        })
                        continue

                elif action == "image":
                    try:
                        input_text = message.get("text")
                        user = db.query(User).filter(User.login == user_login).first()
                        if not user:
                            await websocket.send_json({
                                "status": "error",
                                "message": "Пользователь не найден"
                            })
                            continue

                        # Проверяем, существует ли такая заявка у пользователя
                        existing_request = db.query(Request).filter_by(user_id=user.id, text=input_text).first()

                        if existing_request:
                            request = existing_request
                        else:
                            request = Request(user_id=user.id, text=input_text)
                            db.add(request)
                            db.commit()
                            db.refresh(request)

                        current_request_id = request.id
                        raw_json = '''
                        {
                        "model": "cnshenyang/qwen3-nothink:14b",
                        "prompt": "Я сейчас передам тебе текст введённый пользователем. Ты должен вывести пропт для stable-diffusion для генерации изображения по тексту Не используй кавычки в своем ответе и другого текста не относящегося к промпту. Соблюдай мораль и старайся соблюсти полную стилисту Великой Отечественной войны. Не пиши от лица немцев. Пиши от лица советских солдат: '''+ message.get("text") +'''",
                        "stream": false
                        }
                        '''.strip()

                        headers = {
                            "Content-Type": "application/json"
                        }
                        async with httpx.AsyncClient() as client:
                                response = await client.post(
                                GENERATOR_TEXT_URL,
                                content=raw_json,
                                headers=headers,
                                timeout=300
                            )
                                data = response.json()

                                response.raise_for_status()
                        prompt = data.get("response")
                        print(prompt)


                        async with httpx.AsyncClient() as client:
                            response = await client.post(
                                GENERATOR_IMG_URL,
                                json={"prompt": prompt, "steps": 150},  # Используем текст как prompt
                                timeout=30
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
                        "image_url": image_url
                    })

                elif action == "music":

                    # Генерация музыки (заглушка)
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            GENERATOR_IMG_URL,
                            json={"prompt": "Congratulations"},
                            timeout=300
                        )
                        response.raise_for_status()

                        # Просто сохраняем бинарный контент
                        filename = f"{uuid.uuid4().hex}.mp3"
                        with open(filename, "wb") as f:
                            f.write(response.content)

                        print(f"Аудиофайл сохранён как {filename}")

                    new_file = GeneratedFile(
                        request_id=request.id,
                        file_url=music_url,
                        file_type=FileType.music
                    )
                    db.add(new_file)
                    db.commit()

                    # await websocket.send_json({
                    #     "status": "success",
                    #     "message": "Музыка сгенерирована (заглушка)",
                    #     "music_url": music_url,
                    #     "request_text": request.text
                    # })
                    try:
                        delay = random.randint(5, 10)
                        await asyncio.sleep(delay)

                        music_url = random.choice(MUSIC_PLACEHOLDER_URLS)

                        # Сохраняем файл в заявку
                        new_file = GeneratedFile(
                            request_id=1,
                            file_url=music_url,
                            file_type=FileType.music
                        )
                        db.add(new_file)
                        db.commit()

                        await websocket.send_json({
                            "status": "success",
                            "message": f"Музыка сгенерирована за {delay} секунд",
                            "music_url": music_url,
                        })
                    except Exception as e:
                        await websocket.send_json({
                            "status": "error",
                            "message": f"Ошибка при генерации музыки: {e}"
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
