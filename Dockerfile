FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY apps ./apps
COPY config ./config
COPY manage.py ./

RUN python -m pip install ".[dev]"

EXPOSE 8000 5678

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
