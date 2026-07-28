# Informe de testeo funcional integral — aplicación Web

Fecha: 2026-07-27  
Conclusión: **no apta para liberar sin correcciones**.

## 1. Entorno

| Dato | Valor |
|---|---|
| URL | `http://127.0.0.1:5050/` |
| Rama / commit | `agent/release-1-5-0` / `90ee112` |
| Python | 3.12.5 (`.venv`) |
| Servidor | `python -m simulador_ev3.web.waitress_server` ya iniciado en la estación |
| Navegador real | Navegador integrado Codex (motor Chromium; no se pudo certificar específicamente Chrome o Edge) |
| Resoluciones inspeccionadas | 1920×1080, 1280×800, 1024×768 y 390×844 |
| Temas | Claro y oscuro; persistencia tras recarga comprobada |

La campaña se ejecutó contra la instancia real mediante interacción de navegador, no mediante lectura de código. Se mantuvo el criterio de no corregir defectos durante la ejecución.

## 2. Alcance y resultado

| ID | Caso | Resultado | Observación |
|---|---|---|---|
| WEB-01 | Carga inicial, controles y telemetría | FAIL | Tras carga/recarga se observó telemetría `ACTIVO`, tiempo/tick no nulos mientras el pie indica `ready`. |
| WEB-02 | Ejecución de script Pybricks válido con LCD y `wait` | FAIL | El editor llegó a `finished`, pero la telemetría permaneció en `ACTIVO` con tick/tiempo anteriores y LCD sin contenido visible. |
| WEB-03 | Detener y reiniciar | FAIL | El pie de sesión quedó en `created`, pero canvas/telemetría no volvieron visualmente a estado inicial. |
| WEB-04 | Menú Misiones y carga de misión | PASS parcial | Se desplegaron las tres misiones y se cargó «Sigue líneas básico». El estado visual heredado impide aceptar el flujo completo. |
| WEB-05 | Menús principales | PASS parcial | Archivo, Ejemplos, Mundos, Escenarios, Misiones, Tema, Fidelidad, Tiempo máximo, Trazas y Ayuda están presentes; se abrió Misiones y Tema. No se ejecutó cada comando individual. |
| WEB-06 | Tema claro/oscuro y persistencia | PASS | Cambio de oscuro a claro y vuelta a oscuro; el tema oscuro persistió tras recargar. |
| WEB-07 | Respuesta visual escritorio | PASS parcial | No se detectó overflow horizontal global en 1920×1080, 1280×800 ni 1024×768. |
| WEB-08 | Respuesta visual móvil 390×844 | FAIL | «Haces ON» queda recortado en el borde derecho; el canvas conserva 980 px de ancho de escritorio. |
| WEB-09 | Navegación básica por teclado | BLOCKED | El foco no se trasladó con la automatización del navegador; se requiere sesión manual en Chrome/Edge para confirmar Tab, Shift+Tab, Enter y Escape. |
| WEB-10 | Consola del navegador | PASS | No se capturaron mensajes `warning` ni `error` durante los recorridos realizados. |
| WEB-11 | Red/servidor | BLOCKED | El navegador no expone un registro de red/servidor completo; no se infiere ausencia de errores. |
| WEB-12 | Editor de mundos: CRUD e inválidos | BLOCKED | No se completó un CRUD real ni entradas malformadas en esta campaña. |
| WEB-13 | Sensores, colisiones, trazas, zoom y paneo | BLOCKED | No se verificaron todos los escenarios controlados por el estado de sincronización defectuoso. |
| WEB-14 | Pausa, reanudar, depuración, bucle infinito y >30 s | BLOCKED | Requiere recorrido adicional después de resolver WEB-01/WEB-02. |
| WEB-15 | Paridad Web/Tkinter | FAIL | Tkinter muestra telemetría y resultado terminal coherentes en las validaciones previas; Web conserva estado visual anterior tras terminar o reiniciar. |

## 3. Hallazgos priorizados

### WEB-F-001 — Alta: telemetría Web no sincroniza con estados terminales

**Pasos:** abrir la aplicación, ejecutar el script mínimo:

```python
from pybricks.hubs import EV3Brick
from pybricks.tools import wait
ev3 = EV3Brick()
ev3.screen.print("QA OK")
wait(100)
```

**Esperado:** al finalizar, editor, LCD y telemetría muestran el mismo snapshot terminal (`FINALIZADO`, tiempo/tick actuales).  
**Observado:** el editor indicó `finished`, pero telemetría quedó `ACTIVO`, `0.04 s`, tick `2`; la LCD no mostró `QA OK`.  
**Impacto:** el alumno recibe estado de robot y resultado de programa desactualizados.  
**Evidencia:** captura interactiva de la campaña; DOM expuso simultáneamente `Estado: finished` y resumen `ACTIVO`.

### WEB-F-002 — Alta: «Detener y reiniciar» no refresca canvas ni telemetría

**Pasos:** ejecutar el script anterior y pulsar **Detener y reiniciar**.  
**Esperado:** robot, tick, tiempo, LCD y paneles retornan al estado inicial del mundo.  
**Observado:** el pie cambió a `Estado: created`, pero persistieron `ACTIVO`, `0.04 s`, tick `2` y la representación previa.  
**Impacto:** contradice la semántica del control y puede causar evaluaciones visuales erróneas.  
**Evidencia:** DOM posterior al reinicio y captura de la campaña.

### WEB-F-003 — Media: diseño móvil corta herramienta del mapa

**Pasos:** establecer viewport 390×844 y abrir la página.  
**Esperado:** todos los controles del mapa quedan accesibles y no truncados.  
**Observado:** el botón **Haces ON** queda cortado en el borde derecho. El canvas informa 980 px de ancho, propio de escritorio.  
**Impacto:** controles no utilizables en móvil; experiencia educativa degradada.  
**Evidencia:** captura móvil realizada durante la campaña.

## 4. Riesgos de liberación

- Alto riesgo de interpretación errónea: el resultado del programa puede ser terminal mientras telemetría, LCD y canvas muestran datos anteriores.
- Alto riesgo funcional en reinicio: un estudiante no puede confirmar visualmente que el mundo volvió al inicio.
- Riesgo medio de accesibilidad/responsividad móvil por controles recortados.
- Cobertura manual incompleta de CRUD, sensores, modos de depuración y fallos de red; esos ámbitos permanecen BLOCKED y no deben considerarse aprobados.

## 5. Recomendaciones

1. Investigar la secuencia SSE/snapshot tras `finished`, `error`, `reset` y carga de sesión. Un único estado terminal debe actualizar canvas, LCD, telemetría y barra de estado desde el mismo snapshot/generación.
2. Añadir prueba E2E Web de regresión: ejecutar script corto, esperar `finished`, verificar simultáneamente estado terminal, tick/tiempo no obsoletos, LCD y posición; repetir tras reset.
3. En móvil, aplicar breakpoint que reorganice herramientas del mapa y limite/escale el canvas al contenedor sin cortar botones.
4. Ejecutar una segunda campaña en Chrome o Edge con DevTools para registrar red, consola, foco de teclado y todos los comandos de menú.
5. Completar CRUD de mundos, escenarios con sensores, pausa/reanudar, trazas, errores de sintaxis, límite configurable y bucle cancelable una vez resuelta la sincronización base.

## 6. Conclusión

La aplicación Web **no está apta para liberar** en su estado observado. La carga básica, menús y persistencia de tema funcionan parcialmente, pero los defectos de sincronización terminal y reinicio afectan los flujos educativos centrales. La campaña debe repetirse para los casos BLOCKED después de corregir WEB-F-001 y WEB-F-002.
