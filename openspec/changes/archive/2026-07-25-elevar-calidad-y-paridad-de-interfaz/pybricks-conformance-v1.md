# Matriz de conformidad Pybricks v1

Esta matriz define la API EV3 que el simulador declara soportada. Cada fila se
verifica en `tests/pybricks_api/test_pybricks_api.py`; una API no incluida se
considera fuera de alcance y no debe anunciarse como compatible.

| Módulo | Clase | Métodos soportados | Prueba de conformidad |
| --- | --- | --- | --- |
| `pybricks.parameters` | `Port`, `Color`, `Stop`, `Direction`, `Button` | valores y conversiones | `TestParameters` |
| `pybricks.ev3devices` | `Motor` | `run`, `dc`, `stop`, `brake`, `hold`, `run_time`, `run_angle`, `run_target`, `track_target`, `run_until_stalled`, `angle`, `speed`, `reset_angle`, `done`, `stalled`, `load`, `settings`, `close` | `TestMotorAPI` |
| `pybricks.ev3devices` | Sensores | `pressed`, `distance`, `presence`, `color`, `reflection`, `ambient`, `hsv`, `detectable_colors`, `angle`, `speed`, `reset_angle`, `beacon` | `TestSensorAPI` |
| `pybricks.robotics` | `DriveBase` | `drive`, `stop`, `brake`, `straight`, `turn`, `curve`, `settings`, `done`, `stalled`, `state`, `distance`, `angle`, `reset` | `TestDriveBaseAPI` |
| `pybricks.hubs` | `EV3Brick` | luz, altavoz, pantalla y botones | `TestEV3BrickAPI` |
| `pybricks.tools` | `StopWatch`, `wait` | tiempo, pausa, reinicio y espera | `TestWait`, `TestStopWatch` |

Los valores de parada `COAST`, `BRAKE` y `HOLD` se prueban además en
`tests/domain/robot/test_motor_model.py` y `tests/domain/robot/test_drivebase_model.py`.
