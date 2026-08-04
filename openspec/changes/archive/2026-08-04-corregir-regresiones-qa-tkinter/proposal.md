# Propuesta: corregir regresiones QA de Tkinter

## Motivo

La campaña QA de `Documentos/INFORME_TESTEO_INTEGRAL_2026-07-27.md` encontró
TK-001 (telemetría truncada), TK-002 (Robot/Estado inaccesible bajo la LCD) y
TK-003 (callback Tcl inválido al cierre). Impiden aprobar la liberación de
escritorio.

## Cambio propuesto

Reorganizar responsivamente telemetría y Brick, hacer idempotente el cierre de
la ventana y añadir evidencia/pruebas para 1024×768, 1280×800 y 1920×1080 en
temas claro y oscuro.

## Fuera de alcance

- Motor de simulación, runtime Pybricks, mundos, misiones y datos.
- Rediseño funcional de la Web.
- Declarar aprobados menús, mundos, misiones o scripts sin recorrido Windows
  interactivo verificable.

## Impacto

Se afectan `ui/telemetry_panel.py`, `ui/brick_panel.py`, `ui/main_window.py`,
el capturador de evidencia y las pruebas de escritorio.
