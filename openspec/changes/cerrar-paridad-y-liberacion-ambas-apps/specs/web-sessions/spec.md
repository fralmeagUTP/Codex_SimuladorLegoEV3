## ADDED Requirements

### Requirement: Recuperación verificable de la sesión Web

La sesión Web MUST conservar o restaurar un estado documentado ante recarga,
interrupción recuperable del worker y transición terminal, sin aplicar eventos
de una generación anterior a la interfaz actual.

#### Scenario: Evento retrasado después de reiniciar

- **DADO** una ejecución cancelada y una nueva generación de sesión iniciada;
- **CUANDO** llegue un evento terminal retrasado de la generación anterior;
- **ENTONCES** la interfaz lo ignorará;
- **Y** no cambiará el estado ni mostrará una notificación de éxito incorrecta.
