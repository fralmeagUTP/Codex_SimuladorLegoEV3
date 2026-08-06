# Índice de documentación

> Revisado: 2026-08-05. Versión distribuible: `1.5.0`. Estado del producto:
> **apta con observaciones**.

## Cómo usar este índice

- **Canónico:** describe el producto vigente y debe actualizarse con el código.
- **Especializado:** aplica a una plataforma o despliegue concreto.
- **Histórico:** evidencia fechada; no representa por sí sola el estado actual.
- **Normativo:** requisito OpenSpec que gobierna cambios futuros.

## Inicio y estado

| Documento | Tipo | Audiencia | Propósito |
|---|---|---|---|
| `README.md` | Canónico | Todos | Instalación, ejecución y mapa general. |
| `Documentos/ESTADO_ACTUAL_PROYECTO.md` | Canónico | Todos | Línea base vigente y dictamen de liberación. |
| `CHANGELOG.md` | Canónico | Todos | Cambios por versión publicada. |
| `ROADMAP.md` | Canónico | Producto/desarrollo | Capacidades completadas y trabajo futuro. |
| `CONTRIBUTING.md` | Canónico | Contribuidores | Flujo OpenSpec, pruebas y documentación. |

## Estudiantes y docentes

| Documento | Tipo | Propósito |
|---|---|---|
| `Documentos/MANUAL_DE_USO.md` | Canónico | Uso completo de Web y Tkinter. |
| `Documentos/GUIA_APRENDIZAJE_EJEMPLOS.md` | Canónico | Ruta didáctica por ejemplos. |
| `Documentos/MISIONES_EVALUABLES.md` | Canónico | Misiones, criterios y resultados. |
| `Documentos/DIFERENCIAS_SIMULADOR_ROBOT.md` | Canónico | Límites frente a Pybricks/EV3 físico. |
| `Documentos/SEGURIDAD_Y_USO_EN_AULA.md` | Canónico | Uso responsable y controles de aula. |
| `Documentos/Ejemplos_Simulador_Actual/README.md` | Especializado | Catálogo didáctico conservado. |
| `worlds/README.md` y `Documentos/Mundos/README.md` | Canónico | Formato y recursos de mundos. |

## Arquitectura y desarrollo

| Documento | Tipo | Propósito |
|---|---|---|
| `Documentos/ARQUITECTURA_C4.md` | Canónico | Contexto, contenedores, componentes y flujos. |
| `Documentos/REFERENCIA_CONFIGURACION.md` | Canónico | Variables, seguridad y observabilidad. |
| `Documentos/MATRIZ_PARIDAD_CIERRE_WEB_TKINTER.md` | Canónico | Catálogo funcional cerrado Web/Tkinter. |
| `Documentos/MATRIZ_PARIDAD_VISUAL_WEB_TKINTER.md` | Canónico | Reglas de diseño y evidencia visual. |
| `openspec/project.md` | Normativo | Contexto y principios del producto. |
| `openspec/specs/` | Normativo | Requisitos base vigentes. |
| `openspec/changes/` | Normativo/histórico | Cambios activos y archivados. |
| `openspec/use-cases/` | Normativo | Casos de uso compartidos. |

## Instalación, operación y despliegue

| Documento | Tipo | Plataforma |
|---|---|---|
| `Documentos/GUIA_OPERACION_WINDOWS.md` | Canónico | Web y Tkinter local. |
| `Documentos/GUIA_WEB_FLASK_WINDOWS.md` | Especializado | Web Windows/Waitress. |
| `Documentos/GUIA_RELEASE_WINDOWS.md` | Especializado | Paquete Tkinter Windows. |
| `Documentos/GUIA_DESPLIEGUE_LINUX.md` | Canónico | Contenedor Linux. |
| `Documentos/GUIA_INSTALACION_CPANEL.md` | Especializado | cPanel. |
| `Documentos/CHECKLIST_POST_DEPLOY_CPANEL.md` | Especializado | Verificación cPanel. |
| `Documentos/PLAYBOOK_FILE_MIRROR_CPANEL_SHARED.md` | Especializado | Sesiones por archivos. |
| `Documentos/PLAYBOOK_REDIS_CPANEL_FASE3.md` | Especializado | Redis. |

