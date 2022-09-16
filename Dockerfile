FROM python:3

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN pip install poetry
RUN poetry install

COPY . .

CMD ["poetry", "run", "uvicorn", "web_app:app"]
