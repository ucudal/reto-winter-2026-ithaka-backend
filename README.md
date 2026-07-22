# reto-winter-2026-ithaka-backend

## Configuración y Ejecución Local

1. **Entorno Virtual e Instalación de Dependencias**:
```bash
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
