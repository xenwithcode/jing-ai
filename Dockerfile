FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS backend
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN groupadd -r jing && useradd -r -g jing -d /app -s /bin/false jing

COPY pyproject.toml uv.lock README.md ./
COPY jing/ ./jing/
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
RUN uv sync --frozen --no-dev --no-editable

COPY --from=frontend-builder /app/dist ./frontend/dist

RUN chown -R jing:jing /app

USER jing

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000
