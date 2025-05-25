import os.path
from contextlib import asynccontextmanager
from http.client import responses

from fastapi import FastAPI
from starlette.responses import FileResponse, JSONResponse

from .models import *
from .services.ai_service import AiService


ai_service = AiService(model_name="facebook/musicgen-stereo-small", models_dir="./models/")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[App] Starting...")
    ai_service.setup()
    print("[App] Ready!")

    yield

    print("[App] Shutting down...!")

app = FastAPI(
    title="Катюша, уроки музыки", description="Сервис \"Катюши\" по генерации музыки", version="0.2.1",
    summary="Adeptus Altusches Team",
    lifespan=lifespan
)

@app.post("/generate", responses={
    201: {"content": {"audio/mp3": {}}},
    404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}
})
async def generate(request: GenerateRequest):
    """
    Генерация небольшого аудио файла
    """
    if ai_service.is_busy:
        return JSONResponse(status_code=409, content={"title": "Ошибка очереди",
                                                      "message": "Генератор занят, повторите попытку позже"})

    ai_service.generate(request.text)

    if not os.path.exists("../out/result.mp3"):
        return JSONResponse(status_code=422, content={"title": "Ошибка генерации",
                                                      "message": "Файл с результатом генерации не найден"})

    return FileResponse(status_code=201, path='/out/result.mp3', filename='music.wav', media_type='')

@app.get("/", responses={404: {"model": ErrorResponse}})
async def nope():
    """
    Что ты тут забыл?
    """
    return JSONResponse(status_code=404, content={"title": "Ты думаешь что всё так просто?",
                                                  "message": "Нет, тебе точно не сюда! Здесь закрытая репетиция!"})