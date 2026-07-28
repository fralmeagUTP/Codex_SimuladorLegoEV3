# Matriz inicial de paridad visual Web–Tkinter

La Web es la fuente de verdad. Esta matriz define el inventario de Fase 1.

| Área Web | Control/estado | Equivalente Tkinter | Estado objetivo |
|---|---|---|---|
| Barra de simulación | Ejecutar, Pausar, Reanudar, Detener y reiniciar | Barra superior | Mismo orden y color semántico |
| Mundo | Nombre, pose, haces, zoom y ubicar robot | Panel Entorno de simulación | Misma etiqueta y estados |
| Editor | Ejecutar, Detener, Depurar, Paso, watches | Editor de código | Mismo catálogo y disponibilidad |
| Depuración | Pausas, paso, continuar, puntos de interrupción y watches | Editor de código | Mismo estado y atajos disponibles |
| Telemetría | Robot, motores, sensores | Telemetría | Misma jerarquía de información |
| Brick | LED, LCD, altavoz | EV3 Brick | Misma paleta y encabezados |
| Menús | Tema, Fidelidad, Trazas, Ayuda | Barra de menú | Mismos nombres y orden |

Las áreas de verificación comunes son: simulación, mundo, editor,
depuración, telemetría, brick, tema, fidelidad, trazas y ayuda.

## Evidencia reproducible

La referencia Web de esta iteración se generó en
`Documentos/EVIDENCIA_PARIDAD_2026-07-24/web` con:

```powershell
py -3.12 scripts/capture_web_evidence.py --output-dir Documentos/EVIDENCIA_PARIDAD_2026-07-24/web
```

El capturador valida los paneles visibles, el mapa, menús, editor,
telemetría/brick, editor de mundos y sesiones independientes.

La referencia Tkinter equivalente se obtiene en una sesión gráfica de Windows
sin restaurar ni modificar la sesión guardada del usuario:

```powershell
py -3.12 scripts/capture_desktop_evidence.py --output-dir Documentos/EVIDENCIA_PARIDAD_2026-07-24/tkinter
```

Las capturas de esta iteración están en `Documentos/EVIDENCIA_PARIDAD_2026-07-24/tkinter`.
La inspección comparativa confirmó que la barra integrada, las etiquetas de
ejecución, el selector de haces y la lectura de pose ya tienen equivalente
visual. Permanecen diferencias propias de los controles nativos Tkinter en
bordes, scrollbars y distribución adaptable de paneles. La telemetría de
Tkinter se organiza ahora en las mismas columnas Robot, Motores y Sensores de
la Web; las tarjetas inactivas siguen visibles para conservar el detalle de
puertos del escritorio.

## Tokens iniciales

## Resultado de comparacion 2026-07-24

La comparacion se realizo sobre `simulacion_light_1280x800.png` de ambas
carpetas de evidencia. Confirma el menu claro, el orden de controles, la
division Mundo/Editor aproximada 58/42, la barra de acciones, pose, haces,
depuracion, telemetria Robot/Motores/Sensores, Brick y franja de estado.
Los colores de menu claro y oscuro proceden de las reglas CSS `.menu-bar` de
la Web.

La tolerancia de posicion para controles equivalentes es de 4 px en la
geometria de referencia (`1280x800`), salvo la redistribucion permitida por
el sistema de paneles de Tkinter. Se mantienen diferencias de renderizado
nativo en bordes de botones, menus desplegables y barras de desplazamiento;
no cambian la funcionalidad ni la semantica visual.

## Comparación automatizable

La comparación se ejecuta sobre las regiones de encabezado, barra de acciones,
mundo, editor, telemetría y brick de la captura `1280x800`. Las máscaras PNG
blancas excluyen las diferencias nativas permitidas (bordes, menús y barras de
desplazamiento); los demás píxeles se comparan con diferencia RGB normalizada
máxima de `0.08`.

```powershell
py -3.12 scripts/compare_visual_evidence.py referencia.png actual.png --mask mascara_nativa.png --threshold 0.08
```

La tarea `desktop-visual` de `.github/workflows/quality.yml` genera una
captura Tkinter de referencia en Windows, la compara con el umbral anterior y
publica el directorio `artifacts/tkinter` aun cuando la comparación falle.

El mapa Tkinter tambien aplica la paleta de fondo y rejilla de la Web en los
temas claro y oscuro. Los colores del robot, LCD y objetos del mundo no se
tematizan: representan elementos fisicos de la simulacion.

`background`, `surface`, `surface_muted`, `text`, `text_muted`, `primary`,
`primary_active`, `danger`, `success`, `warning`, `focus` y `border` se definen
en `simulador_ev3.shared.ui_design_tokens` para los temas claro y oscuro.
Los tokens `toolbar` y `toolbar_text` replican especificamente la barra de
menus de la Web en ambos temas.
