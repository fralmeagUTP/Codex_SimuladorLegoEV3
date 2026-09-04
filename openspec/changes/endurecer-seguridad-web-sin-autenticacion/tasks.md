# Tareas: endurecer seguridad Web sin autenticación

## Fase 1 — Contratos y configuración

- [x] 1.1 Definir configuración tipada de cuotas por cliente, confianza de proxy y políticas de endpoints operativos.
- [x] 1.2 Definir contrato de respuesta `429`, `Retry-After` y mensajes sin detalles internos.
- [x] 1.3 Definir política de validación `Origin`/Fetch Metadata compatible con el cliente Web existente.
- [x] 1.4 Actualizar especificaciones `web-sessions`, `observability`, `script-runtime` y ciclo de vida de recursos.

## Fase 2 — Protección HTTP y sesiones

- [x] 2.1 Implementar limitador por cliente para crear sesión y comandos costosos, con limpieza acotada de memoria.
- [x] 2.2 Proteger `/healthz`, `/metrics` y `/operations` por política configurable y ocultar detalles sensibles en modo público.
- [x] 2.3 Añadir validación anti-CSRF basada en origen/metadatos de petición a rutas mutables.
- [x] 2.4 Completar CSP, política de cookies HTTPS y documentación de HSTS del proxy.
- [x] 2.5 Aplicar permisos restrictivos y validación de ruta al espejo de metadatos de sesión.

## Fase 3 — Aislamiento de ejecución y operación

- [x] 3.1 Añadir perfil de producción Linux con límites cgroup/PIDs, usuario no privilegiado y filesystem temporal.
- [x] 3.2 Documentar denegación de egress y límites de workers para Docker/Nyquist sin afirmar garantías inexistentes.
- [x] 3.3 Reducir `except Exception` silenciosos de rutas, recuperación de sesiones y runtime; registrar fallos sin secretos.
- [x] 3.4 Asegurar que logs, métricas y diagnósticos nunca incluyan token de propietario ni script completo.

## Fase 4 — Recursos y memoria

- [x] 4.1 Registrar workers y temporales por sesión; cerrar, esperar y verificar cada worker en cierre, expiración y apagado de Web/Tkinter.
- [x] 4.2 Implementar limpieza de arranque para residuos propios expirados, sin actuar sobre procesos ni archivos ajenos.
- [x] 4.3 Eliminar temporales de carga de mundo mediante `try/finally` y establecer antigüedad máxima configurable.
- [x] 4.4 Acotar snapshots de `SimulationTrace`, indicar truncamiento y liberar trazas al cerrar/reiniciar sesión.
- [x] 4.5 Convertir persistencia de preferencias de escritorio a escritura atómica y recuperación segura ante archivo parcial.

## Fase 5 — Seguridad de escritorio

- [x] 5.1 Inventariar aperturas, guardados, importaciones y persistencia de archivos de Tkinter; validar rutas, extensiones y tamaño.
- [x] 5.2 Hacer obligatorio el worker aislado para scripts de escritorio fuera del modo explícito de compatibilidad.
- [x] 5.3 Asegurar que el worker de escritorio herede entorno saneado, directorio temporal privado y límites de CPU/memoria disponibles.
- [x] 5.4 Eliminar exposición de rutas, trazas o secretos en diálogos y registros de diagnóstico de escritorio.
- [x] 5.5 Verificar que el ejecutable Windows se ejecute sin privilegios elevados y documentar permisos de instalación/datos.

## Fase 6 — Pruebas y liberación

- [x] 6.1 Crear pruebas de cuota por cliente, restablecimiento de ventana y rechazo antes de crear worker.
- [x] 6.2 Crear pruebas de origen cruzado, cabeceras, endpoints operativos y redacción de diagnósticos.
- [x] 6.3 Crear pruebas de cierre de workers, limpieza de temporales, límite de traza y escritura atómica de preferencias.
- [x] 6.4 Crear pruebas de permisos del espejo, archivos de escritorio y configuración productiva inválida.
- [x] 6.5 Ejecutar Bandit, Pip-Audit, pruebas `security`, pruebas de worker y carga concurrente local.
- [x] 6.6 Actualizar guía Nyquist, modelo de amenazas, procedimiento de reversión y evidencia de liberación.
