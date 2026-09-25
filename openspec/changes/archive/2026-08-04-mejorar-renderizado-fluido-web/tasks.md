# Tareas: mejorar renderizado fluido Web

## Fase 1 — Contrato y configuración

- [x] 1.1 Documentar las tres cadencias: motor, snapshots y frames.
- [x] 1.2 Añadir configuración validada para EV3_WEB_WEB_SNAPSHOT_MAX_HZ,
  con valor predeterminado de 30 Hz y límites de 10–60 Hz.
- [x] 1.3 Mantener publicación forzada del snapshot final antes de cada evento
  terminal y cubrir el orden con pruebas de contrato.

## Fase 2 — Renderizado

- [x] 2.1 Extraer un controlador de interpolación visual independiente del
  controlador de snapshots autoritativos.
- [x] 2.2 Interpolar posición y orientación en requestAnimationFrame sin
  alterar telemetría, LCD, sensores, ticks ni estado.
- [x] 2.3 Desactivar interpolación de forma segura en cambios de generación,
  teletransporte, colisión, pausa, estados terminales o snapshots obsoletos.
- [x] 2.4 Renderizar haces y trayectoria con la pose interpolada y limpiar
  correctamente al reiniciar o cambiar de mundo.

## Fase 3 — Rendimiento y compatibilidad

- [x] 3.1 Conservar SSE como canal preferido y el polling como fallback.
- [x] 3.2 Evitar reconstruir capas estáticas del mundo por cada frame.
- [x] 3.3 Añadir diagnóstico opcional de FPS, cadencia y retraso sin exponerlo
  por defecto al estudiante.
- [x] 3.4 Verificar navegador de escritorio y móvil sin desbordamiento ni
  consumo excesivo de CPU.

## Fase 4 — Verificación

- [x] 4.1 Pruebas unitarias de interpolación lineal, ángulos circulares,
  límites y reinicios.
- [x] 4.2 Pruebas de integración de publicación a 30 Hz y snapshot terminal.
- [x] 4.3 E2E Web: movimiento visible continuo, pausa, reanudar, detener,
  cambio de mundo y radar ultrasónico.
- [x] 4.4 Registrar evidencia de rendimiento y actualizar documentación de
  operación y diferencias Web/Tkinter.
