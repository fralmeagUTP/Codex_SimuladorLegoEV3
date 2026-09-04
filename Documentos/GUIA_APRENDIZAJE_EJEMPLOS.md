# Guia de aprendizaje por etapas (Pybricks + Simulador EV3)

> Estado: actual al 2026-07-25. Version aplicable: `1.5.0`. Esta guia usa los
> recursos compartidos de `examples/` y `worlds/`, disponibles desde Web y Tkinter.

Esta guia propone un orden didactico para usar los ejemplos del simulador.

## Etapa 1 - Fundamentos del brick

1. `01_intro_led.py`: LED y temporizacion basica.
2. `02_intro_pantalla_altavoz.py`: LCD, altavoz y cronometro.

## Etapa 2 - Movimiento base

1. `03_movimiento_basico.py`: avance y giro con dos motores.
2. `04_movimiento_motores_individuales.py`: pivotes y control por encoder.
3. `05_drivebase_cuadrado.py`: trayectoria geometrica con `DriveBase`.
4. `06_drivebase_perfiles_aceleracion.py`: diferencias de perfiles dinamicos.

## Etapa 3 - Sensores esenciales

1. `07_sensor_tacto_reaccion.py`: reaccion por contacto.
2. `08_sensor_ultrasonido_frenado.py`: parada por distancia.
3. `09_sensor_color_stop.py`: eventos por color.
4. `10_sensores_combinados.py`: fusion tacto + ultrasonido + color.

## Etapa 4 - Control reactivo

1. `11_siguelineas_basico.py`: siguelineas proporcional.
2. `12_siguelineas_robusto.py`: robustez ante perdida de linea.
3. `13_colision_controlada.py`: prueba controlada de impacto.
4. `14_navegacion_hasta_pared.py`: navegacion por condicion de distancia.
5. `15_esquiva_obstaculos.py`: comportamiento evasivo.
6. `16_resolver_laberinto.py`: resolver laberinto con regla de mano derecha mejorada (sondeo lateral, anti-oscilacion y recuperacion de atascos).

## Etapa 5 - Funciones avanzadas soportadas por el emulador

1. `17_gyro_correccion_rumbo.py`: correccion de rumbo con `GyroSensor`.
2. `18_infrarrojo_beacon_seguidor.py`: seguimiento de baliza IR.
3. `19_motor_encoder_objetivos.py`: posiciones objetivo con `run_target`.
4. `20_motor_run_until_stalled.py`: cierre por estancamiento.
5. `21_drivebase_curva_estado.py`: arcos y telemetria de estado.
6. `22_stopwatch_mision_etapas.py`: mision por etapas con `StopWatch`.

## Recorrido guiado y evidencia docente

Además de los ejemplos, el Centro de ayuda propone recorridos verificables:
crear mundo, primera simulación, motores y sensores, depuración, misión,
trazas, tiempo máximo y diagnóstico. Marque cada paso cuando pueda comprobar
su resultado; reinicie la guía para repetir una práctica.

Para evaluación, conserve una captura del mundo, el programa final, el estado
terminal de la misión y una explicación de la lectura de un sensor. Las trazas
permiten comparar intentos, pero deben limpiarse al reiniciar antes de evaluar
un nuevo recorrido. Valide finalmente el comportamiento con el robot físico.

## Mundos sugeridos

1. `01_linea_negra_basica.json`: ideal para color y siguelineas.
2. `05_obstaculos_baliza_ir.json`: obstaculos generales y pruebas de reaccion.
3. `06_pasillo_gyro_rumbo.json`: pasillo para giro y rumbo con gyro.
4. `07_laberinto_v1.json`: primer laberinto para navegacion reactiva.
5. `12_radar_ultrasonido_360.json`: mundo recomendado para el radar 360.

## Evidencia y misiones

Para convertir un ejemplo en una actividad evaluable:

1. Selecciona el ejemplo y el mundo sugerido.
2. Ejecuta el programa con el perfil de simulacion indicado por el docente.
3. Inicia el registro desde **Diagnóstico > Trazas de simulación** antes de ejecutar.
4. Exporta la traza en JSON o CSV al finalizar.
5. Revisa la evidencia con los criterios de `Documentos/MISIONES_EVALUABLES.md`.

Las trazas contienen el comportamiento simulado y permiten revisar una actividad
sin depender de la interfaz usada. Antes de trasladar la solucion al robot real,
consultar `Documentos/DIFERENCIAS_SIMULADOR_ROBOT.md` y recalibrar sensores,
ruedas y umbrales del entorno fisico.
