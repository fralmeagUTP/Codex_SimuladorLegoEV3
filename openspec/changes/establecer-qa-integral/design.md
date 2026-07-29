# Diseño: programa integral de pruebas y calidad

## Principios

1. Una afirmación `PASS` requiere evidencia de ejecución del tipo de prueba
   declarado. Leer código, inspeccionar DOM o usar mocks no aprueba una UI real.
2. Las pruebas se ubican en la capa más baja que detecte el defecto; los E2E se
   reservan para recorridos críticos y paridad visible.
3. Cada defecto confirmado se convierte en una prueba de regresión estable,
   evitando mocks que oculten el comportamiento real.
4. Los datos de prueba son sintéticos, temporales y aislados; mundos del usuario
   no se sobrescriben ni eliminan.
5. Un caso sin acceso, ambiente o instrumentación suficiente se marca
   `BLOCKED`, con causa y acción de desbloqueo.

## Arquitectura de pruebas

| Nivel | Propósito | Herramientas previstas | Evidencia |
|---|---|---|---|
| Estático | estilo, tipos, dependencias, vulnerabilidades | Ruff, Mypy, Bandit, Pip-Audit | salida CI |
| Unitario/dominio | reglas deterministas de motor, mundo, sensores y runtime | pytest | resultados y cobertura |
| Integración/contrato | sesión, worker, persistencia, API y contratos Web/Tkinter | pytest, Flask test client | respuestas y snapshots |
| UI/E2E | recorridos visibles de usuario | Playwright, pyautogui/pywinauto | capturas, consola, red |
| No funcional | accesibilidad, rendimiento, carga y resiliencia | Playwright, pytest, scripts de carga | métricas y umbrales |
| Release | empaquetado, despliegue y recuperación | Docker, PyInstaller, smoke tests | artefactos y logs |

## Catálogo mínimo de riesgos

- **Crítico:** ejecución de scripts, cancelación, reinicio, aislamiento de
  sesiones, persistencia de mundos y seguridad del runtime.
- **Alto:** sincronía canvas/LCD/telemetría/editor, errores terminales,
  menú durante ejecución, Pybricks soportado, colisiones y sensores.
- **Medio:** accesibilidad, tema, responsividad, ayudas, diálogos, rendimiento
  en escenarios complejos y empaquetado.
- **Bajo:** textos auxiliares y detalles visuales no bloqueantes.

## Evidencia y datos

Cada campaña genera un directorio fechado bajo `Documentos/EVIDENCIA_*` y un
informe con entorno, rama, commit, comandos, resultados, capturas, errores de
consola/red, limitaciones y conclusión. Los casos UI críticos guardan captura
antes/después del resultado terminal y vinculan `session_id` cuando exista.

## Compuerta de calidad

La liberación es **apta** solo si pasan las suites obligatorias, no hay defectos
críticos/altos abiertos sin aceptación explícita y los flujos críticos Web y
Tkinter tienen evidencia real vigente. Será **apta con observaciones** si los
riesgos medios/bajos están documentados y aceptados. Será **no apta** si falta
evidencia crítica, falla seguridad/instalación o existe desincronización de
estado terminal.

## Manejo de plataformas

- Web: Chrome/Edge visible; escritorio 1920×1080, 1280×800, 1024×768 y móvil
  390×844; claro y oscuro.
- Tkinter: Windows con sesión gráfica activa; intro, ventana maximizada,
  diálogos nativos, menús, editor y canvas.
- CI: matriz Python 3.11/3.12 y Windows/Linux cuando aplique. La indisponibilidad
  de escritorio activo no permite omitir silenciosamente E2E: deja el resultado
  `BLOCKED`.
