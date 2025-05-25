FROM python:3.9
LABEL authors="Adeptus Altusches Team"

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

# Ставим пакетики :>
RUN pip install --upgrade pip
RUN pip install --upgrade git+https://github.com/huggingface/transformers.git scipy
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# Инициализация ИИ моделей
# Выбрал musicgen-stereo-small т.к. она самая быстрая
RUN py app/setup_model.py  \
    --model "facebook/musicgen-stereo-small"  \
    --dir "./models/facebook/musicgen-stereo-small"  \
    --enable_download True  \
    --enable_testing False

WORKDIR /code

# ВОТ ТУТ ВАЖНО ЧТОБ БЫЛ 1 ВОРКЕР
# Если конечно у вас не серверная AI видиокарта :D
CMD ["fastapi", "run", "app/main.py", "--port", "80", "--workers", "1"]
