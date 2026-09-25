#!/usr/bin/env sh
# Comprueba disponibilidad y métricas sin imprimir el token operativo.
set -eu

base_url=${1:-${EV3_WEB_PUBLIC_URL:-}}
token=${EV3_WEB_OPERATIONS_TOKEN:-}

if [ -z "$base_url" ] || [ -z "$token" ]; then
    echo "Uso: EV3_WEB_OPERATIONS_TOKEN=... $0 https://simulador.ejemplo.edu.co" >&2
    exit 2
fi

base_url=${base_url%/}
curl --fail --silent --show-error \
    -H "X-EV3-Operations-Token: $token" \
    "$base_url/healthz" >/dev/null
curl --fail --silent --show-error \
    -H "X-EV3-Operations-Token: $token" \
    -H "Accept: text/plain" \
    "$base_url/metrics?format=prometheus" >/dev/null

printf '%s\n' "BotLab Studio Web: salud y métricas disponibles."
