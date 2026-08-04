# Indice de documentacion

> Estado: actual al 2026-07-25. Version distribuible: `1.5.0`, leida desde
> `simulador_ev3/_version.py`. Responsable: equipo del proyecto.

## Convenciones

- **Actual**: fuente operativa que debe mantenerse al cambiar el producto.
- **Historico**: evidencia valida de una fecha concreta; no describe por si sola el estado actual.
- **En revision**: requiere actualizacion en este cambio OpenSpec.
- **Especializado**: documento para una plataforma, entorno o migracion concreta.

## Producto e interfaces

| Documento | Estado | Audiencia | Proxima accion |
|---|---|---|---|
| `README.md` | En revision | Todos | Actualizar comandos y resultados de calidad. |
| `CHANGELOG.md` | Actual | Todos | Mantener por version publicada. |
| `CONTRIBUTING.md` | Actual | Contribuidores | Checklist de calidad, OpenSpec y documentacion. |
| `ROADMAP.md` | En revision | Producto y desarrollo | Separar hitos actuales de resultados historicos. |
| `Documentos/MANUAL_DE_USO.md` | En revision | Estudiante y docente | Alinear fecha, sesiones, paridad y problemas. |
| `Documentos/GUIA_APRENDIZAJE_EJEMPLOS.md` | En revision | Estudiante y docente | Verificar ejemplos y rutas actuales. |
| `Documentos/MISIONES_EVALUABLES.md` | Actual | Docente | Mantener con el catalogo de misiones. |
| `Documentos/Ejemplos_Simulador_Actual/README.md` | En revision | Estudiante | Validar referencias Web y Tkinter. |
| `worlds/README.md` y `Documentos/Mundos/README.md` | Actual | Estudiante | Mantener formato y rutas de mundos. |

## Arquitectura, especificaciones y compatibilidad

| Documento | Estado | Audiencia | Proxima accion |
|---|---|---|---|
| `Documentos/ARQUITECTURA_C4.md` | En revision | Desarrollo | Completar contratos, worker y recuperacion. |
| `Documentos/DIFERENCIAS_SIMULADOR_ROBOT.md` | Actual | Docente y estudiante | Revisar al ampliar API Pybricks. |
| `Documentos/MANUAL_TECNICO_ESCRITORIO.html` | Actual | Soporte de aula, desarrollo y evaluador técnico | Manual HTML imprimible de Tkinter; completar versión liberada y hash antes de una entrega formal. |
| `Documentos/MANUAL_TECNICO_WEB.html` | Actual | Administración, desarrollo y evaluador técnico | Manual HTML imprimible de Flask; completar versión liberada y hash antes de una entrega formal. |
| `Documentos/SEGURIDAD_Y_USO_EN_AULA.md` | Actual | Docente y operacion | Mantener con sandbox y politica de secretos. |
| `Documentos/REFERENCIA_CONFIGURACION.md` | Actual | Operacion y desarrollo | Mantener con `web/config.py`. |
| `Documentos/MATRIZ_PARIDAD_VISUAL_WEB_TKINTER.md` | Actual | Desarrollo y QA | Mantener con evidencia visual. |
| `Documentos/SDD_MIGRACION_WEB_FLASK.md` | Historico | Desarrollo | Conservar como migracion. |
| `Documentos/SDD_DEBUGSTATE_PARIDAD_WEB_TKINTER.md` | Historico | Desarrollo | Conservar como antecedente. |
| `openspec/project.md` y `openspec/specs/` | Actual | Desarrollo | Fuente normativa base. |
| `openspec/use-cases/` | En revision | Desarrollo y QA | Cerrar auditoria de mundos y ayuda. |
| `openspec/changes/` | Actual | Desarrollo | Conservar propuestas, disenos, tareas y deltas. |

## Instalacion, operacion y despliegue

