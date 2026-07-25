## ADDED Requirements

### Requirement: Paridad verificable de las interfaces
Las interfaces MUST cumplir este requisito.

Web y Tkinter DEBERAN cubrir y clasificar todos los casos del catalogo de
paridad, incluidos editor de mundos y ayuda. Una capacidad ausente solo sera
aceptable cuando la matriz la declare como limitacion y explique su alternativa.

#### Scenario: Caso de uso de mundo auditado

- DADO un caso de uso de mundo del catalogo compartido
- CUANDO se ejecuta la auditoria de paridad
- ENTONCES Web y Tkinter DEBERAN tener prueba equivalente o limitacion documentada.

### Requirement: Regresion visual controlada
Las interfaces MUST cumplir este requisito.

Las interfaces DEBERAN generar capturas reproducibles en los viewports de
referencia y detectar diferencias fuera de las regiones nativas permitidas.

#### Scenario: Diferencia visual no aprobada

- DADO un cambio que modifica una region visual comparable
- CUANDO la comparacion automatizada supera el umbral configurado
- ENTONCES CI DEBERA fallar y publicar las imagenes de referencia, actual y diferencia.
