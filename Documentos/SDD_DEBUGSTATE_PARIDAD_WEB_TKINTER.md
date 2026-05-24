# SDD - DebugState Unificado y Paridad Web/Tkinter

Fecha: 2026-05-24
Estado: Propuesta aplicable (implementacion incremental)
Alcance: Modulo de depuracion de simulacion para Web Flask y App Tkinter

## 1. Objetivo
Definir un contrato unico de estado de depuracion para eliminar divergencias entre frontends (Web y Tkinter), simplificar la logica de UI y habilitar capacidades de depuracion de mayor aplicabilidad (inspeccion de contexto, control de flujo y trazabilidad).

## 2. Problema actual
- La pausa por breakpoint/step se representa parcialmente en UI local, no como estado canonico de sesion.
- El runtime emite eventos de linea, pero no existe un modelo formal de contexto de depuracion para stack/locals/watches.
- Web y Tkinter implementan reglas propias de habilitacion de controles, con riesgo de deriva funcional.

## 3. Metas funcionales
1. Unificar estado de depuracion en backend (source of truth).
2. Exponer el estado en snapshot y stream SSE.
3. Consumir el mismo contrato en Web y Tkinter para botones, menus y mensajes.
4. Permitir evolucion gradual hacia features avanzadas (step over/into/out, watch, condicionales).

## 4. Modelo canonico de estado

### 4.1 Enumeracion de estados
- idle: sesion creada o reseteada, sin ejecucion activa.
- running: script ejecutando sin pausa de depuracion.
- paused_breakpoint: detenido por breakpoint.
- paused_step: detenido por paso a paso.
- paused_manual: detenido por accion de pausa del usuario.
- stopped: ejecucion detenida por usuario o fin controlado.
- error: termino con excepcion.

### 4.2 Estructura DebugState
```json
{
  "debug_state": "paused_breakpoint",
  "line": 42,
  "function": "seguir_linea",
  "reason": "breakpoint",
  "breakpoints": [12, 42, 88],
  "can_continue": true,
  "can_step": true,
  "timestamp": "2026-05-24T20:15:18Z"
}
```

Reglas:
- line y function son opcionales fuera de estados paused_*.
- reason permitido: breakpoint, step, manual, timeout, error.
- can_continue y can_step son derivados del estado canonico para evitar logica duplicada en UI.

## 5. Contrato de API y SSE

### 5.1 Snapshot
Incluir bloque debug en respuesta de snapshot:
```json
{
  "session_id": "...",
  "status": "running",
  "snapshot": {"robot": {"x_mm": 1000, "y_mm": 1000}},
  "debug": {
    "debug_state": "paused_step",
    "line": 57,
    "function": "main",
    "reason": "step",
    "breakpoints": [57],
    "can_continue": true,
    "can_step": true,
    "timestamp": "2026-05-24T20:15:18Z"
  }
}
```

### 5.2 SSE
Eventos recomendados:
- status: cambios de estado global de sesion.
- snapshot: estado fisico de simulacion.
- debug_state: cambios canonicos de depuracion.
- debug_context: contexto detallado (stack/locals/watches) cuando aplique.

Ejemplo debug_state:
```json
{
  "debug_state": "paused_breakpoint",
  "line": 91,
  "function": "resolver_laberinto",
  "reason": "breakpoint",
  "can_continue": true,
  "can_step": true,
  "timestamp": "2026-05-24T20:15:20Z"
}
```

Ejemplo debug_context:
```json
{
  "line": 91,
  "stack": [
    {"function": "resolver_laberinto", "line": 91},
    {"function": "main", "line": 120}
  ],
  "locals": {
    "distancia": 245,
    "velocidad": 120
  },
  "watches": [
    {"expr": "distancia < 300", "value": true, "error": null}
  ]
}
```

## 6. Comandos de depuracion (minimo)
Mantener los actuales y agregar semantica uniforme:
- POST /api/sessions/{id}/debug/step
- POST /api/sessions/{id}/debug/continue
- POST /api/sessions/{id}/debug/breakpoints

