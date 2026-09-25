# Validaciones externas pendientes

Las validaciones locales y de CI se aprobaron el 2026-07-30. Este archivo se
mantiene como referencia para repetirlas cuando cambie el proceso de despliegue.

## E2E nativo de Tkinter (aprobado)

1. Abrir una sesión Windows local normal (no RDP desconectado ni servicio).
2. Ejecutar desde la raíz del proyecto:

   ```powershell
   $env:EV3_RUN_DESKTOP_E2E = '1'
   .\.venv\Scripts\python.exe -m pytest tests\e2e\test_desktop_pywinauto.py -q -rs
   ```

3. Resultado obtenido: cuatro pruebas aprobadas y captura o error conservado ante fallo.

## Runner Windows limpio (aprobado en CI)

Publicar los cambios y comprobar en GitHub Actions los jobs `windows-release-smoke`
y `docker-smoke`. El primero crea el artefacto desde cero y arranca el `.exe`; el
segundo revalida de forma remota el contenedor y consulta `/healthz`.

Las ejecuciones del workflow `calidad` asociadas al PR #4 finalizaron en verde,
incluidos `contenedor Linux` y `empaquetado Windows limpio`.
