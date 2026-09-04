# Protocolo de validación: menú unificado Web y escritorio

## Propósito

Comprobar que BotLab Studio Web y la aplicación de escritorio presentan la misma estructura de navegación, terminología y resultado funcional.

Para valorar si los nombres se comprenden sin guía, completar también
`FORMULARIO_COMPRENSION_MENU_UNIFICADO.md` con una persona estudiante o docente.

## Preparación

1. Abrir una sesión nueva de la aplicación Web y una instancia nueva de escritorio.
2. Cargar un mundo conocido y conservar un script con cambios no guardados.
3. Verificar que la barra muestra, en orden, Archivo, Aprender, Mundos, Prácticas guiadas, Misiones, Configuración, Diagnóstico y Ayuda.

## Casos de prueba

| ID | Acción | Resultado esperado en ambos productos |
|---|---|---|
| MNU-01 | Recorrer la barra con Tab, Enter, Espacio y Escape. | Cada categoría recibe foco visible, abre y cierra sin perder el foco. |
| MNU-02 | Abrir Aprender. | Los ejemplos están agrupados en Empezar, Movimiento, Sensores, Control y navegación, y Retos avanzados. |
| MNU-03 | Cargar un ejemplo. | Cambia el editor, el nombre del programa y el estado; si la sesión vence, se recupera o informa el fallo sin declarar éxito. |
| MNU-04 | Abrir Mundos y cargar un preestablecido. | Cambia el mapa, la pose inicial y el título del mundo. |
| MNU-05 | Revisar Prácticas guiadas y seleccionar una. | Antes de cargar se identifica objetivo, mundo y programa; al finalizar, ambos recursos coinciden con la práctica elegida. |
| MNU-06 | Abrir una misión. | Se identifican propósito, duración, requisitos y progreso inicial; se carga el mundo y programa inicial correctos. |
| MNU-07 | Cambiar tema, perfil y límite en Configuración. | Se indica el valor activo y se aplica sin alterar el script ni el mundo. |
| MNU-08 | Usar Diagnóstico. | Las trazas, diagnóstico de sesión y exportación están separados del material didáctico. |
| MNU-09 | Abrir Ayuda. | Centro de ayuda, guía rápida, libro y Acerca de abren el destino anunciado. |
| MNU-10 | Iniciar una simulación y abrir menús mutables. | Las acciones que cambiarían el contexto están bloqueadas y se habilitan al detener y reiniciar. |
| MNU-11 | Modificar el script y cargar un ejemplo, mundo, práctica o misión; elegir Cancelar. | Se advierte que hay cambios sin guardar y se conserva el editor y mundo previos. |

## Criterios de aceptación

- No hay categorías antiguas independientes de Tema, Fidelidad, Tiempo máximo o Trazas.
- Ninguna acción muestra éxito si editor, mundo o sesión no se actualizaron.
- Los mensajes de recuperación no exponen identificadores internos, procesos, tokens ni rutas privadas.
- Web y escritorio usan las mismas ocho categorías y etiquetas equivalentes.
- Los controles funcionan con teclado y muestran foco visible.
- Se registra una captura por producto para MNU-01, MNU-05, MNU-07 y MNU-10.

## Evidencia

Guardar las capturas, resultados y errores en `artifacts/e2e-web/` para Web y `artifacts/e2e-desktop/` para escritorio. Anotar fecha, versión y sistema operativo usado.
