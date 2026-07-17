#!/bin/sh
set -eu

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  python scripts/migration_cli.py upgrade head
fi

exec "$@"
