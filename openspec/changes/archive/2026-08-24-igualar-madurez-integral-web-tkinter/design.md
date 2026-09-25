## Contexto

La arquitectura actual ya comparte `SimulationSession`, worker aislado,
snapshots y dominio EV3. La Web dispone además de rutas HTTP, sesiones de
usuario, métricas y soporte móvil; Tkinter aporta distribución local y widgets
nativos. El objetivo no es forzar los mismos componentes técnicos, sino que
ambas plataformas alcancen la misma capacidad observable y didáctica.

## Objetivos

- Garantizar el mismo catálogo aplicable de capacidades y resultados de
  dominio.
- Alcanzar una puntuación MMI mínima de 9.5/10 en cada interfaz, sin ocultar
  limitaciones de plataforma.
- Mantener una única fuente de verdad para estados, contenido educativo, ayuda,
  tokens visuales, criterios de evaluación y telemetría diagnóstica.
- Poder comparar calidad y uso real con evidencia repetible por plataforma.

## No objetivos

- No se requiere identidad píxel a píxel entre HTML/CSS y Tkinter.
- No se transforma Tkinter en una aplicación web ni se elimina la adaptación
  nativa de archivos, ventanas, teclado o móvil.
- No se expone un servidor HTTP local de escritorio como requisito para
  considerarlo observable.

## Modelo de madurez de interfaz

Cada dimensión se califica con evidencia, no por percepción. Una plataforma no
podrá declararse al mismo nivel si falla una compuerta obligatoria.

| Dimensión | Evidencia exigida | Umbral de cierre |
|---|---|---:|
| Arquitectura | puertos compartidos, ausencia de acceso privado entre UI y runtime, contratos | 9.5 |
| Diseño y accesibilidad | tokens, jerarquía, tema, foco, teclado, contraste, tamaños y assets | 9.5 |
| Funcionalidad | matriz de casos y snapshots equivalentes | 100 % aplicable |
| Pedagogía y ayuda | objetivos, práctica, recuperación y progreso equivalentes | 100 % catálogo |
| Calidad y pruebas | contrato, unidad, integración, E2E real y regresiones | 100 % críticos PASS |
| Observabilidad | diagnóstico correlacionado, trazas y exportación adaptada | 100 % datos comunes |

Las únicas excepciones permitidas serán `N/A` por plataforma, documentadas con
una alternativa equivalente. Por ejemplo, móvil solo aplica a Web, mientras
que instalador nativo solo aplica a escritorio.

## Arquitectura objetivo

```text
              Catálogos compartidos
  casos de uso | ayuda | pedagogía | tokens | diagnósticos
                         |
         Presentation / UI Ports versionados
                         |
             SimulationSession compartida
                         |
          Worker aislado + dominio Pybricks
                         |
     Snapshot + LearningState + ObservabilitySnapshot
                         |
             Web adapters / Tkinter adapters
```

1. `LearningState` contendrá actividad, objetivo, avance, resultado,
   recuperación sugerida y versión del contenido. Debe persistirse localmente
   con privacidad explícita y sin mezclar datos de usuarios diferentes.
2. `ObservabilitySnapshot` contendrá `session_id`, `command_id`, `worker_id`,
   estado, duración, tick, cola, error y correlación de traza cuando exista.
   La Web lo expone en API/métricas; Tkinter lo presenta en diagnóstico local y
   permite exportación segura.
3. Las UI consultarán catálogos compartidos de controles, ayuda, actividades y
   criterios, evitando textos, reglas y estados duplicados.
4. Las adaptaciones visuales nativas se documentarán en una matriz; ninguna
   podrá cambiar validaciones, resultado de dominio o recuperación.
5. `AssetCatalog` será la fuente única de verdad de recurso, identificador,
   versión, licencia, hash, variantes, tamaño lógico y destino de empaquetado.
   Web y Tkinter resolverán el mismo identificador, aunque difieran los
   mecanismos de carga de archivo, bundle o estático.

## Estrategia de activos visuales

1. Inventariar todos los assets usados por Tkinter, Web, editor de mundos,
   ayuda y pantallas de inicio, incluidas figuras de robot, obstáculos, metas,
   pisos, haces, iconos y tutoriales.
2. Definir un manifiesto de assets con hash SHA-256, variante, dimensiones y
   ubicación canónica. Una actualización de figura o imagen deberá modificar
   ese manifiesto y las dos distribuciones en el mismo cambio.
3. Generar una prueba que compare el manifiesto con los archivos entregados en
   `web/static`, el bundle PyInstaller y el paquete de distribución.
4. Usar capturas de referencia para comprobar que el mismo `asset_id` conserva
   proporción y significado en ambas UI. Solo se permiten variaciones de
   escalado y antialiasing documentadas.

## Estrategia de verificación

- Pruebas de contrato validan el mismo comando, estado, snapshot, ayuda,
  progreso y diagnóstico en ambas UI.
- Playwright y Pywinauto ejercitan los mismos identificadores de casos de uso;
  cada resultado queda trazado a la matriz común.
- Comparación visual verifica estructura, jerarquía, contraste y estados; no
  compara píxeles de widgets nativos.
- CI publica reporte MMI, capturas y artefactos de diagnóstico por plataforma.

## Riesgos y mitigaciones

- Tkinter depende de una sesión gráfica: mantener pruebas nativas en Windows y
  un protocolo manual bloqueante cuando falte el escritorio.
- La observabilidad Web puede ser más rica por su servidor: definir datos
  mínimos comunes y un adaptador de exportación para escritorio.
- El contenido pedagógico puede divergir: mantener un catálogo versionado y
  pruebas que comparen identificadores, pasos y resultados.
- La equivalencia visual puede generar cambios costosos: medir semántica,
  accesibilidad y jerarquía antes que detalles de bordes nativos.
- Los assets pueden duplicarse o quedar desactualizados entre bundles: un
  manifiesto con hashes y una prueba de empaquetado detectará diferencias antes
  de liberar.

## Plan de migración

1. Publicar línea base MMI y registrar todas las brechas.
2. Extraer catálogos y DTOs comunes sin cambiar el comportamiento existente.
3. Adaptar Web y Tkinter por dimensión, empezando por brechas críticas.
4. Añadir pruebas y compuertas; corregir cualquier divergencia descubierta.
5. Actualizar manuales y emitir informe de liberación solo con evidencia de
   ambas plataformas.
