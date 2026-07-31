# Reporte de ejecución

## Actualización QA integral — 2026-07-28

| Comando | Objetivo | Resultado |
|---|---|---|
| `.\.venv\Scripts\python.exe -m pytest -q` | Regresión completa (revalidada el 2026-07-29) | 777 aprobadas, 4 omitidas. |
| `.\.venv\Scripts\python.exe -m pytest -q` | Regresión completa (2026-07-30) | **799 aprobadas, 4 omitidas en 91.38 s**. Las cuatro omisiones pertenecen a E2E Tkinter sin escritorio Windows visible. |
| `.\.venv\Scripts\python.exe -m pytest --cov=simulador_ev3 --cov-report=term --cov-report=json:build\qa-coverage.json -q` | Cobertura real | 773 aprobadas, 4 omitidas; 71.15 %. |
| `.\.venv\Scripts\python.exe -m pytest --cov=simulador_ev3 --cov-report=term --cov-report=json:build\qa-coverage.json -q` | Cobertura real (2026-07-30) | **799 aprobadas, 4 omitidas; 71.35 %**. Supera el umbral 70 %. `coverage` avisó que usó trazador Python al no disponer de trazador C. |
| `.\.venv\Scripts\python.exe -m ruff check simulador_ev3 tests` | Lint | salida 0. |
| `.\.venv\Scripts\python.exe -m ruff check simulador_ev3 tests` | Lint global (2026-07-30) | salida 0. |
| `.\.venv\Scripts\python.exe -m mypy` | Tipado global | 109 módulos, salida 0. |
| `.\.venv\Scripts\python.exe -m mypy` | Tipado global (2026-07-30) | 109 módulos, salida 0. |
| `.\.venv\Scripts\python.exe -m bandit -q -r simulador_ev3` | Seguridad estática (revalidada el 2026-07-29) | salida 1: 56 hallazgos, 54 bajos (`try/except` silencioso) y 2 medios (`exec` de scripts y `eval` de watches en el sandbox). Requieren clasificación explícita; no se ocultaron. |
| `.\.venv\Scripts\python.exe -m bandit -q -c pyproject.toml -r simulador_ev3` | Seguridad estática con política oficial | salida 0. `pyproject.toml` excluye B102/B110/B112/B307 por el sandbox y callbacks tolerantes a fallos; CI debe invocar esta variante para evitar resultados distintos. |
| `.\.venv\Scripts\python.exe -m bandit -q -c pyproject.toml -r simulador_ev3` | Seguridad estática con política oficial (2026-07-30) | salida 0. |
| `.\.venv\Scripts\python.exe -m pip_audit` | Vulnerabilidades conocidas (revalidada el 2026-07-29) | `No known vulnerabilities found`; el paquete local `simulador-ev3` no está publicado en PyPI y quedó fuera de auditoría. |
| `.\.venv\Scripts\python.exe -m pip_audit` | Vulnerabilidades conocidas (2026-07-30) | `No known vulnerabilities found`; se mantiene la exclusión inevitable del paquete local `simulador-ev3` al no estar publicado en PyPI. |
| `docker version` / `docker build` | Construcción del artefacto Linux | **BLOCKED por ambiente**: Docker CLI no está instalado en esta estación. La revisión estática del `Dockerfile` confirmó Python 3.12, ejecución sin privilegios con usuario `ev3` y servidor Waitress; la construcción real debe ejecutarse en CI o en un equipo con Docker. |
| `winget install --id Docker.DockerDesktop --exact --accept-package-agreements --accept-source-agreements --silent` | Habilitar smoke Docker/Linux (2026-07-30) | **BLOCKED por permisos**: descargó Docker Desktop 4.84.0 y verificó el hash, pero el instalador solicitó elevación y finalizó con código `4294967291`. Docker CLI continúa no disponible. Un administrador debe completar la instalación y reiniciar si se solicita. |
| `.\scripts\build_release_windows.ps1 -PythonExe .\.venv\Scripts\python.exe` | Empaquetado oficial Windows (2026-07-30) | salida 0 en 25.4 s. Generó `dist\SimuladorEV3\SimuladorEV3.exe` (6,686,829 bytes) y copió `Documentos\Ejemplos` y `Documentos\Mundos`. Se observaron advertencias de entorno Conda, sin fallo de empaquetado. Falta ejecución en Windows limpio. |
| `.\.venv\Scripts\python.exe -m pytest tests\web\test_container_configuration.py tests\release -q` | Smoke de liberación y configuración de contenedor (2026-07-29) | 10 aprobadas en 11.91 s. Cubre ejemplos críticos, dispositivos, telemetría y la variable de entorno de producción del `Dockerfile`. No equivale a construir o ejecutar una imagen Docker ni a generar un artefacto Windows. |
| `.\.venv\Scripts\python.exe -m pytest tests\web\test_container_configuration.py -q` | Regresión estática del empaquetado Windows (2026-07-29) | **1 FAIL, 2 PASS**. `build_release_windows.ps1` elimina `SimuladorEV3.spec`; no se ejecutó el script para evitar esa operación destructiva. El fallo corresponde a QA-REG-013. |
| `.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py tests\web\test_container_configuration.py tests\release -q` | Regresión de contraste, empaquetado y release (2026-07-30) | 53 aprobadas en 50.98 s. QA-REG-012 aprobó 10 combinaciones de contraste Web; QA-REG-013 aprobó la conservación/uso de `SimuladorEV3.spec`. No se construyó contenedor ni `.exe`. |
| `.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py tests\web\test_container_configuration.py tests\release -q` | Regresión Web, contraste, empaquetado y release (2026-07-30) | 54 aprobadas en 53.57 s. Incluye `test_reset_hides_the_terminal_mission_result`, que verifica que una misión terminada no conserve ni reciba un resultado tardío tras “Detener y reiniciar” (QA-REG-006). |
| `.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py tests\web\test_container_configuration.py tests\release -q` | Regresión Web, pausa coherente, empaquetado y release (2026-07-30) | 54 aprobadas en 54.23 s. La telemetría recibe un snapshot actualizado al pausar y reanudar; `test_simulation_controls_follow_execution_state` comprueba que el estado de sesión y el de telemetría sean ambos `paused` (QA-REG-007). |
| `.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py tests\web\test_container_configuration.py tests\release -q` | Regresión Web de misión, pausa, depuración y reinicio (2026-07-30) | 56 aprobadas en 54.58 s. Incluye cobertura de resultado tardío de misión, telemetría pausada, reinicio desde breakpoint y recuperación de “Ultrasonido + obstáculos” (QA-REG-006/007/009/010). |
| `.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py tests\web\test_container_configuration.py tests\release tests\web\test_qa_world_crud.py -q` | Regresión Web integral de sesión, editor, ayuda y release (2026-07-30) | 59 aprobadas en 57.49 s. Cubre QA-REG-006/007/008/009/010/011, contraste Web y empaquetado estático. |
| `.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py tests\load tests\web\test_container_configuration.py tests\release tests\web\test_qa_world_crud.py tests\shared\test_ci_quality_matrix.py tests\shared\test_testing_documentation.py -q` | Campaña QA ampliada (2026-07-30) | 65 aprobadas en 58.50 s. Incluye E2E Web, CRUD, carga sostenida, empaquetado estático, release, documentación y el orden de foco Tab/Shift+Tab/Enter del menú. |
| `.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -k all_primary_menu_triggers -q` | Accesibilidad de barra completa Web (2026-07-30) | 1 aprobada en 3.79 s. Verifica las 10 entradas del menú principal en orden de tabulación real. |
| `$env:EV3_RUN_DESKTOP_E2E='1'; .\.venv\Scripts\python.exe -m pytest tests\e2e\test_desktop_pywinauto.py -q -rs` | E2E nativo Tkinter (revalidado el 2026-07-29) | **BLOCKED por ambiente**: 4 omitidas. La ventana de introducción y las tres pruebas siguientes agotaron espera porque esta sesión no expone un escritorio Windows visible. |
| `$env:EV3_RUN_DESKTOP_E2E='1'; .\.venv\Scripts\python.exe -m pytest tests\e2e\test_desktop_pywinauto.py -q -rs` | E2E nativo Tkinter (2026-07-30) | salida 0 con **4 omitidas en 46.75 s**. Pywinauto no pudo detectar la ventana de introducción ni un escritorio Windows visible; el bloqueo es del entorno de automatización. |
| `.\.venv\Scripts\python.exe -m pytest tests\load -q` | Carga controlada de sesiones Web (revalidada el 2026-07-29) | 2 aprobadas en 2.00 s. Crea ocho sesiones concurrentes y, en un caso separado, dos workers aislados; comprueba `/metrics` (solicitudes, sesiones, memoria, pico, cola y ticks). No sustituye una campaña sostenida con SLA. |
| `.\.venv\Scripts\python.exe -m pytest tests\load -q` | Carga Web sostenida y métricas operativas (2026-07-30) | 3 aprobadas en 1.71 s. Añade 12 altas/cargas en tres rondas paralelas y exige <2 s por operación y <5 s de campaña en `TESTING`; mide sesiones, latencia media, cola, memoria y ticks. |
| `.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -q` | E2E Web Chromium (2026-07-29) | 30 aprobadas en 32.78 s. Complementa la campaña visible; no invalida las regresiones manuales confirmadas. |
| `.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py tests\shared\test_ci_quality_matrix.py -q` | E2E Web y evidencia de fallo (revalidada el 2026-07-29) | 31 aprobadas en 33.28 s. Ante un fallo E2E, la fixture guarda captura completa, consola JSON y eventos de red fallidos/HTTP ≥400 en `artifacts/e2e-web`; CI publica ese directorio como artefacto `evidencia-e2e-web`. |

