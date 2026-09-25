# Casos prioritarios — QA total Web

| ID | Objetivo | Datos/acción | Resultado esperado | Estado actual |
|---|---|---|---|---|
| WEB-RUN-001 | Finalización correcta | Script Pybricks corto | Snapshot final coherente y un toast | PASS (WEB-RET-002) |
| WEB-RUN-002 | Reinicio tras éxito | Detener y reiniciar | Pose, LCD, tick y motores iniciales | PASS (WEB-RET-003) |
| WEB-RUN-003 | Cancelar código no cooperativo | `while True: pass` y reinicio | Cancelación inmediata, sin 500 | FAIL (WEB-RET-005) |
| WEB-RUN-004 | Pausar/reanudar | `wait(20000)`, Pausar, Reanudar | Estado y telemetría iguales, sin error residual | FAIL (WEB-RET-007 a 009) |
| WEB-DBG-001 | Breakpoint | Línea 5 y Depurar | Pausa y Continuar habilitado | FAIL (WEB-RET-006) |
| WEB-A11Y-001 | Móvil | 390×844, carga estable | Controles críticos dentro del viewport | PASS parcial (WEB-RET-010) |
| WEB-HELP-001 | Ayuda contextual | Abrir enlace `target=_blank` | Nueva pestaña con ancla de ayuda | BLOCKED |
| WEB-SEC-001 | Sesiones y payload | Tokens cruzados, límite, payload inválido | 401/403/400/429 correctos | PASS automatizado |
| WEB-SESSION-001 | Aislamiento | Dos contextos de navegador | Código y sesión independientes | PASS E2E aislado |
