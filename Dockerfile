# syntax=docker/dockerfile:1

# --- build stage: resolve dependencies with uv ---
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-install-project

# --- runtime stage ---
FROM python:3.14-slim-bookworm

RUN useradd --create-home --uid 1000 app \
    && install -d -o app -g app /app/rpi-homepage /app/rpi-homepage/cache

WORKDIR /app/rpi-homepage

COPY --from=builder /app/.venv /app/.venv
COPY --chown=app:app rpi-homepage/ /app/rpi-homepage/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER app

EXPOSE 1234

CMD ["python", "rpi-homepage.py"]
