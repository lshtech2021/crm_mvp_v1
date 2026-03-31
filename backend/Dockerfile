# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY pyproject.toml ./

# ---------------------------------------------------------------------------
# Development target – includes dev dependencies and hot-reload
# ---------------------------------------------------------------------------
FROM base AS development

RUN pip install --no-cache-dir -e ".[dev]"

COPY . .

USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---------------------------------------------------------------------------
# Production target – minimal image
# ---------------------------------------------------------------------------
FROM base AS production

RUN pip install --no-cache-dir .

COPY . .

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
