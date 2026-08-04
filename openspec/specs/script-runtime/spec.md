# Especificación: runtime de scripts

## Purpose

Ejecutar programas Python del estudiante contra la API virtual y coordinar ciclo de vida, depuración, comandos bloqueantes, errores y timeout.
## Requirements
### Requirement: Namespace de programa restringido
El runtime MUST cumplir este requisito.

El runtime DEBERÁ ejecutar el programa cargado en un namespace construido con la política de ejecución. DEBERÁ exponer sólo builtins seguros configurados, módulos estándar permitidos y módulos Pybricks virtuales. Las importaciones directas fuera del conjunto permitido DEBERÁN fallar con `ImportError`.

#### Scenario: Importación bloqueada del sistema operativo

- DADA una política de ejecución predeterminada
- CUANDO un programa importa `os`, `subprocess` o `socket`
- ENTONCES la ejecución DEBERÁ fallar con error de importación
- Y la sesión DEBERÁ informar el error sin detener otras sesiones.

### Requirement: Ciclo de vida del programa
El runtime MUST cumplir este requisito.

El runtime DEBERÁ informar estados inactivo, ejecutando, finalizado, detenido, agotado por tiempo o con error, según corresponda. El retorno natural del código DEBERÁ producir estado finalizado; una parada explícita DEBERÁ señalizar el evento de detención y liberar operaciones en espera cuando sea posible.

#### Scenario: Finalización natural

- DADO un programa válido y finito
- CUANDO alcanza el final de su código fuente
- ENTONCES el runtime DEBERÁ marcar la ejecución como finalizada
- Y DEBERÁ notificar a la aplicación o sesión propietaria.

### Requirement: Errores de runtime
El runtime MUST cumplir este requisito.

El runtime DEBERÁ capturar excepciones de sintaxis y ejecución, preservar mensaje y traceback, y emitir un evento de error para la sesión propietaria.

#### Scenario: Sentencia inválida

- DADO código con error de sintaxis Python
- CUANDO el runtime lo inicia
- ENTONCES la sesión DEBERÁ informar estado de error y traceback
- Y el proceso web DEBERÁ seguir disponible para las demás sesiones.

### Requirement: Política de watchdog
El runtime MUST cumplir este requisito.

Cuando `max_runtime_s` sea mayor que cero, el runtime DEBERÁ armar un watchdog y señalar timeout cuando el programa supere la duración configurada.

#### Scenario: Ejecución limitada en tiempo

- DADA una política de sesión con máximo de 30 segundos
- CUANDO el programa sigue ejecutándose después de 30 segundos
- ENTONCES el runtime DEBERÁ marcarlo agotado por tiempo y solicitar su terminación.

### Requirement: Depuración a nivel de código fuente
El runtime MUST cumplir este requisito.

Cuando el modo debug esté activo, el runtime DEBERÁ permitir breakpoints, step y continue para líneas del código del estudiante. Las cargas de depuración DEBERÁN contener línea actual y, cuando estén disponibles, variables locales y watches serializables y acotados.

#### Scenario: Pausa por breakpoint

- DADO el modo debug activo con un breakpoint en una línea fuente
- CUANDO la ejecución alcanza esa línea
- ENTONCES el runtime DEBERÁ publicar un evento de pausa
- Y NO DEBERÁ avanzar la ejecución hasta recibir continue, step o stop.

### Requirement: Protocolo IPC versionado del worker
El runtime MUST cumplir este requisito.

El runtime aislado DEBERÁ intercambiar comandos y eventos mediante mensajes
serializables con `protocol_version`, `session_id`, secuencia monotónica y
correlación `command_id`. DEBERÁ soportar inicialización, carga, inicio, pausa,
reanudación, parada, reinicio, depuración, mundo, snapshots, errores y cierre.

#### Scenario: Cancelación no cooperativa

- DADO un worker que no confirma `stop` dentro de su presupuesto
- CUANDO el proceso principal agota la espera
- ENTONCES DEBERÁ terminar el worker
- Y publicar `stopped` o `timed_out` conservando el último snapshot válido.

### Requirement: Aislamiento de ejecución y política de watchdog
El runtime MUST cumplir este requisito.

El runtime DEBERÁ ejecutar programas de usuario en un worker aislado del proceso
de interfaz/API. El worker DEBERÁ aplicar límite positivo de tiempo en producción,
límites de CPU y memoria, filesystem temporal restringido, red deshabilitada y
terminación forzada. El filtro de imports del runtime DEBERÁ mantenerse como
defensa adicional y no como única frontera de seguridad.

#### Scenario: Programa no cooperativo

- DADO un programa que no responde al evento de parada
- CUANDO supera el límite de recursos o se solicita detenerlo
- ENTONCES el proceso principal DEBERÁ terminar el worker de forma segura
- Y la sesión DEBERÁ informar estado `timed_out` o `stopped` sin afectar otras sesiones.

### Requirement: Worker como ruta predeterminada
El runtime MUST cumplir este requisito.

La ejecución de scripts DEBERÁ realizarse en un worker aislado por defecto. El
modo local DEBERÁ requerir una configuración explícita de desarrollo o pruebas.

#### Scenario: Ejecución estándar

- DADO una sesión creada sin configuración de compatibilidad local
- CUANDO se inicia un script
- ENTONCES los comandos y eventos DEBERÁN atravesar el worker versionado.

### Requirement: Verificación temporal de ejecución y renderizado Web

La campaña Web MUST medir y registrar la relación entre reloj de pared,
`sim_time_s`, ticks, snapshots y frames. El renderizado no MUST modificar la
semántica temporal de Pybricks.

#### Scenario: Espera y movimiento de duración conocida

- DADO un programa que usa `wait`, motor o DriveBase
- CUANDO se ejecuta en navegador real
- ENTONCES el informe DEBERÁ registrar su duración de pared, tiempo simulado y
  ticks, comparados con una tolerancia declarada
- Y una desviación deberá clasificarse con causa y evidencia.

#### Scenario: Interpolación visual activa

- DADO dos snapshots consecutivos de una ejecución
- CUANDO el canvas interpola posición u orientación
- ENTONCES tick, LCD, sensores, motores, tiempo y estado DEBERÁN conservar el
  último snapshot autoritativo
- Y la interpolación NO DEBERÁ adelantar la finalización del programa.

## Límite de seguridad

Este runtime es una capa de restricción de conveniencia, NO una frontera sólida de seguridad frente a Python hostil. Ejecuta `exec` dentro del proceso de la aplicación. Los despliegues que acepten código público no confiable DEBERÁN aislar la ejecución en proceso o contenedor con límites de CPU, memoria, filesystem, red y tiempo.
