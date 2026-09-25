# Diseño: ayuda didáctica, interactiva y visualmente fiel

## Diagnóstico de partida

| Aspecto | Estado actual | Riesgo |
|---|---|---|
| Contenido | 7 guías con pasos, resultado y recuperación | Sin objetivos medibles ni práctica por nivel |
| Recursos visuales Web | 3 SVG genéricos repetidos | La guía puede enseñar una pantalla distinta de la real |
| Recursos visuales Tkinter | Esquemas Canvas simplificados | No permite reconocer controles reales |
| Navegación | Búsqueda, categorías y enlaces de destino | No conserva progreso ni retorno contextual |
| Accesibilidad | Texto alternativo y teclado base | Faltan transcripción de anotaciones y estado de avance |
| Mantenimiento | Sin manifiesto ni fecha de captura | Las imágenes se desactualizan sin detección |

## Modelo de contenido compartido

Cada `HelpGuide` evolucionará sin romper identificadores existentes con:

- `learning_objective`, `level` (`inicial`, `intermedio`, `avanzado`) y tiempo;
- pasos con identificador, instrucción, comprobación observable y contexto;
- visuales por plataforma y tema: ruta, alt, transcripción, versión de UI,
  resolución y fecha de captura;
- ejemplo Pybricks opcional, copiable pero nunca ejecutado automáticamente;
- relaciones de prerrequisito, guía siguiente y una advertencia explícita de
  simulador frente a robot físico.

## Experiencia de aprendizaje

Cada guía mostrará meta y duración, requisitos, paso actual, una captura
anotada con transcripción, comprobación que el usuario marca de forma explícita,
práctica contextual, recuperación y siguiente guía. El progreso se guardará
localmente por plataforma y guía; podrá borrarse y no llevará código, sesiones
ni datos personales.

## Capturas canónicas

Se creará `simulador_ev3/shared/help_visual_manifest.py` y un directorio de
assets de ayuda. Cada entrada declarará guía, plataforma, tema, resolución,
hash o versión de UI, fecha, origen, anotaciones, alt, transcripción, licencia
interna y revisión visual. Se usarán datos sintéticos y capturadores
reproducibles: Playwright para Web y el capturador gráfico existente para
Tkinter. CI validará cobertura, archivos, proporción, metadatos y privacidad.

## Paridad y accesibilidad

Web y Tkinter comparten catálogo, objetivos, pasos, resultados, recuperación y
progreso semántico. Web usa tarjetas, indicador y botón de copia; Tkinter usa
widgets nativos equivalentes. Tab, Shift+Tab, Enter, Espacio y Escape deben
funcionar; claro/oscuro debe conservar contraste AA; las anotaciones no pueden
depender únicamente del color; y se respetará `prefers-reduced-motion`.
