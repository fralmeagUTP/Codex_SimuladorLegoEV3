## Requisitos añadidos

### Requisito: pausa cooperativa de scripts

El runtime DEBE conservar el tiempo restante de `pybricks.tools.wait()` cuando
la sesión se pausa y DEBE permitir cancelarla inmediatamente.

#### Escenario: reanudar una espera pausada

- **Dado** un script ejecutando `wait(8000)`;
- **cuando** el usuario pausa y luego reanuda;
- **entonces** la espera continúa durante el tiempo pendiente y no finaliza de
  inmediato.

### Requisito: trazas desde worker aislado

La sesión de escritorio DEBE incorporar a la traza los snapshots recibidos del
worker aislado mientras el registro esté activo.

#### Escenario: exportar una ejecución aislada

- **Dado** el registro activo y un script ejecutado en worker;
- **cuando** se exporta JSON después de recibir ticks;
- **entonces** el arreglo `snapshots` contiene al menos un elemento.
