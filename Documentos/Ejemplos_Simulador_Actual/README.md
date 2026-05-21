# Ejemplos para el simulador actual

Estos ejemplos estan pensados para las funcionalidades que ya se pueden probar en el simulador de escritorio y en la version web.

Incluyen:

- movimiento con `Motor`
- movimiento con `DriveBase`
- LED, pantalla y sonido del `EV3Brick`
- lectura basica de `UltrasonicSensor`, `ColorSensor`, `GyroSensor` y `TouchSensor`
- uso de `StopWatch`

Orden recomendado:

1. `01_movimiento_basico.py`
2. `02_cuadrado_drivebase.py`
3. `03_motores_individuales.py`
4. `04_brick_led_pantalla_sonido.py`
5. `05_ultrasonido_hasta_borde.py`
6. `06_color_sensor_superficie.py`
7. `07_giro_y_gyro.py`
8. `08_touch_hasta_colision.py`
9. `09_stopwatch_demo.py`

Notas:

- Los ejemplos de sensores avanzados dependen del mundo cargado.
- Estos ejemplos buscan funcionar bien incluso con el mundo por defecto.
- En la version web, los ejemplos principales se cargan desde el menu `Ejemplos` o desde el selector de la pagina `/`.
- Para validar escenarios completos, usar el menu `Escenarios` de la web o de la app Tkinter.
