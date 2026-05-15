#!/usr/bin/env bash
set -euo pipefail
docker compose pull || true
docker compose up -d --build
docker compose exec api alembic upgrade head