| Documento | Estado | Audiencia | Proxima accion |
|---|---|---|---|
| `Documentos/GUIA_WEB_FLASK_WINDOWS.md` | En revision | Operacion local | Validar comandos, variables y health. |
| `Documentos/GUIA_OPERACION_WINDOWS.md` | Actual | Estudiante y operacion local | Punto de entrada para Web y Tkinter. |
| `Documentos/GUIA_RELEASE_WINDOWS.md` | En revision | Release Windows | Actualizar version y distinguir Web de ejecutable. |
| `Documentos/GUIA_DESPLIEGUE_LINUX.md` | En revision | Operacion Linux | Corregir discrepancia de variable en Dockerfile. |
| `Documentos/GUIA_INSTALACION_CPANEL.md` | Especializado | Operacion cPanel | Revisar version Python y advertencias. |
| `Documentos/CHECKLIST_POST_DEPLOY_CPANEL.md` | Especializado | Operacion cPanel | Mantener con despliegue cPanel. |
| `Documentos/PLAYBOOK_*CPANEL*.md` | Historico | Operacion cPanel | Conservar como procedimientos fechados. |
| `Documentos/PLAN_TECNICO_MIGRACION_REDIS_FASES.md` | Historico | Desarrollo | Marcar resultados como historicos. |
| `Dockerfile`, `.dockerignore`, `scripts/start_web.*` | Actual | Operacion | Fuente ejecutable para guias. |

## Calidad, pruebas y releases

| Documento | Estado | Audiencia | Proxima accion |
|---|---|---|---|
| `Documentos/CONTROLES_CALIDAD.md` | Actual | Desarrollo y QA | Mantener con CI y herramientas. |
| `Documentos/CHECKLIST_QA_RELEASE.md` | En revision | QA y release | Actualizar version, comandos y gates. |
| `docs/testing/diagnostico.md` | Historico | QA | Conservar con fecha y enlazar reporte actual. |
| `docs/testing/inventario_funcional.md` | En revision | QA | Alinear con catalogo OpenSpec. |
| `docs/testing/estrategia_pruebas.md` | En revision | QA | Incluir worker, E2E y visual. |
| `docs/testing/casos_prueba.md` | En revision | QA | Mantener casos criticos verificables. |
| `docs/testing/matriz_trazabilidad.md` | En revision | QA | Relacionar requisitos OpenSpec y pruebas. |
| `docs/testing/reporte_ejecucion.md` | En revision | QA | Publicar resultado actual fechado. |
| `docs/testing/informe_prueba_manual_escritorio.md` | Historico | QA | Conservar evidencia manual fechada. |
| `Documentos/EVIDENCIA_QA_RELEASE_2026-05-20.md` | Historico | QA | No actualizar sus cifras; enlazar reporte actual. |
| `Documentos/INFORME_*` y `Documentos/REPORTE_*` fechados | Historico | QA | Conservar como evidencia. |
| `Documentos/RELEASE_NOTES_v*.md` | Historico | Usuarios | Mantener por version. |
| `.github/workflows/quality.yml`, `tests.yml` | Actual | Desarrollo | Fuente ejecutable de CI. |

## Configuracion y fuente de verdad

| Elemento | Estado | Uso documental |
|---|---|---|
| `simulador_ev3/_version.py` | Actual | Fuente unica de `APP_VERSION`. |
| `pyproject.toml` | Actual | Dependencias, herramientas y pruebas. |
| `requirements.txt` y `requirements-audit.txt` | Actual | Dependencias de ejecucion y auditoria. |
| `scripts/` | Actual | Comandos automatizados soportados. |
| `Documentos/EVIDENCIA_PARIDAD_2026-07-24/` | Historico fechado | Capturas de paridad visual. |

## Regla de actualizacion

Todo cambio que modifique un comando, interfaz, contrato, requisito, dependencia,
flujo de operacion o resultado de calidad debe actualizar este indice y el documento actual afectado.
Las evidencias historicas no se reescriben: se etiquetan con fecha, entorno y comando.
