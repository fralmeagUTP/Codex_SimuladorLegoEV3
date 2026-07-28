# Inventario funcional

| ID | Funcionalidad | Componentes | Riesgo | Pruebas |
|---|---|---|---|---|
| F-01 | Ejecutar scripts Pybricks | runtime, application, core | Alto | unitarias, runtime, integración |
| F-02 | Aislamiento y recuperación worker | runtime/isolated_worker.py, web/session | Alto | runtime y carga |
| F-03 | Sesiones Web y token propietario | web/session_manager.py, rutas API | Alto | API e integración |
| F-04 | Depuración, trazas y perfiles | sesiones, Web, Tkinter | Alto | paridad y E2E |
| F-05 | Editor y mundos JSON | application/world_editor_service.py, Web/Tkinter | Alto | dominio, API, UI |
| F-06 | Telemetría, brick y canvas | snapshots, JS, Tkinter | Medio | UI/Web/E2E |
| F-07 | Métricas y trazas operativas | web/app.py, pages.py | Medio | Web |

Los requisitos se infieren de README, OpenSpec y código; no hay historias de usuario formales separadas.
