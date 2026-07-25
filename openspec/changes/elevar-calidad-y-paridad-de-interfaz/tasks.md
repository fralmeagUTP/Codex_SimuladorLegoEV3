# Tareas: elevar calidad, seguridad y paridad de interfaces

## Fase 1 — Contratos y línea base

- [x] 1.1 Crear catálogo versionado de casos de uso compartidos Web/Tkinter.
- [x] 1.2 Definir DTO y máquina de estados de sesión, transiciones y códigos de error.
- [x] 1.3 Corregir auto-reinicio para conservar snapshot y eventos finales.
- [x] 1.4 Unificar la fuente de versión del paquete, documentación y health endpoint.
- [x] 1.5 Exigir clave secreta y timeout positivo en configuración de producción.

## Fase 2 — Paridad estricta de interfaces

- [x] 2.1 Inventariar funciones actuales de web y Tkinter y publicar matriz de paridad.
- [x] 2.2 Implementar en la interfaz que carezca de ellos todos los controles de simulación, mundo, depuración, brick, telemetría y recuperación presentes en la otra.
- [x] 2.3 Extraer adaptadores de UI para que ambas usen los mismos casos de uso y DTOs.
- [x] 2.4 Añadir pruebas de contrato y E2E equivalentes para ambas interfaces.
- [x] 2.5 Bloquear en CI cambios que introduzcan funciones en una sola interfaz.

## Fase 3 — Runtime seguro y robusto

- [x] 3.1 Diseñar protocolo IPC de worker, comandos, snapshots, depuración y cancelación.
- [x] 3.2 Implementar worker aislado compatible con Windows y Linux bajo feature flag.
- [x] 3.3 Aplicar límites de recursos, filesystem, red y privilegios del worker.
- [x] 3.4 Migrar sesiones web y Tkinter al worker aislado.
- [x] 3.5 Ejecutar pruebas de escape, timeout, cancelación y recuperación de worker.

## Fase 4 — Fidelidad EV3 y trazabilidad

- [x] 4.1 Centralizar semántica de motor y drivebase, incluidos `COAST`, `BRAKE`, `HOLD` y curvas.
- [x] 4.2 Eliminar accesos de API a atributos privados de dominio.
- [x] 4.3 Implementar perfiles ideal, realista y calibrado para física y sensores.
- [x] 4.4 Crear matriz Pybricks y pruebas de conformidad por método soportado.
- [x] 4.5 Añadir exportación/reproducción de trazas JSON/CSV y modo de tick paso a paso.

## Fase 5 — Calidad operativa y educativa

- [x] 5.1 Modularizar frontend web y separar responsabilidades de aplicación.
- [x] 5.2 Añadir logging estructurado, métricas, health y dashboards operativos.
- [x] 5.3 Configurar Ruff, formatter, type checker, Bandit, auditoría de dependencias y pre-commit.
- [x] 5.4 Ampliar CI a Python 3.11/3.12, Windows/Linux, con cobertura y carga.
- [x] 5.5 Crear misiones evaluables, criterios docentes y documentación simulador-vs-robot.

## Dependencias y criterios de cierre

- Las fases 2 y 3 dependen de 1.1 y 1.2.
- La migración final de worker depende de pruebas de paridad aprobadas.
- Una tarea sólo se marca completada con pruebas automatizadas y actualización de
  especificación/matriz de compatibilidad cuando corresponda.
- La propuesta se archivará únicamente cuando ambas UI cumplan todos los casos de
  uso compartidos y los quality gates estén en verde.

## Avance de implementación

- 2026-07-23: la finalización natural ahora publica el estado `finished` en vez
  de reutilizar `stopped`. Web ya no reinicia automáticamente al recibir ese
  estado, conserva el snapshot final del brick y permite reinicio manual. Tkinter
  presenta el mismo estado funcional como `Finalizado`. La suite completa aprobó
  591 pruebas.
- 2026-07-23: se añadió el contrato compartido de estados `created`, `ready`,
  `running`, `paused`, `finished`, `stopped`, `error`, `timed_out`, `resetting`
  y `expired`. Los timeouts ahora terminan como `timed_out` en Web y Tkinter, sin
  ser reemplazados por `stopped`. Falta versionar el DTO y hacer cumplir todas las
  transiciones desde una única fachada. La suite completa aprobó 595 pruebas.
- 2026-07-23: el contrato de snapshot se versionó como `snapshot_version: 1`.
  Las respuestas web ahora incluyen una secuencia de sesión y cada snapshot una
  generación que cambia tras `reset`; el cliente web descarta snapshots de una
  generación o tick anterior. Falta centralizar la aplicación obligatoria de
  todas las transiciones en una única fachada. La suite completa aprobó 597 pruebas.
- 2026-07-23: `SimulationSession` centraliza ahora todas sus transiciones en
  `_transition(...)`, validada contra el contrato compartido. Callbacks tardíos
  que contradicen un estado terminal se descartan. La tarea 1.2 queda completada;
  la suite completa aprobó 598 pruebas.
- 2026-07-23: se creó el catálogo versionado v1 de casos de uso de paridad en
  `openspec/use-cases/interface-parity-v1.md` y su contrato verificable en
  `shared/use_case_catalog.py`. La tarea 1.1 queda completada; la suite completa
  aprobó 600 pruebas.
