# Evidencia de liberación de seguridad — 2026-08-24

## Contexto

- Commit evaluado: `c1e715a` (antes de los cambios de esta campaña).
- Rama: `codex/desbloquear-menus-al-finalizar-ejecucion`.
- Sistema: Windows 10; Python 3.12.5.
- Alcance: cambio OpenSpec `endurecer-seguridad-web-sin-autenticacion`.
- Producto: anónimo; no se agregaron cuentas, autenticación ni roles.

## Resultados verificables

| Verificación | Resultado |
| --- | --- |
| Ruff sobre producción y pruebas de campaña | PASS |
| Archivos limitados, editor de mundos y worker | PASS, 53 pruebas |
| Pruebas marcadas `security` | PASS, 13 pruebas |
| Carga local concurrente de sesiones | PASS, 3 pruebas |
| Bandit (`-lll`) | PASS, sin hallazgos de severidad media/alta |
| Pip-Audit | PASS tras actualizar `pip` 26.1.2 a 26.2 |
| Validación OpenSpec estricta | PASS |
| Build PyInstaller temporal | PASS |
| Inicio/cierre del ejecutable de distribución sin elevación | PASS |

## Comandos ejecutados

```powershell
.\.venv\Scripts\ruff.exe check simulador_ev3 tests\shared\test_local_file_security.py tests\application\test_desktop_session_adapter.py tests\runtime\test_isolated_worker.py tests\load\test_web_session_load.py
.\.venv\Scripts\python.exe -m pytest tests\shared\test_local_file_security.py tests\application\test_world_editor_service.py tests\application\test_desktop_session_adapter.py tests\runtime\test_isolated_worker.py -q --basetemp .pytest-security-phase56-postredaction
.\.venv\Scripts\python.exe -m pytest -m security -q --basetemp .pytest-security-marked-final
.\.venv\Scripts\python.exe -m pytest tests\load\test_web_session_load.py -q --basetemp .pytest-security-load-final
.\.venv\Scripts\bandit.exe -r simulador_ev3 -q -lll
.\.venv\Scripts\pip-audit.exe
openspec validate endurecer-seguridad-web-sin-autenticacion --strict
.\scripts\build_release_windows.ps1 -PythonExe .\.venv\Scripts\python.exe -BuildRoot artifacts\security-release-20260824\build -DistRoot artifacts\security-release-20260824\dist -SkipInstaller
```

El ejecutable temporal generado en
`artifacts/security-release-20260824/dist/SimuladorEV3/SimuladorEV3.exe` se
inició con una cuenta sin elevación, permaneció activo cinco segundos y se cerró
controladamente. El ZIP contiene el ejecutable.

## Hallazgo corregido durante la campaña

Las pruebas de carga consultaban `/metrics` suponiendo exposición pública. El
contrato actual protege la observabilidad por política; se actualizó el entorno
de prueba para declararlo explícitamente como cliente local autorizado. La
carga volvió a aprobar sin relajar la protección de producción.

## Límites y seguimiento

- `pip-audit` no consulta el paquete local `simulador-ev3` porque no está
  publicado en PyPI; sí auditó las dependencias instaladas y no reportó
  vulnerabilidades conocidas.
- No se validó el build Docker: el daemon local respondió acceso denegado al
  socket de Docker Desktop. Debe repetirse en el host/CI con Docker disponible
  antes de publicar una imagen Linux.
- La validación de la app de escritorio fue un smoke de arranque/cierre; las
  pruebas funcionales GUI siguen el protocolo manual de la aplicación.
