# Informe de prueba manual asistida — Escritorio

Fecha: 2026-07-24.

## Alcance ejecutado

- Ventana Tkinter iniciada, movida a pantalla principal y verificada como responsive.
- Ratón: foco del editor, botón **Ejecutar** y **Detener y reiniciar**.
- Teclado: selección y sustitución temporal del script en el editor.
- Script usado: `print('QA_UI_OK')` y `wait(200)`.

## Resultado

El editor aceptó el texto y Ejecutar inició la simulación. Detener y reiniciar dejó el proceso responsive.

## Hallazgo manual

`MAN-01` (media, no confirmado): tras dos segundos la barra mostraba “Simulación en curso” para el script corto. No se declara defecto confirmado porque las pruebas automatizadas de ciclo de vida y paridad pasan; requiere una prueba de UI con aserción temporal del estado final y lectura de la consola/estado para reproducirse de forma determinista.

## Seguridad

- Bandit: salida 0 sin hallazgos de severidad media o superior.
- Pip-Audit: sin vulnerabilidades conocidas en `requirements-audit.txt`.
