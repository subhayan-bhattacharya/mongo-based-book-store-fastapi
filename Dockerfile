FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN pip install poetry

COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false && poetry install

COPY . /app

WORKDIR /app

CMD uvicorn --host 0.0.0.0 application:app

