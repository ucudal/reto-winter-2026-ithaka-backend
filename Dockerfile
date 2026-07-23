ARG PYTHON_VERSION=3.13

# ---------- Builder: compila wheels ----------
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# requirements primero => cache de capa: no re-compila wheels si solo cambia el código.
COPY requirements.txt ./

RUN python -m pip install --upgrade pip setuptools wheel && \
    pip wheel --wheel-dir /wheels -r requirements.txt

# ---------- Runtime: imagen de presentación ----------
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

# Instalar SOLO desde los wheels precompilados, sin ir a la red.
COPY requirements.txt ./
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels requirements.txt

# Copiar el código: queda /app/app/main.py => `app.main:app` resuelve (cwd /app en sys.path).
COPY --chown=appuser:appgroup app ./app

# Copiar migraciones Alembic
COPY --chown=appuser:appgroup alembic ./alembic
COPY --chown=appuser:appgroup alembic.ini .

USER appuser

EXPOSE 8000

# La imagen slim no trae curl/wget; usamos Python (ya está) para el healthcheck a "/".
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/').status == 200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
