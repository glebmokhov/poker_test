FROM python:3.11-slim

WORKDIR /app

# копируем только pyproject (по-умолчанию) и установим poetry
COPY pyproject.toml /app/pyproject.toml

RUN pip install --upgrade pip && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY . /app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
