FROM python:3.9
LABEL authors="Adeptus Altusches Team"

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip
RUN pip install --upgrade git+https://github.com/huggingface/transformers.git scipy
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

WORKDIR /code/app
RUN py app/setup_model.py  \
    --model "facebook/musicgen-stereo-small"  \
    --dir "./models/facebook/musicgen-stereo-small"  \
    --enable_download True  \
    --enable_testing False

WORKDIR /code
CMD ["fastapi", "run", "app/main.py", "--port", "80"]