- 2026-07-23: la versión distribuible `1.3.4` se centralizó en `_version.py` y
  se usa en el metadato dinámico del paquete, Web, Tkinter, assets y `/healthz`.
  Se actualizaron README, changelog y guías operativas relevantes. La tarea 1.4
  queda completada; la suite completa aprobó 602 pruebas.
- 2026-07-23: el modo `production` ahora valida una clave secreta propia de al
  menos 32 caracteres, un timeout positivo por script y cookies seguras para
  HTTPS. Los valores de desarrollo y de pruebas continúan disponibles sin
  cambio. La configuración y las pruebas de arranque quedaron documentadas en
  la guía operativa y README.
- 2026-07-23: se auditó el catálogo de casos de uso contra Web y Tkinter en
  `openspec/use-cases/matriz-paridad-actual-v1.md`. El resultado identifica
  recuperación de sesión y watches como parciales, además de tema y controles
  visuales exclusivos que la tarea 2.2 deberá normalizar. La matriz queda
  protegida por una prueba que exige cubrir todo identificador del catálogo.
- 2026-07-23: Tkinter incorporó el campo de configuración y el panel de
  resultados de `watches`, conectado a `SimulationService`; así UC-DEBUG-01
  queda en paridad funcional con Web. Las pruebas UI verifican normalización,
  propagación y presentación de valores y errores. La tarea 2.2 sigue en curso.
- 2026-07-23: Tkinter incorporó tema claro/oscuro persistente con preferencias
  locales; se elimina esa diferencia aplicable frente a la selección persistente
  de tema de Web. Queda por resolver y delimitar la recuperación de sesión.
- 2026-07-23: Tkinter ahora recupera al iniciar el script, mundo disponible,
  breakpoints y watches que guardó al cerrar. Con esto UC-SESSION-01 también
  alcanza paridad funcional y la tarea 2.2 queda completada. La siguiente tarea
  es extraer adaptadores de UI y después reforzar contratos/E2E equivalentes.
- 2026-07-23: Tkinter usa `DesktopSessionAdapter` como fachada local y existe
  una primera prueba de ejecución cruzada Web/Tkinter que compara `finished` y
  el snapshot del brick para el mismo programa. La extracción de adaptadores de
  mundo y depuración sigue pendiente para completar la tarea 2.3.
- 2026-07-23: se completó la extracción inicial de adaptadores compartidos:
  sesión local de escritorio, normalización de depuración y proyección de
  `editor_spec` usada por Web y Tkinter. La suite completa aprobó 616 pruebas;
  la tarea 2.4 continuará con contratos y recorridos de interfaz equivalentes.
- 2026-07-23: las pruebas de contrato cruzado cubren ejecución finalizada,
  configuración de depuración, pausa/reanudación y colocación de assets de
  mundo. Las colocaciones publican además `x_px/y_px` junto a los campos
  compatibles `x/y`. La suite completa aprobó 619 pruebas; faltan recorridos
  GUI/E2E emparejados para cerrar la tarea 2.4.
- 2026-07-23: se cerró 2.4 usando los recorridos E2E Web existentes, las
  pruebas UI sin pantalla de Tkinter y los contratos cruzados de ejecución,
  depuración y mundo. El gate 2.5 se incorpora a la suite CI: cada caso de uso
  no planificado debe figurar como `Completa` en la matriz de paridad.
- 2026-07-23: se definió `ipc-worker-protocol-v1`, con envoltura versionada,
  comandos, eventos, correlación, cancelación, terminación y recuperación para
  el worker aislado multiplataforma. La tarea 3.1 queda completada.
- 2026-07-24: se implementó `IsolatedRuntimeWorker` con `spawn`, IPC
  versionado, ciclo de vida, snapshots, errores, directorio temporal privado,
  red bloqueada y ejecución real de scripts mediante `SimulationService` dentro
  del proceso. Permanece protegido por `EV3_WORKER_ISOLATION_ENABLED`; 3.2 queda
  completada. Faltan límites del sistema y migración de sesiones para 3.3/3.4.
- 2026-07-24: se cubrieron escape de red y filesystem, protocolo incompatible,
  timeout de script no cooperativo, cancelación IPC y recuperación tras reinicio
  forzado del worker. La tarea 3.5 queda completada con pruebas automatizadas.
- 2026-07-24: se habilitaron Ruff, formatter, Mypy, Bandit, Pip-Audit y
  pre-commit. CI ejecuta la matriz Python 3.11/3.12 sobre Windows/Linux,
  cobertura y una carga concurrente acotada de sesiones. Las verificaciones
  estáticas y las pruebas de carga quedan automatizadas; 5.3 y 5.4 completadas.
- 2026-07-24: el worker impone límites de CPU/memoria disponibles por SO,
  directorio temporal privado, red bloqueada, guardas de filesystem, saneamiento
  de secretos heredados y rechazo de ejecución elevada. La tarea 3.3 queda
  completada con pruebas de aislamiento del worker.
- 2026-07-24: el frontend Web separó módulos de API, tema, menú, canvas,
  perfiles, trazas, audio del brick y diálogo informativo; la aplicación
  principal conserva la orquestación. Las pruebas verifican la carga y
  delegación de los módulos extraídos. La tarea 5.1 queda completada.
- 2026-07-24: al activar el aislamiento, Web y Tkinter delegan la ejecución,
  pausa, reanudación, parada y depuración al worker. Los eventos del worker
  alimentan snapshots, estados, errores y depuración; el servicio local queda
  acotado a edición/proyección de mundos. La tarea 3.4 queda completada con
  pruebas de ruta de ejecución para ambas interfaces.
