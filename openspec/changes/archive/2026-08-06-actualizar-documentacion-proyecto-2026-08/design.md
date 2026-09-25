## Context

El repositorio contiene guías canónicas y numerosos informes fechados. Las guías
deben describir el producto vigente; los informes deben conservarse como evidencia
histórica inmutable. La versión se obtiene de `simulador_ev3/_version.py`.

## Goals / Non-Goals

**Goals:**

- Ofrecer una ruta documental clara para usuarios, docentes, desarrollo, QA y
  operación.
- Alinear comandos y arquitectura con archivos ejecutables del repositorio.
- Registrar el cierre de paridad y la evidencia de QA del 5 de agosto de 2026.
- Detectar referencias locales rotas y deriva de versión mediante pruebas.

**Non-Goals:**

- Reescribir informes históricos o alterar sus resultados.
- Cambiar funcionalidades del simulador.
- Presentar el manual técnico como certificación o registro legal.

## Decisions

1. `README.md` será la entrada operativa corta y
   `Documentos/INDICE_DOCUMENTACION.md` el catálogo por audiencia.
2. `Documentos/ESTADO_ACTUAL_PROYECTO.md` concentrará la línea base vigente,
   evitando mezclarla con reportes históricos.
3. Los comandos se documentarán con `.venv` y alternativas explícitas; el puerto
   predeterminado seguirá siendo 5050 y los puertos distintos se marcarán como
   elecciones de ejecución.
4. La evidencia vigente enlazará al informe final de paridad; las cifras antiguas
   conservarán fecha y carácter histórico.
5. Las pruebas documentales validarán archivos canónicos, versión, índice y
   referencias Markdown locales.

## Risks / Trade-offs

- Un inventario exhaustivo puede volver a derivar; se mitiga con una prueba de
  enlaces y con la regla de actualización en contribuciones.
- Los manuales HTML son extensos; se actualizarán metadatos y referencias
  canónicas sin rediseñarlos ni alterar su finalidad probatoria.

## Migration Plan

Actualizar documentos canónicos, ejecutar validadores, cerrar tareas y archivar
el cambio. No requiere migración de datos ni despliegue.
