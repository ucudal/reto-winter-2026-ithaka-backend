# reto-winter-2026-ithaka-backend

API del proyecto Ithaka, hecha con **FastAPI** (Python). Esta guía es para todo el
equipo: explica cómo levantar el proyecto, cómo crear endpoints y cómo funciona el
pipeline de CI/CD. No necesitás saber de DevOps.

Endpoints que existen hoy:

- `GET /health` → `{"status": "ok"}` (chequeo de salud).
- `GET /docs` → documentación interactiva (Swagger UI).

La app usa **PostgreSQL** con **SQLAlchemy** (ORM) y **Alembic** (migraciones). Para cambiar
tablas, ver la sección [Cómo cambiar tablas (migraciones)](#2-cómo-cambiar-tablas-migraciones).

---

## 1. Desarrollo local (sin Docker)

Es la forma más cómoda para programar día a día, con recarga automática.

1. **Entorno virtual e instalación de dependencias**:

```bash
python -m venv .venv
source .venv/bin/activate      # Mac / Linux
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
cp .env.example .env            # completar los valores
```

2. **Base de datos con Docker**:

```bash
docker compose up -d db         # levanta PostgreSQL local en background
```

3. **Aplicar las migraciones** (crea/actualiza las tablas):

```bash
alembic upgrade head
```

4. **Cargar datos de ejemplo (seeders)**:

```bash
python -m app.core.db.seed          # puebla la base (no hace nada si ya hay datos)
python -m app.core.db.seed --force  # ⚠️ BORRA todo y repuebla (solo en local)
```

5. **Iniciar el servidor de desarrollo**:

```bash
uvicorn app.main:app --reload       # http://127.0.0.1:8000/docs
```

---

## 2. Cómo cambiar tablas (migraciones)

**Regla de oro:** nunca cambies el schema de la base a mano. Todo cambio de tabla se hace con una
**migración de Alembic** versionada en git, que se aplica sola al deployar.

### Paso a paso para cambiar una tabla

1. **Cambiá el modelo** en `app/core/models/` (agregar/quitar columna, tabla nueva, etc.).

2. **Generá la migración** (con la base local corriendo — `docker compose up -d db`):

   ```bash
   alembic revision --autogenerate -m "add phone to users"
   ```

   Esto crea un archivo en `alembic/versions/` con `upgrade()` y `downgrade()`. **Abrilo y
   revisalo** — `--autogenerate` a veces se equivoca (no detecta renombres, defaults, etc.).

3. **Probala localmente**:

   ```bash
   alembic upgrade head     # aplica el cambio
   alembic downgrade -1     # opcional: verificá que el rollback también funciona
   alembic upgrade head
   ```

4. **Commiteá el modelo Y la migración juntos** en el mismo PR (así se revisan juntos).

### Qué pasa al mergear a `main`

El pipeline buildea la imagen (que incluye `alembic/versions/`) y, en el cluster, el **initContainer
`migrate`** corre `alembic upgrade head` **antes** de arrancar la app. Alembic aplica solo las
migraciones que falten. No hay que hacer nada manual: mergeás y el schema de prod se actualiza solo.

### ⚠️ Qué NO hacer (esto rompió prod una vez)

- **No reescribas ni borres una migración que ya se aplicó en prod.** Una migración aplicada es
  historia inmutable: si necesitás otro cambio, creá una migración **nueva** encima. (Consolidar/
  regenerar migraciones viejas hace que la base quede apuntando a una revisión que ya no existe →
  el deploy crashea con `Can't locate revision`.)
- **No cambies el formato de datos existentes sin migrarlos.** Ej: cambiar el algoritmo de hash de
  contraseñas deja los usuarios viejos sin poder loguearse. Si cambiás cómo se guardan datos, hay
  que migrar los datos existentes (o re-seedear en local).
- **No toques la tabla `alembic_version` a mano** salvo emergencia.
- **El seed NO es una migración.** `seed.py` carga datos de ejemplo (se corre manual); las
  migraciones son solo estructura. Nunca corras `seed.py --force` en producción con datos reales.

### Conflicto de "multiple heads"

Si dos ramas crean migraciones en paralelo desde la misma base, Alembic se queja de "multiple heads".
Se resuelve con `alembic merge heads -m "merge migrations"`, pero es mejor coordinar en el equipo
para que las migraciones salgan en cadena.

---

## 3. Levantar todo con Docker Compose

Para construir y levantar todos los servicios (API + Base de Datos):

```bash
docker compose up -d --build
```

---

## 4. Documentación API

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 5. Flujo de trabajo (Git)

Trabajamos con ramas `feature/*` → `testing` → `main`. El paso a paso completo está en
[CONTRIBUTING.md](CONTRIBUTING.md). En resumen: tu rama sale de `testing`, y tu PR
vuelve a `testing` (nunca directo a `main`).