Durante la activación del capturador, Chromium bloqueó una instancia E2E en el
puerto efímero `1720` con `net::ERR_UNSAFE_PORT`. La evidencia se conservó en
`artifacts/e2e-web/`. Se corrigió `_free_port()` para seleccionar únicamente
puertos efímeros mayores o iguales a 20000 y la repetición completa fue
aprobada; se trata de infraestructura de prueba, no de un defecto del producto.
| `.\.venv\Scripts\python.exe -m pytest -m "security or performance or release" -q` | Selección seguridad, carga y liberación | 19 aprobadas. |

La campaña gráfica Web, su entorno, los flujos ejercitados y los límites de
cobertura manual se documentan en `campana_web_visible_2026-07-28.md`.

> Evidencia actual: 2026-07-25, Windows, Python 3.12.5, version `1.5.0`.
> Ejecucion realizada desde el entorno limpio `C:\temp\ev3-doc-verify-20260724`.

| Comando | Objetivo | Resultado |
|---|---|---|
| `py -3.12 -m pytest -q` | Suite completa | 689 aprobadas |
| `py -3.12 -m pytest --cov=simulador_ev3 --cov-report=term-missing -q` | Suite y cobertura | 689 aprobadas; 71.50% |
| `py -3.12 -m pytest tests/e2e/test_web_playwright.py -q` | E2E real Chromium | 20 aprobadas |
| `py -3.12 -m ruff check simulador_ev3 tests` | Lint | salida 0 |
| `py -3.12 -m mypy` | Tipado | 99 módulos, salida 0 |

