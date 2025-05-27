FROM python:3.12

#RUN python3 -m pip install venv
COPY requirements.txt requirements.txt
RUN ls -la && sleep 5

#RUN python3 -m venv venv
#ENV VIRTUAL_ENV=/venv
RUN python3 -m pip install --upgrade pip && python3 -m pip install fastapi && python3 -m pip install -r requirements.txt
#RUN python3 main.py

WORKDIR "/api/"
#CMD ["python3", "main.py", "--help"]
#CMD ["/bin/bash"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
