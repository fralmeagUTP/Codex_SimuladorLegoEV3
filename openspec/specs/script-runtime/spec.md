# Especificación: runtime de scripts

## Propósito

Ejecutar programas Python del estudiante contra la API virtual y coordinar ciclo de vida, depuración, comandos bloqueantes, errores y timeout.

## Requisitos

### Requisito: Namespace de programa restringido

El runtime DEBERÁ ejecutar el programa cargado en un namespace construido con la política de ejecución. DEBERÁ exponer sólo builtins seguros configurados, módulos estándar permitidos y módulos Pybricks virtuales. Las importaciones directas fuera del conjunto permitido DEBERÁN fallar con `ImportError`.

#### Escenario: Importación bloqueada del sistema operativo

- DADA una política de ejecución predeterminada
- CUANDO un programa importa `os`, `subprocess` o `socket`
- ENTONCES la ejecución DEBERÁ fallar con error de importación
- Y la sesión DEBERÁ informar el error sin detener otras sesiones.

### Requisito: Ciclo de vida del programa

El runtime DEBERÁ informar estados inactivo, ejecutando, finalizado, detenido, agotado por tiempo o con error, según corresponda. El retorno natural del código DEBERÁ producir estado finalizado; una parada explícita DEBERÁ señalizar el evento de detención y liberar operaciones en espera cuando sea posible.

#### Escenario: Finalización natural

- DADO un programa válido y finito
- CUANDO alcanza el final de su código fuente
- ENTONCES el runtime DEBERÁ marcar la ejecución como finalizada
- Y DEBERÁ notificar a la aplicación o sesión propietaria.

### Requisito: Errores de runtime

El runtime DEBERÁ capturar excepciones de sintaxis y ejecución, preservar mensaje y traceback, y emitir un evento de error para la sesión propietaria.

#### Escenario: Sentencia inválida

- DADO código con error de sintaxis Python
- CUANDO el runtime lo inicia
- ENTONCES la sesión DEBERÁ informar estado de error y traceback
- Y el proceso web DEBERÁ seguir disponible para las demás sesiones.

### Requisito: Política de watchdog

Cuando `max_runtime_s` sea mayor que cero, el runtime DEBERÁ armar un watchdog y señalar timeout cuando el programa supere la duración configurada.

#### Escenario: Ejecución limitada en tiempo

- DADA una política de sesión con máximo de 30 segundos
- CUANDO el programa sigue ejecutándose después de 30 segundos
- ENTONCES el runtime DEBERÁ marcarlo agotado por tiempo y solicitar su terminación.

### Requisito: Depuración a nivel de código fuente

Cuando el modo debug esté activo, el runtime DEBERÁ permitir breakpoints, step y continue para líneas del código del estudiante. Las cargas de depuración DEBERÁN contener línea actual y, cuando estén disponibles, variables locales y watches serializables y acotados.

#### Escenario: Pausa por breakpoint

- DADO el modo debug activo con un breakpoint en una línea fuente
- CUANDO la ejecución alcanza esa línea
- ENTONCES el runtime DEBERÁ publicar un evento de pausa
- Y NO DEBERÁ avanzar la ejecución hasta recibir continue, step o stop.

## Límite de seguridad

Este runtime es una capa de restricción de conveniencia, NO una frontera sólida de seguridad frente a Python hostil. Ejecuta `exec` dentro del proceso de la aplicación. Los despliegues que acepten código público no confiable DEBERÁN aislar la ejecución en proceso o contenedor con límites de CPU, memoria, filesystem, red y tiempo.
