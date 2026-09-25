# Propuesta: ejecutar QA total de la aplicación Web

## Problema

Las pruebas existentes cubren rutas críticas y algunas campañas manuales, pero
no acreditan que **todo el catálogo disponible en la instancia Web** haya sido
recorrido mediante navegador real: cada ejemplo, mundo, escenario, misión,
menú, diálogo, control, modo de depuración, sesión y flujo de autoría.

## Objetivo

Ejecutar una campaña de calidad integral, reproducible y trazable de la
aplicación Web de BotLab Studio. La campaña debe descubrir dinámicamente el
catálogo de la instancia, ejercer cada opción visible en un navegador gráfico y
complementarla con pruebas automatizadas, de contrato y no funcionales.

## Alcance

- Navegación manual real por todas las opciones y diálogos Web.
- Ejecución de todos los ejemplos, mundos, escenarios y misiones disponibles.
- Editor Pybricks, depuración, controles, canvas, sensores, trazas, temas,
  fidelidad y límite de tiempo.
- CRUD completo de mundos con datos sintéticos aislados.
- Sesiones concurrentes y aislamiento de múltiples usuarios.
- API, SSE/polling, persistencia, seguridad, accesibilidad, rendimiento,
  resiliencia, compatibilidad y empaquetado/despliegue Web.
- Evidencia fechada: capturas, consola, solicitudes, HAR, resultados y matriz.

## Coherencia temporal

La campaña verificará que el tiempo de pared, `sim_time_s`, los ticks del motor,
la ejecución Pybricks y la animación del canvas evolucionen de forma coherente.
La interpolación solo puede suavizar la pose visual: no puede acelerar, retrasar
ni adelantar la semántica, la telemetría, LCD, estados o fin de un programa.

## Fuera de alcance

- No se usarán usuarios, mundos, datos ni credenciales de producción.
- No se alterarán reglas de negocio para aprobar pruebas.
- No se declarará PASS para una acción no ejercitada en navegador real.

## Resultado esperado

Un informe de liberación con inventario ejecutado, casos PASS/FAIL/BLOCKED,
defectos reproducibles priorizados, cobertura real, limitaciones y decisión
`apta`, `apta con observaciones` o `no apta`.
