#!/usr/bin/env sh
# Compuerta de aceptación para staging o VPS. No imprime secretos ni cookies.
set -eu

base_url=${1:-${EV3_WEB_PUBLIC_URL:-}}
token=${EV3_WEB_OPERATIONS_TOKEN:-}
http_url=${EV3_WEB_HTTP_URL:-}

if [ -z "$base_url" ] || [ -z "$token" ]; then
    echo "Uso: EV3_WEB_OPERATIONS_TOKEN=... $0 https://simulador.ejemplo.edu.co" >&2
    exit 2
fi

base_url=${base_url%/}
if [ -z "$http_url" ]; then
    http_url="http://${base_url#https://}"
fi
http_url=${http_url%/}

if ! docker compose -f docker-compose.production.yml ps --status running | grep -q 'simulador-ev3'; then
    echo "La aplicación Web no figura como contenedor en ejecución." >&2
    exit 1
fi
if ! docker compose -f docker-compose.production.yml ps --status running | grep -q 'caddy'; then
    echo "El proxy Caddy no figura como contenedor en ejecución." >&2
    exit 1
fi
if docker compose -f docker-compose.production.yml port simulador-ev3 5050 >/dev/null 2>&1; then
    echo "El puerto 5050 no debe estar publicado por el servicio Web." >&2
    exit 1
fi

curl --fail --silent --show-error \
    -H "X-EV3-Operations-Token: $token" \
    "$base_url/healthz" >/dev/null
curl --fail --silent --show-error \
    -H "X-EV3-Operations-Token: $token" \
    -H "Accept: text/plain" \
    "$base_url/metrics?format=prometheus" >/dev/null

redirect_code=$(curl --silent --output /dev/null --write-out '%{http_code}' "$http_url/")
case "$redirect_code" in
    301|302|307|308) ;;
    *)
        echo "HTTP no redirigió a HTTPS; código recibido: $redirect_code" >&2
        exit 1
        ;;
esac

header_file=$(mktemp)
body_file=$(mktemp)
trap 'rm -f "$header_file" "$body_file"' EXIT HUP INT TERM
create_code=$(curl --silent --show-error --output "$body_file" --dump-header "$header_file" \
    --write-out '%{http_code}' --request POST --header 'Content-Type: application/json' \
    --data '{}' "$base_url/api/sessions")
if [ "$create_code" != "201" ]; then
    echo "No se pudo crear la sesión de comprobación; código: $create_code" >&2
    exit 1
fi
if ! grep -qi 'Secure' "$header_file" || ! grep -qi 'HttpOnly' "$header_file" || ! grep -qi 'SameSite=Lax' "$header_file"; then
    echo "La cookie de sesión no conserva las banderas de seguridad requeridas." >&2
    exit 1
fi

session_data=$(python3 - "$body_file" <<'PY'
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
print(payload["session_id"])
print(payload["owner_token"])
PY
)
session_id=$(printf '%s\n' "$session_data" | sed -n '1p')
owner_token=$(printf '%s\n' "$session_data" | sed -n '2p')
close_code=$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' \
    --request DELETE --header "X-Session-Token: $owner_token" \
    "$base_url/api/sessions/$session_id")
if [ "$close_code" != "200" ]; then
    echo "No se pudo cerrar la sesión de comprobación; código: $close_code" >&2
    exit 1
fi

printf '%s\n' "Compuerta VPS aprobada: HTTPS, redirección, cookies, salud, métricas y red interna."
