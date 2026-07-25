# Tareas: actualizar documentacion integral

## Fase 1 - Inventario y normas

- [x] 1.1 Inventariar README, `Documentos/`, `docs/`, OpenSpec, configuracion y guias de scripts.
- [x] 1.2 Clasificar cada documento como actual, historico, obsoleto, duplicado o faltante.
- [x] 1.3 Publicar indice documental con audiencia, responsable, version y fecha de revision.
- [x] 1.4 Definir plantilla comun para guias operativas, evidencias y compatibilidad.

## Fase 2 - Documentacion de producto e interfaces

- [x] 2.1 Actualizar README: proposito, arquitectura resumida, requisitos, instalacion, comandos y enlaces.
- [x] 2.2 Actualizar manual Web y Tkinter con simulacion, mundos, depuracion, trazas y perfiles.
- [x] 2.3 Actualizar guia de mundos, ejemplos, misiones y exportacion de resultados disponibles.
- [x] 2.4 Documentar accesibilidad, atajos, temas, controles nativos y solucion de problemas.

## Fase 3 - Arquitectura, API y seguridad

- [x] 3.1 Actualizar C4, `SimulationSession`, worker aislado y recuperacion de fallos.
- [x] 3.2 Actualizar matriz Pybricks y diferencias simulador-robot por perfil.
- [x] 3.3 Documentar sandbox, secretos, perfiles, datos locales y uso seguro en aula.
- [x] 3.4 Actualizar variables de entorno, health, metricas y trazas.

## Fase 4 - Operacion, calidad y despliegue

- [x] 4.1 Consolidar instalacion y operacion local Windows de escritorio y Web.
- [x] 4.2 Actualizar despliegue Linux/contenedor sin privilegios, backup y recuperacion. El `Dockerfile` usa `EV3_WEB_APP_ENV=production`, coherente con la configuración y las guías operativas.
- [x] 4.3 Actualizar guia de pruebas: unitarias, integracion, UI, E2E, carga, cobertura y analisis estatico.
- [x] 4.4 Actualizar CI, quality gates, evidencias y procedimiento de release.

## Fase 5 - Verificacion y gobernanza

- [x] 5.1 Crear pruebas de enlaces, version, comandos y referencias cruzadas.
- [x] 5.2 Marcar o reubicar evidencia historica sin alterar su contenido verificable. La clasificacion se publica en `Documentos/INDICE_DOCUMENTACION.md`; los archivos de evidencia conservan fecha y contenido original.
- [x] 5.3 Añadir checklist de documentacion a contribucion y cierre OpenSpec.
- [x] 5.4 Ejecutar comandos documentados en entorno limpio y registrar resultados. Entorno `C:\temp\ev3-doc-verify-20260724`: 689 pruebas, cobertura 71.50%, Ruff, Mypy, Bandit y Pip-Audit con codigo 0.

## Criterios de cierre

- La documentacion actual refleja la version distribuible y resultados vigentes.
- Todos los enlaces locales y comandos criticos pasan verificacion automatica.
- Cada interfaz, plataforma y perfil soportado tiene guia de uso y limites.
- Los documentos historicos siguen accesibles, fechados y no se confunden con el estado actual.
