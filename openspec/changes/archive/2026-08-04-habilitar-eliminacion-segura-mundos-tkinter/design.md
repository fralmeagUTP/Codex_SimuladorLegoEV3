# Diseño

La ventana conserva `current_path` después de guardar o abrir. La nueva acción
solo se habilita cuando esa ruta existe, es un archivo JSON y está dentro del
directorio de mundos configurado. Antes de borrar se resuelve la ruta y se
rechaza cualquier ruta fuera del directorio o un mundo preestablecido incluido
en el catálogo. Tras confirmación positiva se elimina con `Path.unlink()`, se
restablece un mundo vacío y se limpia `current_path`.

La interfaz no usa rutas calculadas desde el texto del usuario: siempre actúa
sobre la ruta publicada por el servicio tras una carga o guardado correcto.
