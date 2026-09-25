# desktop-runtime Specification

## Purpose
TBD - created by archiving change corregir-regresiones-funcionales-qa. Update Purpose after archive.
## Requirements
### Requirement: pausa cooperativa de scripts

El runtime MUST conservar el tiempo restante de `pybricks.tools.wait()` cuando
la sesión se pausa y MUST permitir cancelarla inmediatamente.

#### Scenario: reanudar una espera pausada

- **Dado** un script ejecutando `wait(8000)`;
- **cuando** el usuario pausa y luego reanuda;
- **entonces** la espera continúa durante el tiempo pendiente y no finaliza de
  inmediato.

### Requirement: trazas desde worker aislado

La sesión de escritorio MUST incorporar a la traza los snapshots recibidos del
worker aislado mientras el registro esté activo.

#### Scenario: exportar una ejecución aislada

- **Dado** el registro activo y un script ejecutado en worker;
- **cuando** se exporta JSON después de recibir ticks;
- **entonces** el arreglo `snapshots` contiene al menos un elemento.

### Requirement: Verificación real de flujos críticos de escritorio

La aplicación Tkinter MUST disponer de una campaña reproducible de interfaz
gráfica que ejerza sus comandos críticos y documente los casos que requieran
validación manual.

#### Scenario: Menú y ejecución de escritorio

- **DADO** la ventana Tkinter visible y una simulación activa;
- **CUANDO** se prueben ejecutar, pausar, reanudar, detener y reiniciar;
- **ENTONCES** los menús y controles reflejarán el estado permitido;
- **Y** al llegar a un estado terminal recuperarán su disponibilidad esperada.
