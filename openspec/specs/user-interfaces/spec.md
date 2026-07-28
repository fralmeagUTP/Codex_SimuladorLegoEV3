# Especificación: interfaces de usuario

## Purpose

Presentar simulador, editor educativo de código, brick virtual, telemetría y creación de mundos mediante la web principal y Tkinter heredado.
## Requirements
### Requirement: Rutas web principales
La interfaz MUST cumplir este requisito.

La aplicación Flask DEBERÁ proporcionar simulación en `/`, creación de mundos en `/worlds` y ayuda en `/help`. Los flujos de simulación y editor DEBERÁN estar separados en sus páginas respectivas.

#### Scenario: Abrir simulador

- CUANDO un usuario abre `/`
- ENTONCES la UI DEBERÁ crear o recuperar una sesión de simulación propia
- Y DEBERÁ mostrar controles de código, canvas de mundo, panel del brick y telemetría.

### Requirement: Renderizado del estado web
La interfaz MUST cumplir este requisito.

La UI web DEBERÁ renderizar el último snapshot válido del backend para pose, telemetría de motores, sensores, colisión, LED, LCD y altavoz. DEBERÁ usar SSE cuando esté disponible y polling como alternativa.

#### Scenario: Snapshot actualiza brick

- DADO que el último snapshot informa un tono de altavoz activo
- CUANDO la UI procesa ese snapshot
- ENTONCES el panel del brick DEBERÁ mostrar frecuencia, duración y volumen.

### Requirement: Edición y depuración en navegador
La interfaz MUST cumplir este requisito.

La UI web DEBERÁ proporcionar edición de código con números de línea y ayudas soportadas, además de controles run, stop/reset, breakpoint, step y continue.

#### Scenario: Establecer breakpoint

- DADO un código cargado en modo debug
- CUANDO el usuario alterna una línea válida en el gutter
- ENTONCES la UI DEBERÁ enviar el conjunto de breakpoints a la sesión propietaria.

### Requirement: Flujo del editor de mundos
La interfaz MUST cumplir este requisito.

La UI de mundos DEBERÁ permitir seleccionar, ubicar, mover, rotar, duplicar, eliminar, validar, guardar, importar y exportar assets soportados. Un mundo válido guardado DEBERÁ exponer una ruta directa para cargarlo en la UI de simulación.

#### Scenario: Guardar mundo válido

- DADO un mundo que supera la validación
- CUANDO el usuario lo guarda con nombre válido
- ENTONCES la UI DEBERÁ persistirlo y proporcionar el enlace de simulación.

### Requirement: Escala visual y acceso responsivo
La interfaz MUST cumplir este requisito.

El mapa web DEBERÁ preservar la escala compartida de 32 píxeles por 100 mm y las dimensiones base de 2000 mm. Cuando el panel sea menor que el mapa, la UI DEBERÁ permitir navegación sin deformar proporciones físicas.

#### Scenario: Viewport pequeño

- DADO un viewport más pequeño que el mapa base
- CUANDO el usuario visualiza un mundo
- ENTONCES el mapa DEBERÁ conservar proporciones y ser navegable mediante diseño responsivo y scroll.

### Requirement: Compatibilidad de escritorio heredado
La interfaz MUST cumplir este requisito.

La interfaz Tkinter DEBERÁ seguir operando contra la fachada de aplicación en los flujos existentes. Las nuevas funcionalidades de usuario DEBERÍAN dirigirse primero a web; los cambios de escritorio DEBERÁN limitarse a compatibilidad y correcciones salvo cambio OpenSpec aprobado que amplíe su alcance.

#### Scenario: conservar compatibilidad de escritorio

- DADO un flujo existente de simulación en Tkinter,
- CUANDO se entrega una actualización de interfaz,
- ENTONCES la aplicación MUST conservar ese flujo o documentar el cambio aprobado.

### Requirement: navegación funcional equivalente

Web y Tkinter MUST exponer destinos descubribles para simulación, creación de
mundos, ayuda didáctica y acerca de. Los destinos pueden ser rutas Web o
ventanas nativas, pero DEBEN conducir a la misma capacidad funcional.

#### Scenario: descubrir ayuda contextual

- DADO un usuario que necesita crear un mundo, ejecutar un script o depurar,
- CUANDO abre la ayuda desde Web o Tkinter,
- ENTONCES encuentra tutoriales para las tres tareas con pasos, resultado
  esperado y recuperación,
- Y PUEDE abrir el destino funcional correspondiente.

### Requirement: retorno de mundo guardado a simulación

Tras guardar un mundo válido, ambas interfaces MUST ofrecer una acción para
abrirlo inmediatamente en simulación.

#### Scenario: simular mundo recién guardado

- DADO un mundo válido recién guardado desde el editor,
- CUANDO el usuario elige simularlo,
- ENTONCES la interfaz carga ese mismo archivo en la sesión de simulación,
- Y muestra la simulación con el mundo activo.

#### Scenario: error al aplicar un mundo guardado

- DADO un error de lectura o aplicación del archivo guardado,
- CUANDO el usuario elige simularlo,
- ENTONCES la interfaz informa el error,
- Y NO reemplaza el mundo activo de la sesión.

### Requirement: paridad visual entre interfaces

Tkinter MUST implementar el sistema visual y la organización de controles de la Web.

Tkinter DEBE implementar el sistema visual y la organización de controles de la Web, que actúa como fuente de verdad.

#### Scenario: acción equivalente

- Dado un usuario en Web o Tkinter,
- cuando consulta una acción de simulación, mundo, editor, depuración, perfil o traza,
- entonces encuentra la misma etiqueta, orden, estado y atajo aplicable.

#### Scenario: tema y estado

- Dado un tema o estado de sesión,
- cuando cambie a ejecución, pausa, error o deshabilitado,
- entonces ambas interfaces comunican el estado con tokens semánticos equivalentes.

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

### Requirement: Equivalencia Web y Tkinter
Las interfaces MUST cumplir este requisito.

La aplicación Flask y la aplicación Tkinter DEBERÁN proporcionar funcionalidades
exactamente equivalentes. Ambas DEBERÁN incluir simulación, edición, ejecución,
pausa, reanudación, parada, reinicio, depuración, telemetría, brick virtual,
edición de mundos, carga/guardado/importación/exportación, trazas, ayuda y toda
función futura aplicable. Podrán diferir en presentación visual, pero no en
capacidad funcional, validación, transición de estado ni resultado observable.

#### Scenario: Flujo completo en cualquiera de las interfaces

- DADO el mismo programa, mundo y configuración
- CUANDO un usuario completa un flujo soportado desde Web o Tkinter
- ENTONCES ambas interfaces DEBERÁN alcanzar el mismo estado de sesión y resultado de simulación.

#### Scenario: Entrega de funcionalidad nueva

- DADA una funcionalidad nueva aplicable a una interfaz
- CUANDO se solicita su cierre de desarrollo
- ENTONCES DEBERÁ tener implementación y prueba de aceptación en Web y Tkinter
- Y no podrá declararse completada si falta en una de ellas.

### Requirement: Paridad moderna de interfaces
Las interfaces MUST cumplir este requisito.

Web y Tkinter DEBERÁN consumir el mismo contrato de sesión y ofrecer controles
equivalentes de ejecución, depuración, perfiles, trazas, accesibilidad y teclado.

#### Scenario: Misma operación en ambas interfaces

- DADO un caso de uso del catálogo compartido
- CUANDO se ejecuta en Web y Tkinter
- ENTONCES ambos clientes DEBERÁN producir estados y snapshots equivalentes.
