# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.14

FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY requirements.txt ./

RUN python -m pip install --upgrade pip setuptools wheel && \
    mkdir -p /wheels/runtime /wheels/dev && \
    pip wheel --wheel-dir /wheels/runtime -r requirements.txt

FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

COPY requirements.txt ./
COPY --from=builder /wheels/runtime /wheels/runtime

RUN pip install --no-index --find-links=/wheels/runtime -r requirements.txt && \
    rm -rf /wheels

COPY --chown=appuser:appgroup . .

RUN chmod +x scripts/entrypoint.sh scripts/smoke_test.sh

USER appuser

EXPOSE 8000

ENTRYPOINT ["./scripts/entrypoint.sh"]
CMD ["uvicorn", "ithaka_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM runtime AS development

USER root

COPY requirements-dev.txt ./
COPY --from=builder /wheels/dev /wheels/dev

RUN pip install --no-index \
    --find-links=/wheels/dev \
    --find-links=/wheels/runtime \
    -r requirements-dev.txt && \
    rm -rf /wheels

USER appuser
