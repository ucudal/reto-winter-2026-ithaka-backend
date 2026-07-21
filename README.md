# reto-winter-2026-ithaka-backend

API del proyecto Ithaka, hecha con **FastAPI** (Python). Esta guía es para todo el
equipo: explica cómo levantar el proyecto, cómo crear endpoints y cómo funciona el
pipeline de CI/CD. No necesitás saber de DevOps.

Endpoints que existen hoy:

- `GET /health` → `{"status": "ok"}` (chequeo de salud).
- `GET /docs` → documentación interactiva (Swagger UI).

> Todavía **no hay base de datos** (ver la sección [Base de datos / tablas](#base-de-datos--tablas)).

---

## 1. Desarrollo local (sin Docker)

Es la forma más cómoda para programar día a día, con recarga automática.

1. **Entorno Virtual e Instalación de Dependencias**:

```bash
# 1. Crear el entorno virtual
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. **Base de Datos con Docker**:

```bash
# Levantar el servicio de PostgreSQL en background
docker compose up -d db
```

3. **Migraciones de Base de Datos (Alembic)**:

```bash
alembic upgrade head
```

4. **Ejecutar Seeders (Datos iniciales)**:

```bash
# Poblar la base de datos (omite si ya existen datos)
python seed.py

# Forzar limpieza y repoblación completa
python seed.py --force
```

5. **Iniciar Servidor de Desarrollo**:

```bash
uvicorn app.main:app --reload
```

---

## Levantar todo con Docker Compose

Para construir y levantar todos los servicios (API + Base de Datos):

```bash
docker compose up -d --build
```

---

## Documentación API

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 7. Flujo de trabajo (Git)

Trabajamos con ramas `feature/*` → `testing` → `main`. El paso a paso completo está en
[CONTRIBUTING.md](CONTRIBUTING.md). En resumen: tu rama sale de `testing`, y tu PR
vuelve a `testing` (nunca directo a `main`).
