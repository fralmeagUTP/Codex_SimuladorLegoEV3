# Tareas: madurar calidad y experiencia de aula

## Fase 1 - Paridad completa y documentacion fiable

- [x] 1.1 Auditar UC-WORLD-01, UC-WORLD-02, UC-WORLD-03 y UC-HELP-01 en Web y Tkinter. Evidencia: `openspec/use-cases/matriz-paridad-actual-v1.md`.
- [x] 1.2 Completar funciones faltantes o registrar limitaciones explicitamente aceptadas. La acción `Simular mundo guardado` y la ayuda contextual cierran las brechas detectadas.
- [x] 1.3 Añadir pruebas de contrato y matriz de trazabilidad para esos casos de uso. Evidencia: `tests/shared/test_help_tutorials.py`, `tests/ui/test_world_editor_navigation.py` y catálogo de casos de uso.
- [x] 1.4 Corregir roadmap, manuales y checklist para separar evidencia historica de estado actual.
- [x] 1.5 Añadir una prueba que detecte version, comandos o resultados de calidad obsoletos. Evidencia: `tests/shared/test_project_documentation.py`.

## Fase 2 - Automatizacion de escritorio y regresion visual

- [x] 2.1 Seleccionar y documentar el driver grafico Windows compatible con Tkinter y CI. Driver: `pywinauto`; ejecución local optativa documentada.
- [x] 2.2 Implementar recorridos de escritorio para menus, teclado, ejecucion, pausa, mundo, depuracion y recuperacion. Evidencia: `tests/e2e/test_desktop_pywinauto.py` (ejecución local explícita con escritorio Windows).
- [x] 2.3 Definir regiones, mascaras nativas y umbrales de comparacion visual Web/Tkinter. Evidencia: `scripts/compare_visual_evidence.py`, prueba unitaria y matriz visual.
- [x] 2.4 Ejecutar capturas y comparacion visual en CI; adjuntar artefactos ante fallo. Evidencia: trabajo `desktop-visual` de `.github/workflows/quality.yml` y comparador con umbral `0.08`.
- [x] 2.5 Mantener aprobacion explicita de referencias visuales y evidencia reproducible. Evidencia: `Documentos/MATRIZ_PARIDAD_VISUAL_WEB_TKINTER.md` y capturadores de referencia.

## Fase 3 - Conformidad Pybricks avanzada

- [x] 3.1 Especificar semantica y limites de `Motor.run_target` y `Motor.run_until_stalled`. Implementación aproximada documentada en docstrings y `Documentos/DIFERENCIAS_SIMULADOR_ROBOT.md`.
- [x] 3.2 Implementar y probar ambos metodos en todos los perfiles de simulacion aplicables. Evidencia: `tests/pybricks_api/test_pybricks_api.py`.
- [x] 3.3 Especificar e implementar curvas de `DriveBase` con comportamiento declarado. Evidencia: `pybricks_api/robotics.py` y prueba `curve`.
- [x] 3.4 Añadir `ColorSensor.hsv` y configuracion de colores detectables con pruebas de borde. Evidencia: `pybricks_api/ev3devices.py` y pruebas de sensor de color.
- [x] 3.5 Actualizar matriz de conformidad y diferencias simulador-robot por cada metodo. Evidencia: `openspec/changes/elevar-calidad-y-paridad-de-interfaz/pybricks-conformance-v1.md` y `Documentos/DIFERENCIAS_SIMULADOR_ROBOT.md`.

## Fase 4 - Experiencia docente local

- [x] 4.1 Definir esquema versionado de mision, rubrica y resultado sin datos personales. Evidencia: `simulador_ev3/domain/assessment/mission_models.py` y `tests/domain/assessment/test_mission_models.py`.
- [x] 4.2 Implementar catalogo de misiones y carga equivalente en Web y Tkinter. Evidencia: `simulador_ev3/shared/mission_catalog.py`, menús `Misiones` y API `/api/missions`.
- [x] 4.3 Ejecutar pruebas de aceptacion de una mision contra una traza determinista. Evidencia: `MissionEvaluator` y `tests/application/test_mission_evaluator.py`.
- [x] 4.4 Exportar resultado local JSON/CSV y validar su portabilidad. Evidencia: `simulador_ev3/application/mission_export.py` y `tests/application/test_mission_export.py`.
- [x] 4.5 Documentar flujo docente, limites del simulador y politica de privacidad local. Evidencia: `Documentos/MISIONES_EVALUABLES.md`.

## Criterios de cierre

- Todas las tareas incluyen pruebas y evidencia enlazada.
- Ninguna diferencia Web/Tkinter queda sin clasificar en la matriz de paridad.
- La cobertura y quality gates existentes se mantienen o aumentan.
- La propuesta se archiva solo con CI verde en Windows y Linux cuando aplique.
