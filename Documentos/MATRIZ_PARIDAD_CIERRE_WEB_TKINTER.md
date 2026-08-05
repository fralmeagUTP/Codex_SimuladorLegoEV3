# Matriz de paridad y cierre de liberación

**Cambio OpenSpec:** `cerrar-paridad-y-liberacion-ambas-apps`  
**Estado:** línea base; pendiente de ejecución real por plataforma.  
**Regla:** una fila sólo se marca `PASS` después de ejercitarla en la interfaz
indicada. `Automatizado` no sustituye la prueba manual real.

## Entornos objetivo

| ID | Plataforma | Entorno mínimo | Resoluciones / temas |
|---|---|---|---|
| ENV-WEB | Web | Chrome o Edge gráfico, servidor oficial del proyecto | 1920×1080, 1280×800, 1024×768, 390×844; claro y oscuro |
| ENV-DESK | Escritorio | Windows, Python soportado y sesión gráfica Tkinter | 1920×1080, 1280×800, 1024×768; claro y oscuro |

La política CI soporta Python 3.11 y 3.12 en Windows y Linux. La línea base
local de esta campaña usa Python 3.12.5, Chrome 150.0.7871.188 y Edge
151.0.4129.59; las versiones no se interpretan como un límite máximo de
compatibilidad.

## Catálogo funcional común

| ID | Capacidad | Web | Tkinter | Oráculo de paridad | Automatización existente | Estado de cierre |
|---|---|---:|---:|---|---|---|
| PAR-001 | Nuevo, abrir y guardar script | Sí | Sí | Editor y archivo resultante equivalentes | Web parcial | Pendiente manual |
| PAR-002 | Cargar 23 ejemplos | Sí | Sí | Código cargado corresponde al recurso | Web manual: 23/23 | Pendiente Tkinter |
| PAR-003 | Mundo vacío, archivo JSON, preestablecido y editor | Sí | Sí | Mundo, pose y entidades coinciden | Web manual: 12/12 + CRUD/E2E | Pendiente comparación Tkinter |
| PAR-004 | Escenarios línea, ultrasonido, brick y radar | Sí | Sí | Mundo y programa asociado coinciden | Web manual: 4/4 | Pendiente Tkinter y ejecución |
| PAR-005 | Misiones disponibles | Sí | Sí | Criterios y resultado terminal equivalentes | Web manual: 3/3 carga | Pendiente resultado terminal y Tkinter |
| PAR-006 | Ejecutar, pausar, reanudar y detener/reiniciar | Sí | Sí | Snapshot de sesión coherente | Web: manual + 4 E2E terminales; Tkinter: E2E focal | Pendiente recorrido manual Tkinter |
| PAR-007 | Ubicar robot, theta, haces, zoom y paneo | Sí | Sí | Pose y canvas equivalentes | Web parcial | Pendiente |
| PAR-008 | Perfiles Ideal, Realista y Calibrado | Sí | Sí | Perfil de sesión aplicado | Contrato parcial | Pendiente |
| PAR-009 | Límites 30/60/120/300/sin límite | Sí | Sí | Límite y mensaje terminal equivalentes | Runtime parcial | Pendiente |
| PAR-010 | Trazas: iniciar, detener, tick, JSON y CSV | Sí | Sí | Traza y exportación válidas | Web manual: tick post-ejecución | Pendiente exportación y Tkinter |
| PAR-011 | Depuración: breakpoint, paso, continuar y watches | Sí | Sí | Pausa y contexto equivalentes | Web E2E + Tkinter E2E focalizada | Pendiente manual y watches |
| PAR-012 | Tema claro/oscuro y persistencia | Sí | Sí | Paleta legible y preferencia persistida | Web E2E + Tkinter visual 3 tamaños | Pendiente persistencia manual |
| PAR-013 | Centro de ayuda y acerca de | Sí | Sí | Contenido y apertura correctos | Web E2E / escritorio parcial | Pendiente |
| PAR-014 | Telemetría, EV3 Brick y pantalla LCD | Sí | Sí | Datos del mismo snapshot | Web E2E parcial | Pendiente |
| PAR-015 | Éxito, error, tiempo agotado y cancelación | Sí | Sí | Mensaje correcto, único y no bloqueante | Web: E2E éxito/error/cancelación; Tkinter: E2E focal | Pendiente tiempo agotado y revisión manual final |
| PAR-016 | Recarga Web y recuperación de worker | Sí | N/A | Generación actual preservada/restaurada | Contrato + Web parcial | Pendiente |
| PAR-017 | Accesibilidad por teclado y foco | Sí | Sí | Orden de foco y Escape/Enter operables | Web E2E 20/20 + Tkinter E2E parcial | Pendiente manual Tkinter |
| PAR-018 | Diseño responsivo móvil | Sí | N/A | Controles y canvas sin recorte | Web E2E 20/20, 4 resoluciones | Pendiente revisión manual final |

## Controles exclusivos con adaptación aceptada

| ID | Capacidad | Decisión |
|---|---|---|
| ADP-001 | Carga mediante selector de archivos Web vs diálogo nativo Tkinter | Equivalentes funcionales; deben validar extensión, cancelar y error. |
| ADP-002 | Persistencia de tema mediante navegador vs configuración local | Equivalentes si la preferencia reaparece en el siguiente inicio de cada plataforma. |
| ADP-003 | Toast Web vs diálogo nativo de finalización Tkinter | Equivalentes semánticos; ambos deben ser únicos, posteriores al snapshot y ausentes ante error/cancelación. |
| ADP-004 | Móvil | No aplicable a Tkinter; queda como requisito exclusivo de Web. |

## Inventario de recursos a recorrer

| Recurso | Cantidad detectada | Criterio de cierre |
|---|---:|---|
| Ejemplos Python | 23 | Carga real en ambas UI y ejecución de muestra representativa por familia API. |
| Mundos JSON preestablecidos | 12 | Carga real, validación de pose/entidades y reinicio de cada mundo. |
| Escenarios incorporados | 4 | Carga y limpieza de estado anterior en ambas UI. |
| Menús principales | 10 | Apertura, teclado, cierre, comando y bloqueo durante ejecución. |

## Criterio para completar la matriz

La matriz estará cerrada solamente cuando cada fila aplicable tenga evidencia
manual de ambos entornos, pruebas automatizadas donde sean estables y ninguna
brecha funcional de severidad crítica o alta. El informe de liberación debe
enlazar esta matriz al commit probado.
