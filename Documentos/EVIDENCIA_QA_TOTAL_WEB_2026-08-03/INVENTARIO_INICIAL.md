# Inventario inicial — QA total Web

## Entorno congelado

- Fecha: 2026-08-03.
- URL: `http://127.0.0.1:5050/` (`/healthz`: HTTP 200).
- SO: Windows 10 Pro 10.0.19045.
- Python: 3.12.5.
- Rama/commit: `codex/desbloquear-menus-al-finalizar-ejecucion` / `9708d1e`.
- Servidor: Waitress local.
- Navegador: navegador gráfico integrado de Codex; campaña manual visible.

## Catálogo descubierto por la instancia

| Tipo | Cantidad | Elementos |
|---|---:|---|
| Menús | 10 | Archivo, Ejemplos, Mundos, Escenarios, Misiones, Tema, Fidelidad, Tiempo máximo, Trazas, Ayuda |
| Ejemplos | 23 | `01_intro_led.py` a `23_radar_ultrasonido_5grados.py` |
| Mundos | 12 | `01_linea_negra_basica.json` a `12_radar_ultrasonido_360.json` |
| Escenarios | 4 | Seguidor de línea, Ultrasonido + obstáculos, Test pantalla/altavoz, Radar 360 ultrasonido |
| Misiones | 3 | Sigue líneas básico, Evita obstáculos, Radar ultrasónico |

## Detalle de ejemplos

`01_intro_led.py`, `02_intro_pantalla_altavoz.py`, `03_movimiento_basico.py`,
`04_movimiento_motores_individuales.py`, `05_drivebase_cuadrado.py`,
`06_drivebase_perfiles_aceleracion.py`, `07_sensor_tacto_reaccion.py`,
`08_sensor_ultrasonido_frenado.py`, `09_sensor_color_stop.py`,
`10_sensores_combinados.py`, `11_siguelineas_basico.py`,
`12_siguelineas_robusto.py`, `13_colision_controlada.py`,
`14_navegacion_hasta_pared.py`, `15_esquiva_obstaculos.py`,
`16_resolver_laberinto.py`, `17_gyro_correccion_rumbo.py`,
`18_infrarrojo_beacon_seguidor.py`, `19_motor_encoder_objetivos.py`,
`20_motor_run_until_stalled.py`, `21_drivebase_curva_estado.py`,
`22_stopwatch_mision_etapas.py`, `23_radar_ultrasonido_5grados.py`.

## Criterio de seguimiento

Cada elemento se incorporará a la matriz con PASS, FAIL o BLOCKED. Un PASS de
interfaz exige ejecución visible mediante navegador; los resultados de API o
pruebas automatizadas se registran como evidencia complementaria.
