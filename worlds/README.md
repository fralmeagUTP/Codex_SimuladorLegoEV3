# Mundos preset del simulador

Estos archivos JSON se pueden cargar desde el menu `Mundos` de la app de escritorio y desde la version web.

- `01_linea_negra_basica.json`: superficie con linea negra para pruebas de `ColorSensor`.
- `05_obstaculos_baliza_ir.json`: mundo con obstaculos y una baliza IR.
- `06_pasillo_gyro_rumbo.json`: pasillo para practicar correccion de rumbo con `GyroSensor`.
- `07_laberinto_v1.json` a `11_laberinto_v5.json`: variantes progresivas de laberinto.
- `02_linea_negra_v1.json` a `04_linea_negra_v3.json`: variantes de pista de linea negra.
- `12_radar_ultrasonido_360.json`: mundo para el ejemplo de radar con ultrasonido.

En la web:

- Abrir `http://127.0.0.1:5050/`.
- Seleccionar un mundo en el combo `Seleccionar mundo`.
- Pulsar `Cargar mundo`.

Tambien se puede abrir una URL directa:

```text
http://127.0.0.1:5050/?world=01_linea_negra_basica.json
```

Los mundos creados desde `/worlds` se guardan tambien en esta carpeta si se usa la accion `Guardar`.
