# Mundos preset del simulador

Estos archivos JSON se pueden cargar desde el menu `Mundos` de la app de escritorio y desde la version web.

- `01_linea_negra.json`: superficie con linea negra para pruebas de `ColorSensor`.
- `02_obstaculos_beacon.json`: mundo con obstaculos y una baliza IR.

En la web:

- Abrir `http://127.0.0.1:5050/`.
- Seleccionar un mundo en el combo `Seleccionar mundo`.
- Pulsar `Cargar mundo`.

Tambien se puede abrir una URL directa:

```text
http://127.0.0.1:5050/?world=01_linea_negra.json
```

Los mundos creados desde `/worlds` se guardan tambien en esta carpeta si se usa la accion `Guardar`.
