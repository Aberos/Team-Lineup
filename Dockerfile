FROM node:22-slim AS frontend

ARG APP_PREFIX=""

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN APP_PREFIX="${APP_PREFIX}" npm run build

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && git config --system --add safe.directory /app

COPY --from=frontend /usr/local/bin/node /usr/local/bin/node
COPY --from=frontend /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

COPY pyproject.toml README.md ./
COPY apps ./apps
COPY config ./config
COPY manage.py ./

RUN python -m pip install ".[dev]"

COPY --from=frontend /frontend/dist ./frontend/dist

RUN DJANGO_SECRET_KEY=collectstatic-build-only \
    python manage.py collectstatic --noinput

EXPOSE 8000 5678

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
