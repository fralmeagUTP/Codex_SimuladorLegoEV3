## 1. Línea base y gobierno de paridad

- [x] 1.1 Definir el manifiesto MMI con dimensiones, pesos, umbrales, evidencia, aplicabilidad y responsable.
- [x] 1.2 Inventariar capacidades, menús, atajos, diálogos, recursos, errores y estados de Web/Tkinter; clasificar equivalente, adaptación o brecha.
- [x] 1.3 Registrar línea base reproducible por commit, Windows, Python, navegador, resoluciones y tema.
- [x] 1.4 Crear una regla de CI que impida cerrar una capacidad aplicable sin fila de paridad y evidencia en ambas UI.

## 2. Arquitectura común

- [x] 2.1 Auditar y eliminar accesos UI a detalles privados de runtime, motor o widgets ajenos.
- [x] 2.2 Versionar los puertos `PresentationPort`, `LearningPort` y `ObservabilityPort` sobre `SimulationSession`.
- [x] 2.3 Extraer catálogos compartidos de controles, estados, mensajes, atajos, validaciones y rutas de recuperación.
- [x] 2.4 Convertir los controladores Web y presentadores Tkinter en adaptadores del mismo contrato, con pruebas de contrato cruzadas.
- [x] 2.5 Documentar y probar las adaptaciones legítimas de navegador, móvil, archivos, ventanas e instalación.
- [x] 2.6 Inventariar los assets actuales de Web y Tkinter, identificar figuras o imágenes divergentes y definir `AssetCatalog` como manifiesto versionado único.
- [x] 2.7 Migrar Web y Tkinter para resolver el mismo `asset_id`, eliminar duplicados obsoletos de forma segura y conservar atribución/licencia cuando aplique.

## 3. Diseño, accesibilidad y navegación

- [x] 3.1 Consolidar tokens semánticos compartidos para color, tipografía, espaciado, foco, estado y contraste.
- [x] 3.2 Implementar el mismo mapa de navegación, nombres, orden de controles y estados habilitado/deshabilitado cuando la capacidad sea aplicable.
- [x] 3.3 Verificar claro/oscuro, foco visible, tabulación, Enter, Escape, lectores de pantalla y contraste en ambas UI.
- [x] 3.4 Validar Web en 1920×1080, 1280×800, 1024×768 y 390×844; validar Tkinter en 1920×1080, 1280×800 y 1024×768.
- [x] 3.5 Implementar comparación visual semántica y capturas de referencia para simulación, mundos, ayuda, depuración, telemetría y diálogos.
- [x] 3.6 Añadir pruebas de integridad de assets: hash, presencia, dimensiones y equivalencia de los recursos incluidos en Web, PyInstaller, ZIP e instalador.

## 4. Funcionalidad y consistencia de sesión

- [x] 4.1 Ejecutar y automatizar el catálogo completo de ejemplos, mundos, escenarios, misiones y operaciones de editor en ambas UI.
- [x] 4.2 Verificar equivalencia de ejecutar, pausar, reanudar, depurar, cancelar, reiniciar, tiempo máximo, trazas, perfiles y errores.
- [x] 4.3 Comparar snapshots de robot, canvas, LCD, telemetría, brick, editor y estado global en transiciones críticas.
- [x] 4.4 Añadir regresiones cruzadas para eventos tardíos, caída/recuperación de worker, cambio de mundo y restauración de sesión.
- [x] 4.5 Tratar toda diferencia descubierta como defecto con severidad, evidencia y caso de regresión o protocolo manual reproducible.

## 5. Experiencia didáctica, pedagógica y ayuda

- [x] 5.1 Definir un catálogo común de rutas de aprendizaje, objetivos, prerrequisitos, ejemplos, prácticas, criterios y recuperación.
- [x] 5.2 Mostrar en ambas UI objetivo actual, progreso, resultado comprensible y siguiente actividad sugerida.
- [x] 5.3 Unificar ayuda rápida, ayuda contextual, manual técnico, glosario Pybricks y mensajes de error orientados a aprendizaje.
- [x] 5.4 Añadir prácticas evaluables con retroalimentación formativa, sin presentar simulación como sustituto de validación en robot físico.
- [x] 5.5 Validar con pruebas de contenido que identificadores, pasos, criterios y enlaces sean equivalentes entre Web y Tkinter.

## 6. Observabilidad y soporte

- [x] 6.1 Definir `ObservabilitySnapshot` común y sus reglas de privacidad, retención y correlación.
- [x] 6.2 Exponer en Web métricas, trazas y diagnóstico de sesión; exponer en Tkinter panel/diálogo diagnóstico y exportación local equivalente.
- [x] 6.3 Correlacionar ejecución, error, timeout, cancelación, recuperación y resultado pedagógico por sesión, comando y worker.
- [x] 6.4 Añadir pruebas de integridad de métricas, exportación, redacción de secretos y recuperación ante fallo.
- [x] 6.5 Documentar la guía de diagnóstico para docente, soporte local y operación de servidor.

## 7. Calidad, pruebas y liberación

- [x] 7.1 Definir mínimos por capa para unidad, integración, contrato, UI/E2E, accesibilidad, seguridad, rendimiento, resiliencia, empaquetado y despliegue.
- [x] 7.2 Ejecutar Playwright y Pywinauto con el mismo manifiesto de casos y publicar una matriz PASS/FAIL/BLOCKED por plataforma.
- [x] 7.3 Mantener Ruff, Mypy, Bandit, Pip-Audit, cobertura y pruebas de mutación/escenarios críticos como compuertas de CI.
- [x] 7.4 Ejecutar pruebas de carga multiusuario Web y pruebas de ejecución local/empaquetada Tkinter; comparar límites y recuperación.
- [x] 7.5 Generar informe MMI, actualizar documentación canónica y emitir decisión de liberación trazable al commit.
