## ADDED Requirements

### Requirement: Verificación completa de autoría de mundos Web

La campaña Web MUST ejercitar creación, validación, guardado, carga, edición,
cancelación y eliminación segura de mundos con datos sintéticos aislados.

#### Scenario: Mundo guardado y reabierto

- DADO un mundo QA con posición inicial, obstáculos y sensores
- CUANDO se guarda, se recarga el navegador y se vuelve a cargar
- ENTONCES sus elementos y configuración DEBERÁN persistir
- Y el simulador DEBERÁ iniciar el robot en la pose definida sin restos de un
  mundo anterior.
