# DevOps — Ithaka (CI/CD, Kubernetes, base de datos)

Referencia de cómo funciona la infra en producción y cómo operarla. Aplica a los dos repos:
`reto-winter-2026-ithaka-backend` y `reto-winter-2026-ithaka-frontend`.

---

## 1. Arquitectura en producción

Todo corre en el **cluster Kubernetes de la UCU**. Cada app en su namespace; ingress **APISIX**;
imágenes en **Azure Container Registry** (`crretoxmas2024.azurecr.io`); base de datos **externa**
(gestionada por la cátedra).

```
                                  INTERNET
                     ┌───────────────┴────────────────┐
        ithaka-frontend.reto-ucu.net       ithaka-backend.reto-ucu.net
                     ▼                                 ▼
                 APISIX  (ApisixRoute enruta cada dominio → su Service)
                     ▼                                 ▼
                 Service (ClusterIP)               Service (ClusterIP)
                     ▼                                 ▼
        Deployment ithaka-frontend        Deployment ithaka-backend
        └─ Pod nginx :8080 (SPA React)    ├─ initContainer: migrate (alembic upgrade head)
           HPA 1..2 · ConfigMap           ├─ Pod uvicorn :8000 (FastAPI)
                                          │  HPA 1..2 · ConfigMap · Secret
                                          └─ CronJob: ithaka-checkpoints (trimestral)
                                                       │ DATABASE_URL (Secret)
                                                       ▼
                                    PostgreSQL EXTERNO (cátedra)
                                    10.0.3.7:50003 / ithaka_db (usuario ithaka_app)
                                    (desde afuera: postgres.reto-ucu.net:50003)
```

**Flujo de un request**: el usuario abre el frontend → nginx sirve el SPA → el JS del navegador
llama a `ithaka-backend.reto-ucu.net` (URL horneada con `VITE_API_URL` en build-time) → el backend
valida CORS (dominio del front en su ConfigMap) y consulta la DB externa.

Recursos por app en `k8s/`: `namespace`, `deployment`, `service`, `apisixroute`, `configmap`,
`hpa`. El backend además: `secret` (gitignoreado), `cronjob`, `ci-rbac`.
Límites por pod: **250Mi RAM / 200m CPU** (el HPA necesita `requests.cpu`, ya definido).

---

## 2. Pipeline de CI/CD (GitHub Actions)

3 workflows por repo. Se disparan en **PR a `main`** y **push a `main`**.

`docker-build-prod.yml` — 4 jobs encadenados:
```
secret-scan ──► build-scan-push ──► deploy ──► (notify-failure si algo falla)
 gitleaks       build + Trivy        kubectl set image + rollout + Discord "deploy OK"
                + push a ACR (main)
```
| Job | Cuándo | Qué hace |
|---|---|---|
| secret-scan | PR y push | Gitleaks: falla si hay secretos commiteados |
| build-scan-push | PR y push | Build Docker + Trivy (HIGH/CRITICAL). Push a ACR **solo en push a main** (`:sha` + `:latest`) |
| deploy | **solo push a main** | Configura kubectl (token), `set image` a `:sha`, espera rollout (300s). Falla → `rollout undo`. OK → Discord |
| notify-failure | si algún job falla | Avisa a Discord con el/los job(s) que fallaron + link al run |

`sonarqube.yml` — análisis en PR/push a `main`. `notify-pr-opened.yml` — Discord al abrir PR.

**Deploy backend**: el `set image` actualiza **`backend` Y `migrate`** (misma imagen; si no, el
initContainer queda viejo). Frontend: solo `frontend`.

**Notificaciones Discord**: deploy nuevo ✅, PR abierto ✅, pipeline fallido (reporta el **job**, no
el step — límite de GitHub Actions).

---

## 3. Secrets y Variables de GitHub

Settings → Secrets and variables → Actions. Ojo con la pestaña: `secrets.*` en **Secrets**,
`vars.*` en **Variables** (si se cruzan, llegan vacíos → el step falla).

| Nombre | Tipo | Valor | Lo usa |
|---|---|---|---|
| `ACR_LOGIN_SERVER` | Variable | `crretoxmas2024.azurecr.io` | login + push ACR |
| `ACR_USERNAME` / `ACR_PASSWORD` | Secret | credenciales ACR | login ACR |
| `GITLEAKS_LICENSE` | Secret | key gratis de gitleaks.io (repo de org) | secret-scan |
| `KUBE_API_SERVER` | Secret | `https://kubernetes-main-node.reto-ucu.net` | deploy |
| `KUBE_TOKEN` | Secret | token del SA `ci-deployer` | deploy |
| `KUBE_CA_CERT` | Secret | **vacío** → usa `--insecure-skip-tls-verify` | deploy |
| `SONAR_TOKEN` | Secret | token del proyecto SonarQube | sonarqube |
| `SONAR_HOST_URL` | Variable | `https://sonarqube.reto-ucu.net` | sonarqube |
| `DISCORD_WEBHOOK` | Secret | webhook del canal | notificaciones |
| `VITE_API_URL` (frontend) | Variable | `https://ithaka-backend.reto-ucu.net` | build del front |

