# Misiones evaluables EV3

> Estado: actual al 2026-07-24. Version aplicable: `1.4.0`. Las evidencias se
> generan localmente; no incluyen datos personales por defecto.

Las misiones se ejecutan con los mismos scripts y mundos en la interfaz Web y
Tkinter. La evaluación debe basarse en la traza JSON exportada, no en la
interfaz usada por el estudiante.

| Misión | Ejemplo/Mundo | Evidencia mínima | Criterio |
| --- | --- | --- | --- |
| Sigue líneas | `11_siguelineas_basico.py` / `01_linea_negra_basica.json` | Traza JSON | El robot mantiene lecturas de reflexión y no termina por error. |
| Evita obstáculos | `15_esquiva_obstaculos.py` / `05_obstaculos_baliza_ir.json` | Traza JSON | No queda en colisión y usa distancia ultrasónica. |
| Radar | `23_radar_ultrasonido_5grados.py` / `12_radar_ultrasonido_360.json` | Traza JSON/CSV | Registra lecturas repetidas del sensor ultrasónico. |

## Rúbrica común

- 40 %: el programa carga y termina sin `error` ni `timed_out`.
- 35 %: evidencia de sensores y movimiento en la traza.
- 25 %: comportamiento específico de la misión verificado por el docente.

Las trazas permiten repetir la revisión sin exigir acceso al robot físico.

## Entrega de evidencia

1. Registrar la ejecucion desde el menu **Trazas**.
2. Exportar JSON o CSV con un nombre que identifique mision, fecha y equipo.
3. Entregar el script, el mundo JSON y la traza exportada.
4. Anotar el perfil de simulacion usado y cualquier ajuste de sensores.

La evidencia representa una simulacion. El docente debe aplicar los limites del
apartado siguiente antes de extrapolar el resultado al robot fisico.

## Simulador frente a robot físico

- El perfil `ideal` es determinista; el robot real tiene tolerancias mecánicas,
  batería, iluminación y deslizamiento.
- El perfil `realistic` introduce tracción y ruido reproducibles, pero no
  sustituye la calibración sobre el tablero físico.
- Antes de evaluar en el robot, se deben recalibrar umbrales de reflexión,
  diámetro efectivo de rueda y posición de sensores.
