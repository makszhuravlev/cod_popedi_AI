import os.path
from fastapi import FastAPI, HTTPException

from pydantic import BaseModel
from starlette.responses import FileResponse, JSONResponse

app = FastAPI(
    title="Катюша, уроки музыки", description="Сервис \"Катюши\" по генерации музыки", version="0.1.0",
    summary="Adeptus Altusches Team"
)

class GenerateRequest(BaseModel):
    text: str

@app.post("/generate")
async def generate(request: GenerateRequest):

    # Пу-Пу-Пуууу

    if not os.path.exists("./out/result.mp3"):
        return JSONResponse(status_code=422, content={"message": "Ошибка генерации: файл с результатом генерации не найден"})

    return FileResponse(path='./out/result.mp3', filename='music.wav', media_type='multipart/form-data')

@app.get("/")
async def nope():
    return JSONResponse(status_code=404, content={"message": "Нет, тебе точно не сюда! Здесь закрытая репетиция!"})