**La `DATABASE_URL` NO va en GitHub** — el CI habla con Kubernetes, no con la DB. La URL vive solo
en el Secret de k8s (`ithaka-backend-secrets`) que lee el pod.

---

## 4. Base de datos

- **Externa**, de la cátedra. Desde el cluster: **`10.0.3.7:50003`**. Desde afuera:
  `postgres.reto-ucu.net:50003`.
- Usuario propio de la app: **`ithaka_app`** / base **`ithaka_db`** (NO el admin `postgres`).
- La `DATABASE_URL` está en `k8s/secret.yaml` (gitignoreado). Plantilla: `k8s/secret.example.yaml`.

Conectarse desde tu máquina:
```bash
psql "postgresql://ithaka_app:<PASS>@postgres.reto-ucu.net:50003/ithaka_db"
```

### Migraciones (Alembic) — automáticas
El **initContainer `migrate`** corre `alembic upgrade head` en cada deploy, antes de arrancar la app.
No hay que correrlas a mano: mergeás a main → deploy → migraciones aplicadas.

Cómo cambiar una tabla (ver también el README del repo):
1. Cambiar el modelo en `app/core/models/`.
2. `alembic revision --autogenerate -m "descripcion"` (con la DB local corriendo).
3. Revisar el archivo generado, probar `alembic upgrade head` local.
4. Commitear modelo + migración juntos en el PR.

**Reglas**: nunca reescribir/borrar una migración ya aplicada en prod; nunca tocar
`alembic_version` a mano; la cadena `down_revision` debe ser lineal.

### Seeds (datos de ejemplo) — manuales, NUNCA en el CI
El seed (`app/core/db/seed.py`) carga datos de ejemplo. Se corre a mano dentro de un pod:
```bash
POD=$(kubectl get pods -n ithaka-backend -l app=ithaka-backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec "$POD" -n ithaka-backend -c backend -- python -m app.core.db.seed          # no toca si ya hay datos
kubectl exec "$POD" -n ithaka-backend -c backend -- python -m app.core.db.seed --force   # ⚠️ BORRA todo y repuebla
```
> **⚠️ `--force` borra TODA la base.** Antes de correrlo en prod, verificá que los datos sean solo
> de seed y no reales. El seed no es idempotente sin `--force`; conviene que el equipo agregue
> chequeos "si ya existe, no insertar".

---

## 5. CronJob (checkpoints trimestrales)

`k8s/cronjob.yaml` → `ithaka-checkpoints`. Corre `app/scripts/process_checkpoints.py`
periódicamente, reutilizando la imagen del backend + el Secret + el ConfigMap.
Schedule: **`0 6 1 1,4,7,10 *`** (día 1 de ene/abr/jul/oct, 06:00 UTC = 03:00 Uruguay).

```bash
kubectl apply -f k8s/cronjob.yaml                 # crear/actualizar (una vez, a mano)
kubectl get cronjob -n ithaka-backend             # ver estado / LAST SCHEDULE

# Probarlo YA sin esperar el schedule (crea un Job del cronjob):
kubectl create job -n ithaka-backend cp-test --from=cronjob/ithaka-checkpoints
kubectl logs -n ithaka-backend -l job-name=cp-test          # ver la ejecución
kubectl delete job cp-test -n ithaka-backend                # limpiar
```
> Requiere permiso RBAC sobre `batch` (`cronjobs` para crear el CronJob; `jobs` para probarlo con
> `create job`). Si el pod queda en `ContainerCreating` varios minutos, suele ser el **pull de la
> imagen esperando en cola** (no un error) — se destraba solo.
> **⚠️ El script no evita duplicados**: cada ejecución crea checkpoints nuevos para los grupos
> activos. No dispararlo de más hasta que el backend agregue un chequeo de existencia.

---

## 6. Comandos kubectl — operación

### Conectarse (bash; el cert del cluster es self-signed)
```bash
kubectl config set-cluster reto-ucu --server=https://kubernetes-main-node.reto-ucu.net --insecure-skip-tls-verify=true
kubectl config set-credentials ucu-user --token="<TOKEN_DEL_DOCENTE>"
kubectl config set-context ucu-context --cluster=reto-ucu --user=ucu-user
kubectl config use-context ucu-context
kubectl get pods -A          # smoke test
```
> El token del docente **expira**. Si ves "you must be logged in to the server", renovalo.

