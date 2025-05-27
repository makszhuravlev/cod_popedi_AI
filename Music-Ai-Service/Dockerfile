FROM python:3.9
LABEL authors="Adeptus Altusches Team"

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

# Ставим пакетики :>
RUN pip install --upgrade pip
RUN pip install --upgrade git+https://github.com/huggingface/transformers.git scipy
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install fastapi[uvicorn] uvicorn

RUN mkdir /code/models
RUN mkdir /code/out

COPY ./app /code/app
COPY ./setup_model.py /code

# Инициализация ИИ моделей
# Выбрал musicgen-stereo-small т.к. она самая быстрая
RUN python3 setup_model.py  \
    --model "facebook/musicgen-stereo-small"  \
    --dir "./models/facebook/musicgen-stereo-small"  \
    --enable-download True

WORKDIR /code

# ВОТ ТУТ ВАЖНО ЧТОБ БЫЛ 1 ВОРКЕР
# Если конечно у вас не серверная AI видиокарта :D
CMD ["uvicorn", "app.main:app", "--port", "3000", "--host", "0.0.0.0",  "--workers", "1"]
