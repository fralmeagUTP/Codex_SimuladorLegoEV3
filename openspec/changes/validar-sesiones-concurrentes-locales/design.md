# Diseño: campaña local de sesiones concurrentes

## Arquitectura de prueba

`run_web_session_load.py` iniciará `create_app()` con directorios temporales y
un servidor HTTP local en un puerto aleatorio. Un grupo de hilos representará
usuarios sin cookies compartidas. Cada usuario crea su sesión, carga un script
con una marca única y consulta su resumen autenticado.

## Oráculos

1. Cada alta dentro de capacidad devuelve `201`, UUID y token únicos.
2. Cada script se carga solo en la sesión de su propietario.
3. Un token de otra sesión recibe `403` o `404`, nunca información ajena.
4. Al superar `MAX_ACTIVE_SESSIONS`, el servidor devuelve `429`.
5. `/metrics` informa sesiones activas y contadores coherentes.
6. Al cerrar las sesiones de la campaña, el contador vuelve a cero.

## Seguridad y límites

La carga por defecto será moderada (24 usuarios, 8 hilos) y se ejecutará en una
instancia temporal, no en la aplicación abierta por una persona. Los scripts
son sintéticos y no contienen secretos. La prueba informa latencias observadas,
pero no declara un SLA de producción.

## Evidencia

El ejecutor escribirá JSON en `Documentos/EVIDENCIA_SESIONES_CONCURRENTES/`.
El informe resumirá entorno, configuración, resultados, errores y límites para
la decisión de despliegue en Nyquist.
