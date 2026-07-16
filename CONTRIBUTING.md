# Guía de contribución — Flujo de Git

## Ramas del repo
- `main` → versión estable, la que se muestra en la demo.
- `testing` → acá se prueban los cambios antes de pasar a `main`.
- `feature/...` → tu rama de trabajo diaria.

## Reglas de oro
1. Nunca se trabaja directo sobre `main` ni sobre `testing`.
2. Tu rama sale de `testing` (no de `main`) y tu PR vuelve a `testing`.
3. Todo cambio entra por **Pull Request (PR)**, con al menos 1 aprobación.
4. Solo se pasa `testing` → `main` cuando ya se probó que todo funciona bien.
5. Nunca `git push --force` sobre `main` ni `testing`.
6. Commits chicos y frecuentes, no uno gigante al final del día.

## El paso a paso (siempre en este orden)

```bash
# 1. Actualizate antes de arrancar
git checkout testing
git pull origin testing

# 2. Creá tu rama
git checkout -b feature/nombre-corto

# 3. Trabajá y commiteá seguido
git add .
git commit -m "agrega X"

# 4. Subí tu rama
git push origin feature/nombre-corto

# 5. Abrí el PR en GitHub → base: testing, pedí revisión, esperá aprobación

# 6. Mergeá con "Squash and merge" y borrá la rama

# 7. Volvé al paso 1 para tu próxima tarea
```

Cuando se prueba en `testing` y todo funciona bien, alguien del liderazgo abre el PR de `testing` → `main`.

## Nombres de rama
`feature/algo-nuevo` · `fix/arreglo-de-bug` · `chore/configuracion`

## Si hay conflicto y no sabés resolverlo
**Parate y preguntá en el canal.** No pruebes comandos al azar.

## Nunca subir al repo
`.env` con datos reales, `node_modules/`, `__pycache__/`, `venv/` (ya tienen que estar en `.gitignore`)
