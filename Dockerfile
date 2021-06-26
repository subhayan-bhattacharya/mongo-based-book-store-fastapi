FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY . /app

WORKDIR /app

RUN pip install -r ./requirements/requirements.txt

CMD uvicorn --host 0.0.0.0 application:app --reload

