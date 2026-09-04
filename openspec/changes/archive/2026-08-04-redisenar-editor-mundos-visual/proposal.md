# Propuesta: rediseñar editor de mundos visual

## Motivo

El editor de mundos permite crear y modificar escenarios, pero su interfaz
presenta controles técnicos y una barra de acciones saturada. Docentes y
estudiantes deben interpretar iconos sin ayuda, propiedades internas como
`asset_key` y coordenadas en píxeles, y no cuentan con una biblioteca
organizada ni con una forma clara de seleccionar objetos superpuestos.

Esto eleva la curva de aprendizaje y dificulta crear, validar y probar mundos
como parte de una actividad educativa.

## Cambio

Rediseñar el editor de mundos de Web y Tkinter como una herramienta visual con:

- Cabecera separada en acciones de archivo, edición y simulación.
- Biblioteca lateral de assets por categorías con búsqueda, nombres y ayudas.
- Lienzo principal con estado vacío guiado.
- Inspector de propiedades con unidades y nombres comprensibles.
- Configuración de tamaño de mundo en celdas, presets y equivalencia física.
- Lista de capas para seleccionar, bloquear, ocultar y reordenar objetos.
- Acciones contextuales coherentes y una única operación de eliminar.
- Tema claro/oscuro, navegación por teclado y diseño adaptable.

El rediseño debe conservar el formato JSON, reglas de validación, assets y
semántica de simulación actuales. Web y Tkinter deben mantener paridad
funcional para crear, editar, validar, guardar, cargar y probar mundos.

## Fuera de alcance

- Cambiar el esquema JSON o la versión de los mundos existentes.
- Modificar la física, colisiones o semántica de sensores.
- Introducir colaboración multiusuario, historial remoto o papelera.
- Alterar el flujo de ejecución de programas Pybricks fuera de la transición
  existente de mundo validado a simulación.
