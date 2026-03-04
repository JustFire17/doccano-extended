#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}/docker"

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE="${ROOT_DIR}/.env"

if [[ -f "${ENV_FILE}" ]]; then
	docker-compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" up -d --build
else
	docker-compose -f "${COMPOSE_FILE}" up -d --build
fi