FROM python:3.12

COPY requirements.txt requirements.txt

RUN python3 -m venv venv
ENV VIRTUAL_ENV=/venv
RUN venv/bin/pip install --upgrade pip && venv/bin/pip install -r requirements.txt
#RUN python3 main.py

WORKDIR "/api/"
#CMD ["python3", "main.py", "--help"]
#CMD ["/bin/bash"]
CMD ["venv/bin/uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
