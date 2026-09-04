# Diseño técnico

## Flujo objetivo

    SimulationEngine (50 Hz, autoritativo)
            │ snapshots
            ▼
    SimulationSession (coalescing configurable, 50 Hz por defecto)
            │ SSE / polling
            ▼
    Snapshot buffer Web (dos poses consecutivas + timestamps)
            │ requestAnimationFrame (hasta la frecuencia del monitor)
            ▼
    Canvas interpolado; telemetría y LCD por snapshot autoritativo

## Decisiones

- Mantener 50 Hz y dt=0.02 s en el motor; la fidelidad física no depende de
  la velocidad de pintura del navegador.
- Elevar WEB_SNAPSHOT_MAX_HZ por defecto a 50 Hz y exponer
  EV3_WEB_WEB_SNAPSHOT_MAX_HZ. Validar rango seguro de 10 a 60 Hz.
- El controlador visual guardará snapshot anterior y actual. Interpolará
  x_mm, y_mm y theta por el menor ángulo equivalente; no interpolará ticks,
  motores, sensores, LCD, estado ni colisión.
- La telemetría, LCD, consola y barra de estado se actualizarán solo a partir
  del snapshot autoritativo más reciente. El canvas podrá usar una pose
  temporal de renderizado sin modificar el estado de sesión.
- Si no hay dos snapshots compatibles, si la generación cambia, existe
  colisión, la ejecución está terminal o el retraso supera el umbral, se
  dibujará la pose autoritativa sin interpolar.
- El evento terminal forzará la publicación y aplicación del último snapshot
  del worker antes de cambiar la interfaz al estado terminal.
- El fallback de polling seguirá funcionando; la interpolación no ocultará
  retrasos de red ni inventará movimiento posterior al último snapshot.

## Medición

Se registrarán en modo diagnóstico: Hz de snapshots recibidos, frames
renderizados, snapshots descartados, retraso de snapshot y porcentaje de
frames interpolados. Las métricas no incluirán código ni datos personales.
