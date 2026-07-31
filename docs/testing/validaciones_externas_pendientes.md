# Validaciones externas pendientes

Las validaciones pendientes requieren un escritorio Windows que Pywinauto pueda
detectar o la ejecución remota de CI. El smoke Docker/Linux local fue aprobado
el 2026-07-30.

## 1. E2E nativo de Tkinter

1. Abrir una sesión Windows local normal (no RDP desconectado ni servicio).
2. Ejecutar desde la raíz del proyecto:

   ```powershell
   $env:EV3_RUN_DESKTOP_E2E = '1'
   .\.venv\Scripts\python.exe -m pytest tests\e2e\test_desktop_pywinauto.py -q -rs
   ```

3. Resultado esperado: cuatro pruebas aprobadas y captura o error conservado ante fallo.

## 2. Runner Windows limpio

Publicar los cambios y comprobar en GitHub Actions los jobs `windows-release-smoke`
y `docker-smoke`. El primero crea el artefacto desde cero y arranca el `.exe`; el
segundo revalida de forma remota el contenedor y consulta `/healthz`.

No marcar estas validaciones como aprobadas hasta adjuntar la salida completa o
el enlace de la ejecución de CI al reporte de QA.