Cobertura real registrada: 71.50% global; el umbral configurado es 70%.
Ruff, Mypy (99 modulos), Bandit y Pip-Audit finalizaron con codigo 0. Pip-Audit
emitio advertencias de deserializacion de cache y concluyo `No known vulnerabilities found`.

## Verificación de navegación Web–Tkinter — 2026-07-25

| Comando | Objetivo | Resultado |
|---|---|---|
| `.\.venv\Scripts\python.exe -m pytest -q` | Regresión completa, incluyendo navegación | 695 aprobadas, 1 omitida por escritorio no visible. |
| `.\.venv\Scripts\python.exe -m ruff check simulador_ev3 tests` | Estilo y errores estáticos | salida 0. |
| `.\.venv\Scripts\python.exe -m mypy` | Tipado global | 100 módulos, salida 0. |
| `$env:EV3_RUN_DESKTOP_E2E='1'; ... pytest tests/e2e/test_desktop_pywinauto.py -q` | Recorrido nativo Windows con ratón | Omitida: esta sesión automatizada no expone una ventana Windows visible. |

La prueba `desktop_e2e` inicia Tkinter y navega por **Ayuda → Manual de uso**
y **Mundos → Editor de mundos** mediante controles nativos cuando hay una
sesión gráfica local. No se ejecuta en CI ni en sesiones aisladas sin escritorio.

## Actualización de regresión — 2026-07-30

| Comando | Objetivo | Resultado |
|---|---|---|
| `.\\.venv\\Scripts\\python.exe -m pytest -q` | Regresión completa tras el ajuste de telemetría Tkinter | **802 aprobadas, 4 omitidas** en 103.79 s. Las omisiones corresponden exclusivamente a Pywinauto sin escritorio visible. |
| `.\\.venv\\Scripts\\python.exe -m pytest tests/ui/test_telemetry_layout_live.py tests/ui/test_ui.py -k "telemetry or responsive or layout" -q` | Geometría y estabilidad de telemetría | **10 aprobadas**. Incluye la cuadrícula estable 2×2 para motores A–D. |
| `capture_desktop_evidence.py --verify-layout` | Inspección visual de Tkinter | Capturas reales revisadas en claro/oscuro a 1280×800, y claro a 1024×768 y 1920×1080. El modo estrecho apila secciones para evitar texto recortado. |

