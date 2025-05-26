import os.path
import asyncio
import uuid

from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from starlette.responses import FileResponse, JSONResponse

from .models import *
from .services.ai_service import AiService


ai_service = AiService(model_name="facebook/musicgen-stereo-small", models_dir="./models/")

results = {}
queue = asyncio.Queue()
loop = None

# Обработка очереди
async def queue_worker(loop, executor):
    while True:
        request_id, prompt = await queue.get()
        output_path = f"out/result_{request_id}.mp3"

        if ai_service.is_busy:
            return

        try:
            print(f"[Queue Worker {request_id}] Started generation...")

            await loop.run_in_executor(
                executor,
                ai_service.generate,
                prompt, output_path
            )

            results[request_id] = output_path
            print(f"[Queue Worker {request_id}] Success generated!")

        except Exception as e:
            ai_service.is_busy = False
            results[request_id] = None
            print(f"[Queue Worker {request_id}] Generation Error: {e}")

        queue.task_done()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global loop
    print("[App] Starting...")

    print("[App] Check and Clear \"out\" folder...")
    os.makedirs("out", exist_ok=True)
    for file in os.listdir("out"):
        os.remove(os.path.join("out", file))

    print("[App] Run queue worker...")
    executor = ThreadPoolExecutor(max_workers=1)
    loop = asyncio.get_running_loop()
    asyncio.create_task(queue_worker(loop, executor))

    print("[App] Setup ai service...")
    ai_service.setup()

    print("[App] Ready!")

    yield

    print("[App] Shutting down...!")

app = FastAPI(
    title="Катюша, уроки музыки", description="Сервис \"Катюши\" по генерации музыки", version="1.2.0",
    summary="Adeptus Altusches Team",
    lifespan=lifespan
)

@app.post("/generate", responses={
    201: {"content": {"audio/mp3": {}}},
    404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}
})
async def generate(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Генерация небольшого аудио файла
    """

    request_id = str(uuid.uuid4())
    print(f"[Queue Worker {request_id}] Added to Queue")
    await queue.put((request_id, request.prompt))

    while request_id not in results:
        await asyncio.sleep(1)

    output_path = results.pop(request_id)
    if output_path and os.path.exists(output_path):
        return FileResponse(output_path, status_code=201, media_type="audio/mpeg", filename="result.mp3")

    return JSONResponse(status_code=422, content={"title": "Ошибка генерации",
                                                  "message": "Файл с результатом генерации не найден"})

@app.get("/", responses={404: {"model": ErrorResponse}})
async def nope():
    """
    Что ты тут забыл?
    """
    return JSONResponse(status_code=404, content={"title": "Ты думаешь что всё так просто?",
                                                  "message": "Нет, тебе точно не сюда! Здесь закрытая репетиция!"})
