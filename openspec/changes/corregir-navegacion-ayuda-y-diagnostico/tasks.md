# Tareas: aclarar la navegación de ayuda y el diagnóstico

## Fase 1 — Inventario y contrato

- [x] 1.1 Documentar los destinos actuales de cada comando de Ayuda en Web y
  Tkinter y confirmar los datos seguros que integran el diagnóstico.
- [x] 1.2 Definir el catálogo compartido de los seis comandos, etiquetas,
  orden, atajos y destinos de ayuda contextual.
- [x] 1.3 Definir el esquema versionado del archivo de diagnóstico JSON y la
  política de exclusión de datos sensibles.

## Fase 2 — Menús y guía rápida

- [x] 2.1 Sustituir `Guía de actividad` por `Guía rápida: primera simulación`
  en la Web y conservar el enlace a `first-simulation`.
- [x] 2.2 Añadir la misma guía rápida al menú Ayuda de Tkinter y enfocar la
  entrada equivalente del Centro de ayuda.
- [x] 2.3 Reordenar ambos menús según el contrato y conservar navegación por
  teclado, foco visible y bloqueo de menú durante ejecución si aplica.

## Fase 3 — Diagnóstico y exportación

- [x] 3.1 Crear en la Web una vista/modal de diagnóstico con título, contenido
  y controles propios, sin reutilizar visualmente `Acerca de`.
- [x] 3.2 Implementar descarga de diagnóstico JSON en la Web con `Blob` y
  gestión segura de errores/cancelación.
- [x] 3.3 Alinear el formato mostrado y exportado por Tkinter con el esquema
  común, conservando su selector de archivo nativo.
- [x] 3.4 Comprobar que `Acerca de` queda limitado a información institucional.

## Fase 4 — Pruebas y documentación

- [x] 4.1 Añadir pruebas unitarias de catálogo, orden, destinos, anclas y
  ausencia de datos sensibles.
- [x] 4.2 Añadir pruebas de interfaz Tkinter para guía rápida, diagnóstico,
  exportación y Escape.
- [x] 4.3 Añadir Playwright para abrir cada comando Web, validar títulos,
  exportar JSON y evitar diálogos apilados.
- [x] 4.4 Actualizar el manual de uso y la matriz de paridad de interfaces.
- [x] 4.5 Ejecutar Ruff, pruebas relevantes y registrar evidencia de Web y
  Tkinter en claro y oscuro.

## Fase 5 — Referencia editorial externa

- [x] 5.1 Añadir el enlace seguro al libro de LEGO EV3 en los menús Ayuda de
  Web y Tkinter, con apertura en una nueva pestaña o navegador predeterminado.
- [x] 5.2 Verificar la URL, la apertura segura en Web y la delegación al
  navegador del sistema en Tkinter.
