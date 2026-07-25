# Matriz de trazabilidad

| Requisito inferido | Riesgo | Prueba automatizada | Estado |
|---|---|---|---|
| R-01 Ejecutar scripts con límites | Alto | `tests/runtime/test_isolated_worker.py` | Aprobado |
| R-02 Mantener sesión Web recuperable | Alto | `tests/web/test_web_app.py` | Aprobado |
| R-03 Paridad de interfaces | Alto | `tests/shared/test_interface_execution_parity.py` | Aprobado |
| R-04 Editar y validar mundos | Alto | `tests/application/test_world_editor_service.py` | Aprobado |
| R-05 UI Web operable | Alto | `tests/e2e/test_web_playwright.py` | Aprobado |