## Manuales técnicos y derechos de autor

| Documento | Tipo | Propósito |
|---|---|---|
| `Documentos/MANUAL_TECNICO_ESCRITORIO.html` | Canónico | Arquitectura y operación técnica Tkinter. |
| `Documentos/MANUAL_TECNICO_WEB.html` | Canónico | Arquitectura, sesiones y operación Web. |
| `Documentos/ANEXO_EXPEDIENTE_DERECHOS_AUTOR.md` | Especializado | Lista de evidencia a completar por el titular. |
| `Documentos/PLANTILLA_DOCUMENTACION.md` | Especializado | Plantilla para nuevos documentos. |

Los manuales apoyan la preparación técnica, pero no sustituyen asesoría legal ni
constituyen por sí mismos un registro de derechos de autor.

## Calidad y liberación

| Documento | Tipo | Propósito |
|---|---|---|
| `Documentos/CONTROLES_CALIDAD.md` | Canónico | Herramientas y compuertas. |
| `Documentos/CHECKLIST_QA_RELEASE.md` | Canónico | Lista de liberación reproducible. |
| `docs/testing/estrategia_pruebas.md` | Canónico | Estrategia por nivel y ambiente. |
| `docs/testing/inventario_funcional.md` | Canónico | Capacidades y riesgos. |
| `docs/testing/casos_prueba.md` | Canónico | Casos críticos. |
| `docs/testing/matriz_trazabilidad.md` | Canónico | Requisitos, riesgos y pruebas. |
| `docs/testing/reporte_ejecucion.md` | Canónico + histórico fechado | Registro acumulado de ejecuciones. |
| `Documentos/INFORME_PRELIBERACION_PARIDAD_2026-08-04.md` | Histórico final | Dictamen actualizado el 2026-08-05. |
| `Documentos/LINEA_BASE_PARIDAD_2026-08-04.md` | Histórico final | Evidencia técnica del cierre. |
| `Documentos/INFORME_LIBERACION_WEB_2026-08-04.md` | Histórico | Liberación Web. |
| `Documentos/INFORME_ACTUALIZACION_DOCUMENTAL_2026-08-05.md` | Histórico | Evidencia de esta sincronización integral. |
| `Documentos/RELEASE_NOTES_v*.md` | Histórico | Notas de cada versión. |

Los demás archivos `INFORME_*`, `REPORTE_*`, `EVIDENCIA_*` y documentos de
`docs/testing/` con fecha explícita son históricos. Se conservan sin reescribir
sus resultados; el estado vigente siempre se consulta en
`Documentos/ESTADO_ACTUAL_PROYECTO.md`.

## Fuentes ejecutables

| Elemento | Fuente de verdad |
|---|---|
| Versión | `simulador_ev3/_version.py` |
| Dependencias y calidad | `pyproject.toml` |
| Inicio Web | `scripts/start_web.ps1` / `scripts/start_web.cmd` |
| Inicio Tkinter | módulo `simulador_ev3.ui.main_window` |
| Despliegue Linux | `Dockerfile` |
| CI | `.github/workflows/quality.yml` y `.github/workflows/tests.yml` |
| Configuración Web | `simulador_ev3/web/config.py` |

## Regla de mantenimiento

Todo cambio que modifique versión, comando, interfaz, contrato, dependencia,
configuración, despliegue o resultado de calidad debe actualizar el documento
canónico afectado y este índice. Toda cifra de pruebas debe indicar fecha,
entorno y comando; nunca se presenta evidencia histórica como resultado actual.
