# Auditoría de ayuda didáctica y visuales

## Hallazgos confirmados

| Guía | Audiencia | Destino | Recurso anterior | Discrepancia |
|---|---|---|---|---|
| Mi primera simulación | Estudiante/docente | Simulación | SVG genérico de simulación | No identifica la composición actual de canvas, editor, Brick y telemetría. |
| Crear un mundo | Estudiante/docente | Mundos | SVG genérico de mundo | No muestra biblioteca, inspector ni acciones reales actuales. |
| Ejecutar, pausar y reiniciar | Estudiante/docente | Simulación | SVG genérico compartido | No representa estados de los cuatro controles ni el tema oscuro. |
| Usar motores y sensores | Estudiante/docente | Simulación | SVG genérico compartido | No muestra telemetría ni LCD actuales. |
| Depurar un programa | Estudiante/docente | Depuración | SVG genérico de depuración | No refleja Watches, breakpoints, Paso y Continuar. |
| Resolver error de programa | Estudiante/docente | Simulación | SVG genérico de depuración | No contiene un mensaje de error real ni el flujo de recuperación. |
| Resolver validación de mundo | Estudiante/docente | Mundos | SVG genérico de mundo | No muestra inspector ni validación de propiedades. |

## Decisiones de contenido

- Niveles: **inicial** (primera simulación y mundos), **intermedio** (motores,
  sensores, trazas y depuración) y **avanzado** (misiones, diagnóstico y
  recuperación).
- Rutas: estudiante (inicio → programar → depurar), docente (mundo → misión →
  evidencia) y soporte (diagnóstico → trazas → recuperación).
- Progreso: local, explícito, reiniciable y sin código, credenciales ni datos
  de sesión.
- Capturas: datos sintéticos, temática Web/Tkinter real, texto alternativo y
  transcripción obligatorios.

## Política de actualización

Una captura debe regenerarse si cambia el control destacado, la composición de
la pantalla, el tema, el asset representado o la versión de interfaz. El
manifiesto registra plataforma, fecha, origen y versión; una validación de CI
impedirá publicar una guía sin recurso vigente o fallback textual.