La telemetría conserva los cuatro motores y cuatro sensores sin que una
lectura larga cambie el tamaño de las tarjetas. El bloque **Robot / Estado** se
mantiene bajo la LCD del EV3. La automatización E2E nativa permanece bloqueada
por la falta de un escritorio Windows visible, no por un fallo confirmado del
producto.

Bandit finaliza sin hallazgos usando la configuración oficial del repositorio,
que documenta el `exec` de scripts Pybricks y el `eval` de watches como
mecanismos deliberados del runtime sandbox. Tras actualizar las herramientas
del entorno, Pip-Audit finalizó con `No known vulnerabilities found`; omite
únicamente el paquete local `simulador-ev3`, que no está publicado en PyPI.

### Cobertura consolidada de la campaña (2026-07-30)

| Comando | Objetivo | Resultado |
|---|---|---|
| `.\\.venv\\Scripts\\python.exe -m pytest --cov=simulador_ev3 --cov-report=term-missing -q` | Regresión total y medición de cobertura | **802 aprobadas, 4 omitidas, 1 advertencia** en 150.35 s; cobertura global real de **71.36 %**, superior al umbral exigido de 70 %. |

La advertencia procede de `coverage` al no poder cargar su trazador C; la
medición se completó mediante el trazador Python y no afecta al resultado de
las pruebas. Las cuatro omisiones siguen correspondiendo exclusivamente a la
suite Pywinauto, bloqueada porque esta sesión no expone un escritorio Windows
detectable para esa herramienta.

### Smoke Docker/Linux local (2026-07-30)

| Comando | Objetivo | Resultado |
|---|---|---|
| `docker build --tag simulador-ev3:qa-local-20260730 .` | Construcción reproducible de la imagen Linux | **Aprobada**. Imagen basada en Python 3.12, con usuario no privilegiado `ev3`. |
| `docker run ... --publish 5051:5050 ...` + `curl http://127.0.0.1:5051/healthz` | Arranque y disponibilidad HTTP de producción | **Aprobada**. `/healthz` respondió HTTP 200 y `status: ok`. |

La primera ejecución reveló dos defectos de configuración: el smoke de CI
no inyectaba las variables de producción requeridas y Waitress escuchaba solo
en `127.0.0.1` dentro del contenedor. Se corrigieron sin exponer secretos:
el job usa un secreto efímero de CI y `SESSION_COOKIE_SECURE=true`, mientras
que el `Dockerfile` define `EV3_WEB_HOST=0.0.0.0` exclusivamente para la imagen
contenedorizada. La prueba estática de configuración aprobó 4/4.

| `.\\.venv\\Scripts\\python.exe -m pytest -q` | Regresión completa tras el smoke Docker | **803 aprobadas, 4 omitidas** en 99.02 s. Las omisiones son exclusivamente las pruebas Pywinauto que no pueden detectar el escritorio de esta sesión. |

### Campaña Tkinter visible revalidada (2026-07-30)

| Comando | Flujos ejercitados | Resultado |
|---|---|---|
| `python scripts/interactive_desktop_qa.py <caso>` | Motor A; motores A–D; S1/S4; DriveBase; bloqueo de menús durante ejecución; error de sintaxis; LCD; pausa, reanudación y reinicio | **8/8 ejecuciones completadas** contra una ventana Tkinter visible. Las capturas actualizadas se conservan en `Documentos/EVIDENCIA_TESTEO_INTEGRAL_TKINTER_2026-07-28/`. |

Esta evidencia es una validación gráfica real complementaria. La suite
Pywinauto se conserva como omisión del entorno porque no puede enumerar las
ventanas de esta sesión; no se ha marcado artificialmente como aprobada.

| `python scripts/interactive_desktop_qa.py pause-resume-reset` | Revalidación visible de pausa, reanudación y reinicio Tkinter | Aprobada el 2026-07-30. La captura `pausa_real.png` muestra `PAUSADO`, 0.800 s y tick 40; `reinicio_real.png` muestra `IDLE`, 0.000 s, tick 0 y robot restaurado a (20.0 cm, 20.0 cm, 0.0°). |
