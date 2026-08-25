# Guía de diagnóstico para aula y soporte

## Antes de reportar un problema

1. Anote la versión del producto, plataforma (Web o Tkinter), sistema operativo y hora.
2. Anote el estado visible (`ready`, `running`, `paused`, `finished`, `error`, `timed_out` o `stopped`).
3. Conserve `session_id`, `command_id` y `worker_id` del diagnóstico, si existen.
4. No adjunte código de estudiantes, tokens, contraseñas ni datos personales al informe.

## Web

- Abra **Ayuda → Diagnóstico de sesión** para copiar el estado correlacionado y
  los contadores de renderizado.
- Use **Ayuda → Exportar diagnóstico JSON** para descargar la misma evidencia
  en formato UTF-8 versionado, sin código del editor ni credenciales.
- Para operación del servidor use `/healthz` y `/metrics`; el segundo admite
  formato Prometheus con `?format=prometheus`.
- Si el stream se interrumpe, espere la recuperación automática y confirme que
  el `session_id` permanece igual. Si no se recupera, recargue y cree una nueva
  sesión, registrando el diagnóstico anterior.

## Tkinter

- Abra **Ayuda → Diagnóstico de sesión** para consultar la sesión local.
- Use **Ayuda → Exportar diagnóstico JSON** para adjuntar evidencia técnica
  local. El archivo contiene estado, tick, tiempo, error y correlación; no
  contiene el código ni credenciales.
- Si el worker aislado falla, reinicie la simulación antes de volver a ejecutar.

En ambas interfaces, **Acerca de** solo contiene versión, créditos e
información institucional; no se usa para mostrar diagnósticos.

## Interpretación y escalamiento

| Señal | Acción inicial |
|---|---|
| `timed_out` | Revisar bucles, esperas y límite configurado. |
| `error` | Corregir el mensaje del editor y usar depuración paso a paso. |
| `stopped` | Confirmar si el usuario pidió detener y reiniciar. |
| Worker no disponible | Registrar correlación, reiniciar la sesión y comprobar recuperación. |
| Canvas/LCD/telemetría diferentes | Registrar snapshot, mundo y comando; no declarar finalizada la práctica. |

Los diagnósticos ayudan a investigar la simulación, pero no validan por sí
solos el comportamiento de un robot EV3 físico.