Agregar en fase 3:
- POST /api/sessions/{id}/debug/step-over
- POST /api/sessions/{id}/debug/step-into
- POST /api/sessions/{id}/debug/step-out
- POST /api/sessions/{id}/debug/run-to-cursor

## 7. Cambios minimos por capa

### 7.1 Runtime
- Introducir estructura interna DebugStateSnapshot.
- Emitir eventos canonicos al entrar/salir de pausa.
- Mantener compatibilidad temporal con eventos legacy de linea.

### 7.2 Application Service
- Consolidar traduccion runtime -> DTO debug.
- Exponer metodo get_debug_state() para snapshot y stream.
- Convertir reglas de control a capacidades (can_step, can_continue).

### 7.3 Web Session / Routes
- Incluir debug en summary/snapshot.
- Publicar SSE debug_state y debug_context.
- Validar payloads de breakpoints y futuros comandos avanzados.

### 7.4 Web UI
- Eliminar dependencias de banderas locales como fuente primaria.
- Consumir debug.debug_state para habilitar/deshabilitar botones y menus.
- Mostrar razon de pausa y linea en panel de estado.

### 7.5 Tkinter UI
- Consumir el mismo DTO debug.
- Mantener resaltado de linea y mensajes, pero guiados por estado canonico.
- Compartir matriz de reglas de habilitacion con Web (documentada y testeable).

## 8. Compatibilidad y migracion

### 8.1 Estrategia
- Fase 1: agregar campos nuevos sin remover legacy.
- Fase 2: migrar clientes (Web/Tkinter) al contrato nuevo.
- Fase 3: deprecar eventos/flags legacy tras dos releases estables.

### 8.2 Flags recomendados
- DEBUGSTATE_V2_ENABLED=true (backend)
- WEB_DEBUGSTATE_V2=true (frontend web)
- TK_DEBUGSTATE_V2=true (frontend desktop)

## 9. Plan de pruebas

### 9.1 Unitarias
- Runtime: transiciones running -> paused_* -> running.
- Application: DTO debug consistente para cada transicion.
- Web session: serializacion de debug_state y capacidades.

### 9.2 Integracion
- API: snapshot incluye bloque debug valido.
- SSE: orden y contenido de eventos status/debug_state/snapshot.
- Breakpoints invalidos retornan error de validacion.

### 9.3 UI contract tests
- Web: botones y lock de menu segun debug_state.
- Tkinter: comandos bloqueados/habilitados segun debug_state.
- Paridad: misma matriz de estados produce misma disponibilidad funcional.

### 9.4 E2E
- Caso 1: start debug -> breakpoint -> continue -> finish.
- Caso 2: step repetido en linea segura.
- Caso 3: error de script y exposicion de contexto minimo.

## 10. Roadmap sugerido
1. Sprint A (quick win): DebugState canonico + snapshot/SSE + migracion minima de controles.
2. Sprint B (observabilidad): debug_context con stack y locals serializables.
3. Sprint C (avanzado): step over/into/out, run-to-cursor, watches y breakpoints condicionales.

## 11. Riesgos y mitigaciones
- Riesgo: ruptura de UI por cambios de contrato.
  Mitigacion: compatibilidad dual y feature flags.
- Riesgo: sobrecosto por trazas frecuentes.
  Mitigacion: throttling y envio incremental de contexto.
- Riesgo: exposicion de datos sensibles en locals.
  Mitigacion: serializacion segura con allowlist y truncamiento.

## 12. Criterios de aceptacion
1. Web y Tkinter usan el mismo debug_state como fuente principal de control.
2. El usuario ve razon de pausa y linea actual de forma consistente en ambas apps.
3. La matriz de habilitacion de controles coincide entre ambas apps en todos los estados.
4. No hay regresion en flujo run/pause/reset ni en lock de menu durante ejecucion.