### Deploy manual (lo que el CI hace automático)
Login al ACR primero (`docker login crretoxmas2024.azurecr.io -u <U> -p <P>`).
**Buildear siempre `--platform linux/amd64`** (la Mac es ARM, el cluster amd64).
```bash
TAG=test-$(git rev-parse --short HEAD)
docker buildx build --platform linux/amd64 --target runtime \
  -t crretoxmas2024.azurecr.io/ithaka-backend:$TAG --push .
IMG=crretoxmas2024.azurecr.io/ithaka-backend:$TAG
kubectl set image deployment/ithaka-backend backend=$IMG migrate=$IMG -n ithaka-backend
kubectl rollout status deployment/ithaka-backend -n ithaka-backend --timeout=300s
# frontend: --build-arg VITE_API_URL=https://ithaka-backend.reto-ucu.net ; set image solo frontend=$IMG
```

### Verificar / diagnosticar
```bash
kubectl get pods -n ithaka-backend -o wide                 # estado (Running / ImagePull / CrashLoop)
kubectl describe pod -l app=ithaka-backend -n ithaka-backend | tail -30   # Events
kubectl logs -l app=ithaka-backend -n ithaka-backend -c backend --tail=50
kubectl logs -l app=ithaka-backend -n ithaka-backend -c migrate           # migraciones
kubectl get hpa -A                                          # TARGETS no debe ser <unknown>
curl -i https://ithaka-backend.reto-ucu.net/health          # 200 {"status":"ok"}
```

### Operar
```bash
kubectl rollout restart deployment/<name> -n <ns>     # reiniciar (toma secret/config nuevos)
kubectl rollout undo    deployment/<name> -n <ns>     # rollback
kubectl scale deployment/<name> --replicas=0 -n <ns>  # apagar / =1 prender
kubectl apply -f k8s/secret.yaml -n ithaka-backend    # actualizar el Secret (ej. tras rotar credencial)
```

### RBAC del CI (aplicar 1 vez; token para KUBE_TOKEN)
```bash
kubectl apply -f k8s/ci-rbac.yaml
kubectl create token ci-deployer -n ithaka-backend --duration=8760h   # -> secret KUBE_TOKEN
```

---

## 7. Troubleshooting (problemas reales que ya pasaron)

| Síntoma | Causa | Solución |
|---|---|---|
| Login → **404** | Imagen desplegada vieja, sin el router | Deployar la imagen actual (`set image`) |
| Deploy → **`Init:CrashLoopBackOff`**, `Can't locate revision X` | La DB tenía una migración vieja que el código ya no tiene (se reescribieron migraciones) | `UPDATE alembic_version` al head actual con SQL directo; **no reescribir migraciones aplicadas** |
| Login → **"Incorrect email or password"** con seed | El seed generó hash pbkdf2, el código verifica con bcrypt | Re-seed `--force` con la imagen que tiene bcrypt |
| Deploy job **timeout** aunque el pod queda sano | `--timeout` muy corto (pull + migrate + probes) | Subido a `300s` |
| Build → **`unauthorized → docker.io`** | `ACR_LOGIN_SERVER` (Variable) vacío → login cae a Docker Hub | Cargar la Variable en GitHub |
| Sonar → **`URI with undefined scheme`** | `SONAR_HOST_URL` vacío | Cargar la Variable (con `https://`) |
| Pull → **`no match for platform`** | Imagen buildeada en Mac (ARM) para cluster (amd64) | Rebuildear `--platform linux/amd64` |
| Pod → **`ImagePullBackOff` 401** | Falta el pull secret `acr-secret` en ese namespace | `kubectl create secret docker-registry acr-secret ...` (por namespace) |
| CronJob → **`forbidden: cannot ... cronjobs`** | RBAC sin permiso `batch` | Pedir al docente permisos de `cronjobs`+`jobs` en el namespace |

---

## 8. Reglas de oro
- **`VITE_API_URL` se hornea en build-time** → cambiar el dominio del back = rebuildear el front.
- **Buildear `--platform linux/amd64`** desde la Mac.
- **Tag por SHA, no `:latest`** (trazable, dispara rolling update).
- **Secrets nunca al repo**: `k8s/secret.yaml` gitignoreado; solo se commitea el `.example`.
- **Migraciones automáticas** (initContainer); **seeds manuales** (nunca `--force` en prod con datos reales).
- **Flujo git**: `feature/* → testing → main`. El deploy/sonar están atados a `main`.
