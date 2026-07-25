## MODIFIED Requirements

### Requisito: Paridad moderna de interfaces

Web y Tkinter DEBERÁN consumir el mismo contrato de sesión y ofrecer controles
equivalentes de ejecución, depuración, perfiles, trazas, accesibilidad y teclado.

#### Escenario: Misma operación en ambas interfaces

- DADO un caso de uso del catálogo compartido
- CUANDO se ejecuta en Web y Tkinter
- ENTONCES ambos clientes DEBERÁN producir estados y snapshots equivalentes.
