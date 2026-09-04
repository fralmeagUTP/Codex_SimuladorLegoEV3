#!/usr/bin/env sh
# Respalda únicamente artefactos versionados de despliegue; nunca secretos,
# sesiones, trazas ni temporales de workers.
set -eu

storage_root=${1:-/srv/simulador-ev3}
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
archive="$storage_root/backups/botlab-studio-deploy-$timestamp.tar.gz"

mkdir -p "$storage_root/backups"
umask 077
tar -czf "$archive" \
    docker-compose.production.yml \
    .env.production.example \
    deploy/Caddyfile.production \
    Documentos/REQUERIMIENTOS_HOSTING_Y_DESPLIEGUE_WEB.md \
    Documentos/OPERACION_VPS_WEB.md

printf '%s\n' "Respaldo no secreto creado: $archive"
