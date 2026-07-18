# reto-winter-2026-ithaka-backend

## Como levantar el proyecto local

```bash
python -m venv .venv
pip install -r requirements.txt
.venv\Scripts\activate
```

## Como correr el proyecto

```bash
uvicorn app.main:app --reload
```

## Como levantar el proyecto con Docker

```bash
docker compose up --build
```

## Docs

Swagger UI:
http://127.0.0.1:8000/docs
