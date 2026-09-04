# Diseño

`PybricksContext` expone un `pause_event` compartido con `RuntimeController`.
`tools.wait()` no descuenta su tiempo restante mientras el evento está activo
y conserva la comprobación inmediata de cancelación.

El `DesktopSessionAdapter` recibe snapshots del worker como eventos de sesión;
si el registro está activo los transfiere por la API pública de
`SimulationService` a `SimulationTrace`. La UI continúa aplicando los mismos
eventos sin depender de atributos privados.

La ventana principal mantiene una etiqueta explícita del mundo activo, pues el
modelo de física no conserva necesariamente el nombre del archivo. El diálogo
Acerca de calcula su geometría después de construir los widgets y la centra
respecto a la raíz.
