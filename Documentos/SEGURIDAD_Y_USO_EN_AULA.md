# Seguridad y uso en aula

> Estado: revisado al 2026-08-05. Versión aplicable: `1.5.0`. Audiencia:
> docentes, operacion y desarrollo.

## Modelo de seguridad

Los scripts Pybricks son codigo proporcionado por estudiantes. El modo normal
los ejecuta en un worker aislado, con limites de tiempo, memoria, red y sistema
de archivos definidos por el runtime. El proceso de interfaz o servidor no debe
ejecutar directamente scripts no confiables.

`EV3_LOCAL_RUNTIME_ENABLED=true` habilita compatibilidad local para desarrollo
y pruebas. No debe usarse para ejecutar scripts no confiables en una instalacion
compartida.

## Uso local y produccion

- Para aula local, mantener el servidor en `127.0.0.1` o una red controlada.
- Para produccion, definir `EV3_WEB_APP_ENV=production`, una clave secreta unica
  de al menos 32 caracteres, limite positivo de script y cookies seguras HTTPS.
- No guardar `EV3_WEB_SECRET_KEY`, URL de Redis ni datos personales en archivos
  versionados, capturas, trazas o ejemplos.
- Mantener activas las cabeceras HTTP de seguridad salvo una integracion
  controlada y documentada.
- Limitar sesiones y simulaciones concurrentes segun capacidad del equipo.

## Datos y evidencia docente

Las trazas JSON/CSV describen la ejecucion simulada. Antes de compartirlas,
revisar nombres de archivos, comentarios de scripts y cualquier identificador
que el usuario haya incluido. La aplicacion no requiere datos personales para
ejecutar misiones locales.

## Seguridad fisica

El worker protege el proceso de software, no un robot fisico. Al migrar una
actividad al EV3 real se debe usar velocidad baja, zona despejada, parada
accesible y calibracion previa. Consultar `DIFERENCIAS_SIMULADOR_ROBOT.md`.

## Respuesta a fallos

1. Revisar `/healthz` y los logs de la aplicacion.
2. Si un worker falla, usar el estado y mensaje de recuperacion de la sesion;
   no reutilizar una traza incompleta como evidencia de exito.
3. Si se sospecha exposicion de un secreto, revocarlo en la plataforma de
   despliegue, generar uno nuevo y reiniciar el servicio.
4. Reportar errores de seguridad sin adjuntar secretos ni scripts privados.
