# Tareas: paridad visual Web–Tkinter

## Fase 1 — Inventario y tokens

- [x] 1.1 Inventariar controles, etiquetas, iconos, estados y orden de la Web.
- [x] 1.2 Publicar tokens visuales y tabla CSS–Tkinter versionada.
- [x] 1.3 Definir tamaños de referencia, DPI y tolerancias visuales.

## Fase 2 — Implementación Tkinter

- [x] 2.1 Rehacer barra de acciones, menús y estados conforme a Web (barra integrada, menú claro/oscuro Web y estados Ejecutar/Pausar/Reanudar/Detener verificados en captura de referencia).
- [x] 2.2 Alinear mundo, editor, depuración, telemetría y brick (misma composición Mundo/Editor, depuración, telemetría Robot/Motores/Sensores y Brick; se documentan las diferencias nativas de scroll).
- [x] 2.3 Alinear tema, foco, teclado, mensajes y controles deshabilitados (temas claro/oscuro, Escape, Ctrl+N/O/S y bloqueo de controles cubiertos por pruebas UI).
- [x] 2.4 Sustituir colores y dimensiones codificados por tokens compartidos (tokens Web aplicados a cabecera, controles, estado, mensajes de colocacion y rejilla del mundo; los colores fisicos de robot, LCD y activos del mundo se conservan como datos de renderizado, no como cromia de interfaz).

## Fase 3 — Pruebas y evidencia

- [x] 3.1 Probar catálogo de controles y estados en ambas interfaces (77 pruebas UI/tokens y 20 recorridos Playwright Web ejecutados; la suite completa pasó).
- [x] 3.2 Generar capturas patrón reproducibles para Web y Tkinter en `Documentos/EVIDENCIA_PARIDAD_2026-07-24`.
- [x] 3.3 Comparar visualmente con tolerancia documentada.
- [x] 3.4 Actualizar manuales y matriz de paridad.

## Criterios de aceptación

- Los controles equivalentes tienen igual etiqueta, orden, semántica y estado.
- Colores y espaciado son equivalentes salvo limitaciones nativas documentadas.
- Tema, foco, teclado, depuración, trazas y perfiles conservan paridad visual.
