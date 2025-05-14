from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
import json
import os
import hashlib
import binascii
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Конфигурация БД
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost/asd")

async def get_db_conn():
    return await asyncpg.connect(DATABASE_URL)
def verify_password(stored_hash: str, password: str) -> bool:
    try:
        salt_hex, stored_hash_hex = stored_hash.split(':')
        salt = binascii.unhexlify(salt_hex)
        stored_hash = binascii.unhexlify(stored_hash_hex)

        dk = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            600000,
            dklen=32
        )
        return dk == stored_hash
        
    except (ValueError, binascii.Error):
        return False
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                action = message.get("action")
                if action == "register":
                        conn = await get_db_conn()
                        try:
                            client_hashed_password = message["password"]
                            
                            if len(client_hashed_password.split(':')) != 2:
                                raise ValueError("Invalid hash format")
                                
                            await conn.execute('''
                                INSERT INTO users (email, login, password_hash)
                                VALUES ($1, $2, $3)
                            ''', message["email"], message["login"], client_hashed_password)
                            
                            await websocket.send_json({
                                "status": "success",
                                "message": "Пользователь зарегестрирован"
                            })
                        except asyncpg.UniqueViolationError:
                            await websocket.send_json({
                                "status": "error",
                                "message": "Такой пользователь уже есть"
                            })
                        except ValueError as e:
                            await websocket.send_json({
                                "status": "error",
                                "message": str(e)
                            })
                elif action == "login":
                        conn = await get_db_conn()
                        user = await conn.fetchrow(
                            'SELECT * FROM users WHERE email = $1', 
                            message["email"]
                        )
                        if not user:
                            await websocket.send_json({
                                "status": "error",
                                "message": "Пользователь не найден"
                            })
                        else:
                            is_valid = verify_password(
                                user["password_hash"],
                                message["password"]
                            )
                            
                            if is_valid:
                                await websocket.send_json({
                                    "status": "success",
                                    "user": {
                                        "id": user["id"],
                                        "email": user["email"],
                                        "login": user["login"]
                                    }
                                })
                            else:
                                await websocket.send_json({
                                    "status": "error",
                                    "message": "Неверный пароль"
                                })
                elif action == "text":
                    await websocket.send_json({
                                "status": "success",
                                "message": "E"
                            })
                    print('Ништяк1')
                elif action == "image":
                    await websocket.send_json({
                                "status": "success",
                                "message": "E"
                            })
                    print('Ништяк2')
                elif action == "music":
                    await websocket.send_json({
                                "status": "success",
                                "message": "E"
                            })
                    print('Ништяк3')
                elif action == "all":
                    await websocket.send_json({
                                "status": "success",
                                "message": "E"
                            })
                    print('Ништяк4')
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
        print("Client disconnected")