# Reporte de campaña local de sesiones concurrentes

Fecha: 2026-08-24  
Entorno: Windows local, Python 3.12, servidor HTTP temporal `werkzeug` con
`create_app()` del repositorio. No se usó `nyquist.app`, credenciales, datos de
usuarios ni el servidor abierto en el puerto 5051.

## Perfil ejecutado

- Usuarios simulados: 24.
- Concurrencia: 8 clientes HTTP en paralelo.
- Capacidad configurada: 24 sesiones y 24 simulaciones.
- Operaciones por usuario: crear sesión, cargar script sintético marcado y
  consultar el resumen autorizado.

## Resultado

| Verificación | Resultado |
| --- | --- |
| Sesiones creadas | 24 / 24 |
| IDs y tokens únicos | 24 / 24 |
| Scripts cargados y asociados | PASS |
| Lectura cruzada con token ajeno | `403 Forbidden` esperado |
| Sesión adicional sobre capacidad | `429 Capacity Exceeded` esperado |
| Respuestas 5xx | 0 |
| Sesiones y workers tras cierre | 0 / 0 |
| Duración total de campaña | 13.58 s |
| Mayor latencia por usuario observada | 4781.36 ms |

La evidencia estructurada completa, sin tokens ni IDs de sesión publicados, se
encuentra en `campana_sesiones_local.json`.

## Ampliación de carga: 48 usuarios concurrentes

Se repitió la misma campaña aislada el 2026-08-24 con el doble de usuarios y
sin utilizar el servidor que opera en el puerto 5051.

- Usuarios simulados: 48.
- Concurrencia HTTP: 16 clientes en paralelo.
- Capacidad configurada temporalmente: 48 sesiones y 48 simulaciones.
- Duración total: 27.54 s.
- Mayor latencia individual observada: 7904.99 ms.

| Verificación | Resultado |
| --- | --- |
| Sesiones creadas | 48 / 48 |
| IDs y tokens únicos | 48 / 48 |
| Scripts sintéticos asociados a su sesión | PASS |
| Lectura cruzada con token ajeno | `403 Forbidden` esperado |
| Sesión adicional sobre capacidad | `429 Capacity Exceeded` esperado |
| Respuestas 5xx | 0 |
| Sesiones y workers tras cierre | 0 / 0 |

La evidencia JSON vigente corresponde a esta ampliación de 48 usuarios y no
incluye secretos, tokens ni identificadores de sesión.

## Interpretación para Nyquist

La campaña prueba corrección funcional y aislamiento en la implementación local;
no representa un SLA ni la capacidad del hardware de Nyquist. Antes de liberar,
se debe repetir con la configuración final de procesos, memoria y límites del
servidor, empezando con `MAX_ACTIVE_SESSIONS=20` y
`MAX_RUNNING_SIMULATIONS=8`, y ajustando solo después de observar CPU, memoria,
latencia y cola de workers.
