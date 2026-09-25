# Auditoría de acoplamientos UI–sesión

Fecha de base: `2026-08-23`
Alcance: Fase 2.1 de `igualar-madurez-integral-web-tkinter`.

## Regla de arquitectura

Las vistas Web y Tkinter no pueden acceder a atributos privados de
`SimulationService`, `SimulationEngine`, worker ni a widgets pertenecientes a
otro panel. La comunicación de ejecución usa `SimulationSessionPort`; la
presentación, aprendizaje y diagnóstico usan respectivamente `PresentationPort`,
`LearningPort` y `ObservabilityPort`.

## Resultado de la auditoría inicial

- `ui/main_window.py` usa únicamente métodos y propiedades públicas de
  `DesktopSessionAdapter`.
- `web/routes` no accede a detalles privados de `SimulationSession`.
- Las referencias `_service` de `world_editor_window.py` pertenecen al propio
  presentador y usan la API pública de `WorldEditorService`.
- Los detalles de worker y motor permanecen encapsulados dentro de
  `DesktopSessionAdapter` y `web/services/simulation_session.py`, que son
  adaptadores de aplicación y no vistas.

## Control de regresión

`tests/shared/test_ui_layer_boundaries.py` analiza las vistas principales y
falla si aparece un acceso de tipo `._service._`, `._engine._`, `._worker._` o
`._controller._`. Las excepciones futuras requieren una decisión de arquitectura
documentada, una alternativa pública y una prueba de contrato.
