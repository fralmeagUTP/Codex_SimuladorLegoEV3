# Reporte de staging local del perfil VPS Web

Fecha: 2026-09-03, hora local Colombia.  
Alcance: validación local reproducible del perfil Docker/Caddy antes de contar
con el VPS KVM real. No se usaron dominio, credenciales ni secretos de
producción.

## Configuración ejercida

- `docker-compose.production.yml` con Caddy y aplicación en red interna.
- Host local `localhost`; puertos no conflictivos `8080` y `8443`.
- Secretos locales desechables, eliminados al finalizar.
- Perfil de aplicación: 20 sesiones, 4 simulaciones, 120 s y 8 hilos.
- Caddy emitió un certificado local; la consulta HTTPS se realizó aceptándolo
  solo para esta prueba local.

## Resultado

| Comprobación | Resultado |
| --- | --- |
| Construcción de imagen `simulador-ev3:production` | PASS |
| Contenedor Web no publicado directamente | PASS: solo `5050/tcp` en red interna |
| Caddy publicado | PASS: `8080 -> 80`, `8443 -> 443` |
| `GET /healthz` vía HTTPS y token operativo | PASS: `200 OK` |
| Métricas Prometheus vía HTTPS y token | PASS: `200 OK` |
| Redirección HTTP | PASS: `308` a HTTPS |
| Cookie de sesión | PASS: `Secure`, `HttpOnly`, `SameSite=Lax` |
| Cierre autorizado de sesión | PASS: `200 OK` |
| Cabeceras | PASS: CSP, HSTS, `nosniff`, `DENY` y `Referrer-Policy` |
| Memoria inicial de Web | 44.13 MiB de límite 768 MiB |
| PIDs iniciales de Web | 11 de límite 64 |
| Limpieza | PASS: `docker compose down -v` y secreto temporal eliminados |

## Conclusión y límite de la evidencia

El empaquetado, la red interna, el proxy TLS, cookies, endpoints operativos y
apagado limpio funcionan en el entorno local. Esta evidencia no mide la CPU,
red, certificado público, DNS, firewall, SSE bajo carga o reversión de versión
en un VPS 2 vCPU/8 GB. Esos puntos siguen siendo una compuerta de aceptación
obligatoria antes de liberar la URL pública.

## Complemento: perímetro y sesiones en VPS real

Se realizó una comprobación posterior contra la URL pública del VPS, sin
registrar secretos ni tokens operativos.

| Comprobación | Resultado |
| --- | --- |
| Aplicación disponible mediante HTTPS | PASS: `200 OK` |
| Puerto directo de la aplicación | PASS: dejó de aceptar conexiones públicas tras recrear el servicio detrás de Traefik |
| Creación y carga de scripts en una sola IP de prueba | PASS: 12 sesiones creadas y actualizadas |
| Separación entre sesiones | PASS: una petición cruzada recibió `403` |
| Limpieza de sesiones creadas | PASS: 12 de 12 cerradas |
| Protección contra creación masiva desde una IP | PASS: 8 solicitudes adicionales y una de desborde recibieron `429` |

La prueba confirma que el límite de 12 creaciones por minuto y por dirección
cliente se aplica antes del límite global de 20 sesiones. Para validar 20
usuarios reales se requiere una campaña distribuida desde varias direcciones
de cliente autorizadas, o esperar entre ventanas de limitación. Siguen
pendientes una campaña distribuida de 20 clientes y una reversión de versión
que no vuelva a publicar el puerto interno.

Como comprobación adicional, se enviaron cabeceras de procedencia distintas
desde la misma conexión de prueba. El proxy las reemplazó y conservó el límite
de 12 solicitudes; por tanto, no se aceptó una falsificación de identidad de
cliente para evadir el control. Esta verificación no sustituye una campaña
desde veinte redes reales.

### Capacidad de ejecución aplicada

La primera prueba evidenció que el VPS conservaba el valor predeterminado de
ocho simulaciones. Se incorporó al servicio el perfil de producción acordado:
20 sesiones activas, 4 simulaciones, 120 segundos de duración máxima y 8 hilos.
Tras recrear el contenedor, se realizó de nuevo una prueba con cinco sesiones:

| Comprobación | Resultado |
| --- | --- |
| Primeras cuatro ejecuciones | PASS: `200` en las cuatro |
| Quinta ejecución simultánea | PASS: `429` por capacidad ocupada |
| Cierre de las cinco sesiones de prueba | PASS: 5 de 5 |
| Salud y métricas con token operativo | PASS |
| HTTPS público tras recreación | PASS: `200 OK` |
| Puerto directo tras recreación | PASS: inaccesible desde Internet |

### Reversión controlada

Se amplió el historial del clon del VPS, se respaldaron sus cambios locales y
se desplegó temporalmente el commit inmediatamente anterior con el mismo
proxy, secretos, red interna y límites. La URL pública respondió con error de
disponibilidad para esa versión, por lo que la compuerta de aceptación rechazó
la reversión. Se restauró de inmediato el commit actual, se recompuso el
contenedor y se verificó de nuevo `HTTPS 200` con el puerto interno inaccesible
desde Internet. Los secretos temporales usados para la prueba se eliminaron;
los cambios locales preexistentes del servidor se conservaron intactos.
