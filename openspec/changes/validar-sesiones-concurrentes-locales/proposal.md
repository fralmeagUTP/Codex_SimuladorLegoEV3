# Propuesta: validar sesiones concurrentes locales para despliegue Web

## Motivo

La aplicación Web se desplegará en `nyquist.app`, donde varias personas pueden
abrir el simulador al mismo tiempo. Aunque existen pruebas unitarias y de carga
interna, se requiere una campaña HTTP local reproducible que demuestre creación,
aislamiento, límite de capacidad, métricas y cierre de sesiones antes del
despliegue remoto.

## Cambio propuesto

Incorporar un ejecutor local de carga que levante una instancia aislada del
servidor y simule navegadores independientes. La campaña creará sesiones en
paralelo, cargará scripts distintos, verificará que un token no pueda leer otra
sesión, comprobará respuestas `429` al rebasar límites y cerrará todos los
recursos creados. El resultado quedará en un informe auditable.

## Alcance

- Sesiones REST, tokens de propietario, scripts, métricas y capacidad.
- Servidor local temporal; no se usan datos, credenciales ni servicios remotos.
- Guía de configuración y criterios para el futuro despliegue en Nyquist.

## Fuera de alcance

- Prueba de carga sobre `nyquist.app` o sobre usuarios reales.
- Prueba de capacidad definitiva del hardware del servidor de producción.
- Cambios de reglas de negocio del simulador.

## Éxito esperado

Una campaña configurable demuestra que usuarios concurrentes reciben sesiones
distintas, no comparten scripts ni permisos, el servidor aplica sus límites y
libera las sesiones creadas al terminar.
