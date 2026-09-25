#!/usr/bin/env sh
# Prepara directorios privados del VPS para la operación de BotLab Studio.
# Debe ejecutarse una vez como root antes del primer despliegue.
set -eu

storage_root=${1:-/srv/simulador-ev3}
service_owner=${EV3_VPS_SERVICE_OWNER:-${SUDO_USER:-}}

if [ -z "$service_owner" ]; then
    echo "Defina EV3_VPS_SERVICE_OWNER o ejecute mediante sudo desde el usuario de despliegue." >&2
    exit 2
fi

install -d -m 0750 -o "$service_owner" -g "$service_owner" "$storage_root"
install -d -m 0700 -o "$service_owner" -g "$service_owner" "$storage_root/backups"
install -d -m 0750 -o "$service_owner" -g "$service_owner" "$storage_root/logs"

printf '%s\n' "Almacenamiento privado preparado en $storage_root"
