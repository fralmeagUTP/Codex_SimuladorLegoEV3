# Informe de pruebas manuales Web — 2026-08-03

## Entorno

- URL: `http://127.0.0.1:5050/`.
- Navegador: navegador gráfico integrado de Codex, visible durante la campaña.
- Servidor: Waitress local, reiniciado con `scripts/restart_web.ps1` para servir
  la plantilla y los recursos estáticos de la misma versión.
- Vistas ejercitadas: escritorio predeterminado y móvil `390 x 844`.

## Casos ejecutados realmente

| ID | Flujo | Resultado | Evidencia observada |
|---|---|---|---|
| MAN-WEB-001 | Carga e inicio de sesión | PASS | Estado `ready`; Ejecutar habilitado. |
| MAN-WEB-002 | Ejecutar programa Pybricks inicial | PASS | Estado y telemetría `finished`, tiempo `0.54 s`, tick `27`, botón Ejecutar habilitado. |
| MAN-WEB-003 | Detener y reiniciar tras finalizar | PASS | Estado y telemetría `created`, tiempo `0.02 s`, tick `1`. |
| MAN-WEB-004 | Tema oscuro a claro | PASS | Menú Tema abrió y el atributo visual cambió a `light`. |
| MAN-WEB-005 | Vista móvil y haces de sensores | PASS | A `390 x 844`, Haces ON permaneció visible y cambió a `Haces OFF`. |
| MAN-WEB-006 | Pausar programa no terminante | FAIL | Barra global `paused`; telemetría permaneció `running` incluso tras un segundo. |
| MAN-WEB-007 | Reanudar programa pausado | PASS | Barra y telemetría `running`; Pausar quedó habilitado. |
| MAN-WEB-008 | Cancelar y reiniciar programa no terminante | PASS | Estado y telemetría `created`, tiempo `0.02 s`, tick `1`. |

## Hallazgo confirmado

### WEB-M-001 — Pausa desincronizada en telemetría

- Severidad: media.
- Pasos de reproducción:
  1. Introducir `while True: wait(100)` en el editor.
  2. Ejecutar el programa.
  3. Pulsar **Pausar**.
  4. Esperar al menos un segundo.
- Esperado: barra global y telemetría deben indicar `paused` desde el mismo
  snapshot visible.
- Observado: la barra mostró `paused`, mientras Telemetría continuó en
  `running`; tick y tiempo se congelaron en el último snapshot.
- Impacto: el usuario recibe dos estados contradictorios durante una acción de
  control crítica.
- Recomendación: publicar y aplicar un snapshot decorado con `status=paused`
  antes del evento de estado, verificando también la ruta con worker aislado.

## Incidencia de entorno corregida durante la campaña

Antes de reiniciar Waitress, el navegador mostró
`Cannot read properties of undefined (reading 'create')` en
`simulation_app.js:126`. La instancia en ejecución entregaba una plantilla
anterior sin `render_interpolation_controller.js` junto con JavaScript nuevo.
Tras `scripts/restart_web.ps1`, la sesión inició correctamente y no se volvió a
producir el error. Se registra como riesgo operacional de actualización, no como
fallo reproducido en una instancia iniciada desde cero.

## Limitaciones

No se ejecutaron manualmente en esta sesión el CRUD completo de mundos, cada
misión/escenario, todos los menús, errores sintácticos y de ejecución, ni las
cuatro resoluciones del plan integral. Esos casos permanecen pendientes de una
campaña manual ampliada.

## Ampliación de campaña — 2026-08-04

La evidencia vigente y detallada está en
`EVIDENCIA_QA_TOTAL_WEB_2026-08-03/RESULTADOS_MANUALES_PARCIALES.md`. La
ampliación se ejecutó en una instancia oficial iniciada con `.venv` en
`http://127.0.0.1:5052/`, para evitar la divergencia detectada con el proceso
Miniforge que atendía el puerto 5050.

Resultados que sustituyen o amplían las conclusiones iniciales:

- Una ejecución válida y un reinicio posterior **sí** sincronizan estado,
  telemetría, Brick, LCD y pose cuando no hay fallo de worker.
- Se reprodujo en la instancia oficial que un bucle no cooperativo
  `while True: pass` no se cancela con el primer reinicio: queda bloqueado y
  muestra HTTP 500.
- Se reprodujo que pausar una ejecución activa puede dejar la barra en
  `paused` mientras la telemetría permanece en `running`; el backend informa
  `TimeoutError: El worker sombra no confirmó pause`.
- Se reprodujo que el reinicio posterior conserva el error HTTP 500 aun cuando
  la sesión ya volvió a `created`.
- El breakpoint de línea 5 no pausa una depuración; la ejecución termina en
  `finished`.
- Los enlaces contextuales de Ayuda abren con `target="_blank"`. La campaña no
  pudo controlar la pestaña nueva, por lo que se clasifican como `BLOCKED`, no
  como fallo confirmado.

Por estas incidencias, este informe histórico no constituye un dictamen de
liberación. El dictamen deberá basarse en la matriz ampliada y en la repetición
de los flujos aún pendientes.
