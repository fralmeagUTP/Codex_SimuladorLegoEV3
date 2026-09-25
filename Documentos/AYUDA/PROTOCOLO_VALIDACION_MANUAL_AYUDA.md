# Protocolo de validación manual del Centro de ayuda

Este protocolo completa la evidencia humana pendiente de la tarea 5.4 del
cambio OpenSpec `modernizar-ayuda-interactiva-y-capturas-reales`. No sustituye
las pruebas automatizadas ya ejecutadas.

## Participantes y condiciones

- Una persona estudiante inicial y una persona docente.
- Un equipo con la aplicación Web y otro con la aplicación de escritorio.
- Usar datos locales y sintéticos; no registrar nombres, correos, código
  personal ni identificadores de sesión.
- Duración orientativa: 25 minutos por participante.

## Casos a ejecutar

| ID | Perfil | Acción | Éxito observable | Tiempo | Resultado |
| --- | --- | --- | --- | --- | --- |
| H-MAN-01 | Estudiante | Encontrar y abrir «Mi primera simulación». | Comprende el objetivo y llega a Simulación. | ___ min | PASS / FAIL |
| H-MAN-02 | Estudiante | Marcar dos pasos, recargar y comprobar el avance. | El progreso permanece solo en el navegador local. | ___ min | PASS / FAIL |
| H-MAN-03 | Estudiante | Copiar el ejemplo seguro y ejecutarlo. | El ejemplo se copia sin reemplazar código no solicitado. | ___ min | PASS / FAIL |
| H-MAN-04 | Estudiante | Usar búsqueda y recuperar un error. | Encuentra una guía y aplica una acción de recuperación. | ___ min | PASS / FAIL |
| H-MAN-05 | Docente | Activar Modo docente y seguir la ruta propuesta. | Identifica objetivo, duración, evidencia y advertencia. | ___ min | PASS / FAIL |
| H-MAN-06 | Ambos | Cambiar claro/oscuro y navegar solo con teclado. | Texto legible, foco visible y controles operables. | ___ min | PASS / FAIL |
| H-MAN-07 | Ambos | Abrir ayuda en Web y Tkinter. | Contenido, rutas y acciones equivalentes. | ___ min | PASS / FAIL |

## Preguntas de salida

Cada participante responde del 1 (muy en desacuerdo) al 5 (muy de acuerdo):

1. Encontré la guía que necesitaba sin ayuda externa: ___/5.
2. Los pasos y la captura explican claramente qué debo hacer: ___/5.
3. Entendí qué resultado debía observar y cómo recuperarme de un error: ___/5.
4. El tema y la navegación por teclado fueron cómodos: ___/5.

Registrar también: principal bloqueo, terminología confusa, guía faltante y
mejora sugerida. Si una persona no logra terminar un caso, registrar el paso,
la plataforma y la evidencia visual, sin inferir la causa.

## Criterio de cierre

La tarea 5.4 puede marcarse completada solo cuando haya resultados de al menos
una persona estudiante y una docente, con los casos H-MAN-01 a H-MAN-07
registrados, sus tiempos, bloqueos y decisiones de mejora documentadas.
