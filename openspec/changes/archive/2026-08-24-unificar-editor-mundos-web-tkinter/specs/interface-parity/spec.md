## ADDED Requirements

### Requirement: Matriz obligatoria de paridad del Editor de Mundos

La matriz de paridad MUST enumerar y verificar en Web y Tkinter cada comando,
diálogo, validación, atajo, activo y transición al simulador del Editor de
Mundos. Una discrepancia sólo podrá clasificarse como N/A si documenta una
alternativa equivalente y el motivo de plataforma.

#### Scenario: Comando presente sólo en escritorio

- DADO un comando del Editor de Mundos visible en Tkinter;
- CUANDO se actualiza la matriz de paridad;
- ENTONCES debe existir en Web, implementarse como alternativa equivalente o
  quedar bloqueado como brecha;
- Y no puede declararse cerrada la paridad mientras la brecha no se resuelva.
