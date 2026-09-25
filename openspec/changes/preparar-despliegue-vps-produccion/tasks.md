# Tareas: preparar despliegue Web para VPS de producción

## Fase 1 — Contrato de producción y configuración

- [x] 1.1 Auditar las variables `EV3_WEB_*` y consolidar valores de VPS de 2 vCPU/8 GB: 20 sesiones, 4 simulaciones, 120 s y 8 hilos.
- [x] 1.2 Crear plantilla `.env.production.example`, excluida de secretos, y validar su correspondencia con `WebConfig`.
- [x] 1.3 Hacer que el arranque productivo rechace con mensaje seguro las combinaciones incompatibles de secretos, HTTPS, temporales y límites.
- [x] 1.4 Documentar el paso obligatorio a Redis antes de ejecutar múltiples réplicas Web.

## Fase 2 — Empaquetado y perímetro del VPS

- [x] 2.1 Ajustar y validar `Dockerfile` y Compose para usuario no privilegiado, filesystem de solo lectura, tmpfs privado, límites de CPU, memoria y PID.
- [x] 2.2 Incorporar configuración de referencia Nginx o Caddy: TLS, redirección HTTP, upstream privado, cabeceras proxy y compatibilidad SSE.
- [x] 2.3 Asegurar que los puertos de Waitress no queden publicados directamente a Internet.
- [x] 2.4 Preparar creación idempotente de rutas privadas para workers, espejo de sesiones, logs y respaldos.

## Fase 3 — Operación, observabilidad y mantenimiento

- [x] 3.1 Configurar salud, métricas y tablero operativo para acceso desde host o token, sin exposición pública de datos internos.
- [x] 3.2 Definir rotación de logs, limpieza segura de temporales y alerta por CPU, RAM, PID, 5xx, sesiones y disco.
- [x] 3.3 Documentar procedimientos paso a paso de instalación, actualización, respaldo y reversión para Ubuntu/Debian.
- [x] 3.4 Actualizar la guía de hosting con criterios de aceptación y diagnóstico para proxy, certificados y workers.

## Fase 4 — Pruebas y aceptación

- [x] 4.1 Añadir pruebas unitarias de valores productivos, secreto ausente, límites inválidos y rutas temporales inseguras.
- [x] 4.2 Ejecutar campaña local reproducible de 20 sesiones y 4 simulaciones; registrar latencia, errores, limpieza y consumo.
- [ ] 4.3 Desplegar en staging VPS o equivalente y comprobar HTTPS, cookies seguras, aislamiento de sesiones, límites, healthcheck y reversión. *(Staging Docker local aprobado. En el VPS real se validaron HTTPS, cookies, healthcheck y métricas con token, aislamiento, cierre del puerto directo, el límite de cuatro simulaciones, la protección contra cabeceras falsificadas y la reversión controlada con restauración satisfactoria. Falta una campaña distribuida de 20 clientes.)*
- [ ] 4.4 Ajustar concurrencia solamente con evidencia de CPU, memoria y experiencia fluida; actualizar el informe de capacidad. *(El perfil de 4 simulaciones ya fue aplicado y validado funcionalmente; falta una medición sostenida y distribuida de CPU, memoria y fluidez en el VPS.)*
