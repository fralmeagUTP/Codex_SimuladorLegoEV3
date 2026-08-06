# Matriz de paridad y cierre de liberación

**Cambio OpenSpec:** `cerrar-paridad-y-liberacion-ambas-apps`  
**Estado:** cerrada el 2026-08-05; evidencia real y automatizada aprobada.
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
| PAR-001 | Nuevo, abrir y guardar script | Sí | Sí | Editor y archivo resultante equivalentes | Pruebas UI y recorridos reales | PASS |
| PAR-002 | Cargar 23 ejemplos | Sí | Sí | Código cargado corresponde al recurso | Web 23/23; Tkinter 23/23 | PASS |
| PAR-003 | Mundo vacío, archivo JSON, preestablecido y editor | Sí | Sí | Mundo, pose y entidades coinciden | Web 12/12 + CRUD/E2E; Tkinter 12/12 | PASS |
| PAR-004 | Escenarios línea, ultrasonido, brick y radar | Sí | Sí | Mundo y programa asociado coinciden | Web 4/4; Tkinter 4/4 | PASS |
| PAR-005 | Misiones disponibles | Sí | Sí | Criterios y resultado terminal equivalentes | Web 3/3; Tkinter 3/3 | PASS |
| PAR-006 | Ejecutar, pausar, reanudar y detener/reiniciar | Sí | Sí | Snapshot de sesión coherente | Web E2E + Tkinter E2E nativo | PASS |
| PAR-007 | Ubicar robot, theta, haces, zoom y paneo | Sí | Sí | Pose y canvas equivalentes | Pruebas UI y recorridos reales | PASS |
| PAR-008 | Perfiles Ideal, Realista y Calibrado | Sí | Sí | Perfil de sesión aplicado | Contrato y UI | PASS |
| PAR-009 | Límites 30/60/120/300/sin límite | Sí | Sí | Límite y mensaje terminal equivalentes | Runtime y UI | PASS |
| PAR-010 | Trazas: iniciar, detener, tick, JSON y CSV | Sí | Sí | Traza y exportación válidas | Pruebas de aplicación e interfaz | PASS |
| PAR-011 | Depuración: breakpoint, paso, continuar y watches | Sí | Sí | Pausa y contexto equivalentes | Web E2E + Tkinter E2E | PASS |
| PAR-012 | Tema claro/oscuro y persistencia | Sí | Sí | Paleta legible y preferencia persistida | Web E2E + Tkinter visual en 3 tamaños | PASS |
| PAR-013 | Centro de ayuda y acerca de | Sí | Sí | Contenido y apertura correctos | Web y escritorio real | PASS |
| PAR-014 | Telemetría, EV3 Brick y pantalla LCD | Sí | Sí | Datos del mismo snapshot | Contrato, E2E y revisión visual | PASS |
| PAR-015 | Éxito, error, tiempo agotado y cancelación | Sí | Sí | Mensaje correcto, único y no bloqueante | Web E2E + Tkinter E2E | PASS |
| PAR-016 | Recarga Web y recuperación de worker | Sí | N/A | Generación actual preservada/restaurada | Contrato + Web E2E | PASS |
| PAR-017 | Accesibilidad por teclado y foco | Sí | Sí | Orden de foco y Escape/Enter operables | Web E2E + Tkinter E2E | PASS |
| PAR-018 | Diseño responsivo móvil | Sí | N/A | Controles y canvas sin recorte | Web E2E, 4 resoluciones | PASS |

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

La matriz quedó cerrada con evidencia real en ambos entornos, automatización
estable donde la plataforma lo permite y ninguna brecha crítica o alta abierta.
El informe final conserva los comandos, resultados y observaciones de la
campaña.
