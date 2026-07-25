# Diferencias entre simulador y robot LEGO EV3

> Estado: actual al 2026-07-24. Version aplicable: `1.4.0`. La matriz de
> conformidad detallada esta en
> `openspec/changes/elevar-calidad-y-paridad-de-interfaz/pybricks-conformance-v1.md`.

El simulador enseña la API Pybricks y permite validar lógica, pero no reemplaza
las pruebas finales en un robot físico.

| Área | Simulador | Robot físico | Recomendación docente |
|---|---|---|---|
| Tiempo | Tick nominal fijo de 20 ms. | Depende de batería, carga y firmware. | Tolerar variación y no depender de milisegundos exactos. |
| Motores | Perfiles ideal, realista y calibrado. | Fricción, holgura y rueda afectan distancia. | Calibrar diámetro/track y validar recorridos. |
| Sensores | Ruido determinista configurable. | Luz ambiente, superficie y orientación cambian lecturas. | Usar umbrales, promedios y calibración. |
| Ultrasonido | Modelo geométrico de obstáculos. | Tiene ecos, ángulos muertos y materiales absorbentes. | Diseñar márgenes de seguridad. |
| Botones/pantalla/audio | Eventos y renderizado virtuales. | Dependen del brick y del usuario. | Confirmar interacción manual en hardware. |
| Seguridad | Worker limitado y sin red. | El robot puede moverse físicamente. | Probar a baja velocidad, con zona despejada y parada accesible. |

## Criterio de entrega

Una misión se considera terminada cuando pasa en el perfil **ideal**, conserva
comportamiento aceptable en **realista** y se verifica en el robot físico con
los parámetros de calibración documentados.

## Perfiles de simulacion

| Perfil | Uso esperado | Limite principal |
|---|---|---|
| `ideal` | Introduccion, depuracion y pruebas deterministas. | No representa ruido ni desgaste fisico. |
| `realistic` | Validar tolerancia a friccion, ruido y traccion simulados. | El ruido es reproducible, no una medicion del aula real. |
| `calibrated` | Ajustar parametros de una actividad concreta. | Requiere que el docente documente la calibracion aplicada. |

## Compatibilidad Pybricks declarada

El simulador soporta las clases y metodos incluidos en la matriz de conformidad.
Entre ellos se encuentran `Motor.run_target`, `Motor.run_until_stalled`,
`DriveBase.curve`, `ColorSensor.hsv` y `detectable_colors`. El soporte significa
comportamiento simulado probado, no identidad byte a byte con firmware Pybricks.

Una API no incluida en la matriz se considera fuera de alcance y no debe usarse
como requisito de una actividad. Cuando un ejemplo se traslade a hardware, se
deben verificar especialmente velocidad, parada, distancia, orientacion, ruido
de sensores y condiciones de iluminacion.
