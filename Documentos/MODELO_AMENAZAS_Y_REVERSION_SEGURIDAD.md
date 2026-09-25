# Modelo de amenazas y reversión de seguridad

Fecha de revisión: 2026-08-24. Alcance: aplicación Web pública anónima y
aplicación de escritorio para aula. No se implementan cuentas, autenticación ni
roles.

## Amenazas y controles

| Riesgo | Control aplicado | Límite conocido |
| --- | --- | --- |
| Abuso de creación de sesiones o comandos | cuota por cliente y límites de sesiones/workers | ajustar cuotas según recursos del servidor |
| Script Pybricks no confiable | worker aislado, entorno saneado, temporal privado, bloqueo de red y límites disponibles de CPU/memoria | el sandbox Python no sustituye el aislamiento del sistema operativo |
| CSRF y llamadas externas a rutas mutables | validación Origin/Fetch Metadata y cookie segura en HTTPS | el proxy debe conservar cabeceras de origen |
| Exposición operativa | política configurable para health, métricas y operaciones; redacción de diagnósticos | proteger además por red/proxy en Nyquist |
| Residuos y consumo de disco | limpieza de temporales propios, trazas acotadas y escritura atómica | no se borran archivos ni procesos ajenos |
| Archivos locales malformados | extensiones y tamaños limitados en Tkinter | el usuario conserva la responsabilidad sobre archivos elegidos |

## Configuración mínima Nyquist

1. Activar HTTPS en el dominio y configurar `EV3_WEB_SESSION_COOKIE_SECURE=true`.
2. Establecer una clave secreta única de al menos 32 caracteres fuera del repositorio.
3. Usar `EV3_WEB_APP_ENV=production`, `EV3_WEB_OPERATIONS_ACCESS_POLICY=token`
   y conservar el token de operaciones solo en la configuración del servidor.
4. Mantener el proceso como usuario sin privilegios, limitar CPU, memoria, PIDs
   y egress en la plataforma o proxy.
5. Verificar `/healthz` desde la red administrativa autorizada y ejecutar la
   campaña de sesiones concurrentes antes de cada liberación.

## Procedimiento de reversión

1. Desactive temporalmente el tráfico o revierta al último artefacto etiquetado
   que haya aprobado las pruebas de seguridad.
2. Si existe sospecha de exposición, rote inmediatamente `EV3_WEB_SECRET_KEY`
   y el token de operaciones; no reutilice los anteriores.
3. Reinicie la instancia: las sesiones anónimas en memoria se descartarán y los
   workers activos serán cerrados.
4. Revise logs redaccionados, `/healthz` y métricas; conserve evidencia sin
   incluir scripts, cookies, tokens ni rutas privadas.
5. Reabra el servicio solo después de validar inicio, carga de mundo, ejecución
   corta, reinicio y cierre de sesión.

## Criterios de liberación

- Pruebas `security`, worker y carga concurrente aprobadas.
- Bandit sin hallazgos de severidad media/alta y Pip-Audit sin vulnerabilidades
  sin evaluar.
- Configuración de producción rechaza secretos débiles, cookies inseguras y
  límites inválidos.
- Evidencia de commit, comandos y resultados archivada junto a la liberación.
