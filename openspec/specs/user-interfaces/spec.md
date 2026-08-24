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

### Requirement: Arranque visible de escritorio

La aplicación Tkinter MUST mostrar primero una pantalla de inicio centrada de 800×450 píxeles y MUST abrir después la ventana principal maximizada.

#### Scenario: Inicio normal de la aplicación

- **WHEN** el usuario inicia el punto de entrada de escritorio
- **THEN** se muestra la introducción de 800×450 px
- **AND** al cerrarse la introducción se presenta la ventana principal maximizada.

### Requirement: Visualización LCD del EV3 Brick

La interfaz Tkinter MUST renderizar la pantalla LCD lógica de 178×128 en un área visual nuevamente 30 % mayor, con canvas de referencia 507×169 px y sin alterar el contenido de telemetría o del Brick.

#### Scenario: Panel Brick visible

- **WHEN** el panel EV3 Brick se construye en la aplicación de escritorio
- **THEN** su canvas LCD usa una referencia de 507×169 px
- **AND** conserva la proporción de la pantalla lógica 178×128.

### Requirement: Controles de mapa utilizables en móvil

La interfaz Web MUST ajustar canvas y controles del mapa al ancho disponible
del viewport, sin scroll horizontal no intencional ni controles recortados.

#### Scenario: Viewport de 390×844

- DADO un navegador de 390×844 píxeles
- CUANDO se carga el simulador Web
- ENTONCES el canvas NO DEBERÁ exceder el ancho de su contenedor
- Y el botón de haces DEBERÁ permanecer completamente visible y operable.

### Requirement: Coherencia visual de snapshot

La interfaz Web MUST ignorar snapshots de generaciones antiguas y ticks fuera
de orden dentro de la generación activa.

#### Scenario: Evento tardío tras reset

- DADO que el cliente ya aplicó el snapshot inicial de una nueva generación
- CUANDO recibe un snapshot de una generación anterior
- ENTONCES NO DEBERÁ modificar canvas, LCD, telemetría ni controles.

### Requirement: Telemetría Tkinter responsive y legible

La interfaz MUST mantener esta garantía de legibilidad.

La interfaz Tkinter DEBERÁ mantener la telemetría legible en 1024×768,
1280×800 y 1920×1080, en tema claro y oscuro. Ninguna etiqueta, valor,
encabezado o estado crítico podrá quedar recortado, solapado o fuera de su
celda visible.

#### Scenario: Ancho reducido de telemetría

- DADO un panel cuyo ancho no permite el diseño preferido
- CUANDO Tkinter recalcula el layout
- ENTONCES DEBERÁ aplicar reflujo, punto de ruptura o scroll interno accesible
  antes de recortar texto
- Y los valores extensos deberán conservar acceso completo mediante ajuste o
  tooltip.

### Requirement: Estado del robot accesible desde Brick

El panel MUST mantener esta capacidad de acceso.

El panel EV3 Brick DEBERÁ mostrar o permitir alcanzar claramente la tabla
Robot/Estado junto con la LCD, sin deformar esta última.

#### Scenario: Alto reducido de Brick

- DADO que la altura disponible no permite mostrar LCD y Robot/Estado a la vez
- CUANDO se renderiza el Brick
- ENTONCES el panel DEBERÁ proporcionar scroll vertical independiente o una
  composición responsive
- Y X, Y y Theta deberán permanecer accesibles.

### Requirement: Cierre Tkinter libre de callbacks pendientes

La ventana MUST mantener esta garantía de cierre seguro.

La ventana Tkinter DEBERÁ cancelar de forma segura callbacks de layout, resize
e idle antes de destruir la raíz; el cierre deberá ser idempotente.

#### Scenario: Cierre con layout pendiente

- DADO un callback responsive programado
- CUANDO el usuario o el capturador cierra la ventana
- ENTONCES no DEBERÁ aparecer un error Tcl ni una invocación contra widgets
  destruidos.

### Requirement: Telemetría inicialmente escaneable en escritorio

La interfaz Tkinter MUST mostrar una telemetría útil sin scroll vertical innecesario a 1280x800.

#### Scenario: Inicio de simulador a 1280x800

- **WHEN** el usuario abre el simulador Tkinter en 1280x800
- **THEN** la telemetría muestra resumen, motores A-D y sensores S1-S4 sin texto superpuesto, recortado ni contraste insuficiente

#### Scenario: Altura reducida

- **WHEN** la altura disponible no permite mostrar todas las tarjetas
- **THEN** el desplazamiento conserva orden, etiquetas y acceso a Robot/Estado

### Requirement: bloqueo de menús durante una ejecución activa

Las interfaces Web y Tkinter MUST deshabilitar de manera coherente los comandos de menú que alteran el contexto de simulación mientras el estado de sesión sea `running` o `paused`.

#### Scenario: script ejecutándose

- **WHEN** la persona usuaria inicia un script y la sesión pasa a `running`
- **THEN** los comandos de menú de contexto quedan deshabilitados
- **AND** los controles Pausar, Reanudar y Detener y reiniciar conservan el comportamiento permitido por su estado.

#### Scenario: script pausado

- **WHEN** una sesión pasa de `running` a `paused`
- **THEN** los comandos de menú de contexto permanecen deshabilitados
- **AND** no es posible cargar ni cambiar un mundo, ejemplo, escenario o misión.

### Requirement: reactivación de menús al finalizar o restablecer una sesión

Las interfaces Web y Tkinter MUST habilitar los comandos de menú de contexto al recibir cualquiera de los estados `created`, `ready`, `finished`, `stopped`, `timed_out`, `error` o `reset`.

#### Scenario: finalización natural

- **WHEN** un script termina correctamente y la sesión informa `finished`
- **THEN** los comandos de menú vuelven a estar disponibles sin recargar la interfaz
- **AND** la persona usuaria puede seleccionar otro ejemplo, mundo, escenario o misión.

#### Scenario: detener y reiniciar

- **WHEN** la persona usuaria solicita Detener y reiniciar
- **THEN** la sesión llega a un estado preparado o restablecido
- **AND** los comandos de menú quedan habilitados.

#### Scenario: finalización excepcional

- **WHEN** la sesión termina con `error` o `timed_out`
- **THEN** los comandos de menú quedan habilitados
- **AND** el mensaje de error o tiempo agotado permanece visible conforme al comportamiento actual.

### Requirement: paridad de política entre interfaces

Web y Tkinter MUST aplicar la misma matriz de disponibilidad para un mismo estado de sesión.

#### Scenario: transición terminal repetida

- **WHEN** una interfaz recibe de forma repetida un snapshot terminal
- **THEN** el estado de los menús permanece habilitado
- **AND** no se producen comandos duplicados ni errores de interfaz.

### Requirement: Movimiento Web visualmente fluido

El canvas Web SHALL renderizar movimiento continuo mediante interpolación entre
snapshots compatibles y requestAnimationFrame, sin modificar los datos
autoritativos de telemetría.

#### Scenario: Giro continuo

- **WHEN** el robot recibe snapshots consecutivos de un giro
- **THEN** el robot y sus haces se dibujan con orientaciones intermedias
- **AND** la telemetría conserva el último tick recibido sin valores inventados

#### Scenario: Reinicio o cambio de mundo

- **WHEN** el usuario detiene y reinicia o carga otro mundo
- **THEN** se descarta el buffer de interpolación y la vista muestra la pose
  inicial correspondiente sin trazas ni movimiento residual

### Requirement: Confirmación de ejecución exitosa

Las interfaces Web y Tkinter MUST informar `El programa se ejecutó correctamente.` exactamente una vez cuando la ejecución activa alcance el estado terminal `finished`, después de reflejar el snapshot terminal en sus vistas.

#### Scenario: Script válido termina correctamente

- **WHEN** un usuario ejecuta un programa Pybricks válido y este alcanza `finished`
- **THEN** la interfaz muestra una única confirmación de ejecución correcta
- **AND** canvas, LCD, telemetría y barra de estado ya representan el snapshot terminal.

#### Scenario: Estado no exitoso

- **WHEN** una ejecución alcanza `error`, `timed_out`, `stopped` o `reset`
- **THEN** la interfaz no muestra la confirmación de ejecución correcta.

### Requirement: Presentación accesible y no bloqueante en Web

La interfaz Web MUST mostrar la confirmación como un toast no modal, con región `aria-live`, cierre manual, desaparición automática y contraste válido en temas claro y oscuro.

#### Scenario: Cierre y viewport móvil

- **WHEN** el toast de éxito está visible en un viewport móvil
- **THEN** el usuario puede cerrarlo mediante un control accesible
- **AND** el toast no cubre ni desborda los controles críticos.

### Requirement: Centro de ayuda orientado a tareas

Las interfaces Web y Tkinter MUST ofrecer un Centro de ayuda con rutas de
aprendizaje por tarea, categorías navegables, resultados esperados y pasos de
recuperación, usando el nombre visible `Simulador EV3 Pybricks`.

#### Scenario: Usuario inicia su primera simulación

- **WHEN** una persona abre el Centro de ayuda y selecciona `Mi primera simulación`
- **THEN** la interfaz muestra prerrequisitos, pasos ordenados, resultado
  esperado, recuperación y una acción para abrir la simulación
- **AND** la acción no anuncia ni invoca una capacidad no disponible.

#### Scenario: Paridad de guía entre interfaces

- **WHEN** una guía está disponible en Web y Tkinter
- **THEN** ambas presentan el mismo identificador, objetivo, pasos, resultado y
  recuperación
- **AND** solo pueden diferir los controles propios de la plataforma.

### Requirement: Navegación, búsqueda y accesibilidad

El Centro de ayuda MUST permitir navegar por categorías y buscar por título,
resumen, etiquetas y pasos, con uso completo de teclado y contraste válido en
los temas claro y oscuro.

#### Scenario: Búsqueda sin resultados

- **WHEN** el usuario busca un término que no coincide con ninguna guía
- **THEN** la interfaz informa que no hay resultados y conserva un camino para
  limpiar la búsqueda o volver a las categorías.

#### Scenario: Uso en Web móvil

- **WHEN** el Centro de ayuda se muestra en un viewport de 390×844
- **THEN** el índice se puede abrir y cerrar sin provocar scroll horizontal
- **AND** las acciones y el contenido siguen siendo utilizables mediante toque
  y teclado.

### Requirement: Ayuda contextual para operaciones críticas

Las interfaces MUST ofrecer acceso a una guía contextual desde los controles y
errores de ejecución, reinicio, límites de tiempo, ubicación, haces, trazas,
depuración, telemetría y validación de mundos.

#### Scenario: Error con recuperación disponible

- **WHEN** un error de script o validación tiene una guía de recuperación
  asociada
- **THEN** el usuario puede abrir esa guía desde el mensaje o control contextual
- **AND** la ayuda describe una solución verificable para el caso.

### Requirement: Avance de tick verificable

Cuando la interfaz Web confirme que avanzó un tick, MUST haber recibido y
aplicado un snapshot de la generación activa con tick estrictamente mayor. Si el
motor no puede avanzar en el estado actual, el control DEBERÁ estar deshabilitado
o explicar que no se realizó avance.

#### Scenario: Avanzar un tick con traza activa

- DADA una sesión preparada para avance manual y una traza iniciada
- CUANDO el usuario selecciona Avanzar un tick
- ENTONCES el tick visible DEBERÁ incrementarse
- Y la traza DEBERÁ contener la transición correspondiente.

### Requirement: Ritmo observable de simulación

La interfaz Web MUST mantener el progreso visible alineado con el tiempo
simulado, sin que la interpolación altere la semántica de estados, LCD o
telemetría.

#### Scenario: Espera de un segundo

- DADO un script que ejecuta `wait(1000)`
- CUANDO se ejecuta en el entorno de referencia
- ENTONCES la relación entre tiempo de pared y `sim_time_s` DEBERÁ cumplir el
  presupuesto de rendimiento documentado
- Y el canvas DEBERÁ seguir produciendo frames mientras la sesión esté activa.

### Requirement: Coherencia visible de la sesión

Cada interfaz MUST actualizar el estado terminal o de reinicio de una sesión
como una unidad coherente antes de habilitar comandos dependientes o mostrar una
notificación terminal.

#### Scenario: Finalización correcta del programa

- **DADO** un programa que finaliza correctamente;
- **CUANDO** la interfaz recibe su snapshot terminal actual;
- **ENTONCES** editor, barra de estado, robot, canvas, LCD y telemetría
  representarán ese mismo estado;
- **Y** la notificación de éxito se emitirá una sola vez después de actualizar
  la interfaz.

### Requirement: Sistema de diseño y navegación compartidos

Web y Tkinter MUST consumir tokens y catálogos comunes para nombre de
acción, jerarquía, estado, foco, color semántico, atajo y recuperación. Podrán
diferir los widgets nativos, pero no la intención ni la accesibilidad.

#### Scenario: Control de ejecución en tema oscuro

- DADO el control equivalente de ejecución en ambas interfaces;
- CUANDO una sesión cambia a ejecución, pausa, error o estado deshabilitado en
  tema oscuro;
- ENTONCES el usuario distingue el estado con contraste suficiente y foco
  visible;
- Y el control produce la misma transición de sesión.

### Requirement: Ayuda contextual equivalente

Las dos interfaces MUST presentar la misma ayuda por tarea, objetivo,
resultado esperado y recuperación para operaciones aplicables.

#### Scenario: Usuario recibe un error recuperable

- DADO un error de script, mundo, límite de tiempo o depuración;
- CUANDO la interfaz muestra el error;
- ENTONCES ofrece la guía contextual equivalente;
- Y la guía no recomienda una acción ausente de la plataforma actual.

### Requirement: Catálogo visual único de assets

Web y Tkinter MUST renderizar las mismas figuras, imágenes, sprites,
texturas e iconos definidos por un catálogo versionado común. Un recurso solo
podrá diferir por escalado, antialiasing o mecanismo de empaquetado documentado,
no por contenido, versión o significado.

#### Scenario: Asset actualizado para un obstáculo

- DADO un `asset_id` de obstáculo actualizado;
- CUANDO se publica una versión del producto;
- ENTONCES Web y Tkinter muestran la misma figura y variante del catálogo;
- Y las pruebas comprueban el hash o la procedencia de ambos recursos.

#### Scenario: Asset ausente en una distribución

- DADO un asset requerido por un mundo, ayuda o pantalla de inicio;
- CUANDO se construye Web, ejecutable, ZIP o instalador;
- ENTONCES la validación falla si el recurso no está presente o no corresponde
  a la versión declarada del catálogo.

### Requirement: Composición visual equivalente del simulador

Web y Tkinter MUST presentar una jerarquía equivalente de controles,
canvas, editor, telemetría y EV3 Brick. El Brick DEBERÁ agrupar LCD y
Robot/Estado; la telemetría DEBERÁ conservar bloques legibles de motores y
sensores. Las diferencias de widget nativo o viewport DEBERÁN documentarse y
NO podrán ocultar ni cambiar información.

#### Scenario: Área de trabajo en escritorio

- DADO el mismo mundo abierto en Web y Tkinter a 1280×800 o mayor
- CUANDO se muestra la simulación en estado listo o ejecutando
- ENTONCES el usuario encuentra canvas, editor, telemetría y Brick con la
  misma jerarquía informativa
- Y LCD, Robot/Estado, motores y sensores permanecen visibles o accesibles
  mediante un ajuste o scroll interno explícito.

### Requirement: Estados visibles normalizados

Las interfaces MUST renderizar el mismo texto localizado y token semántico
para `ready`, `running`, `paused`, `finished`, `error`, `timed_out` y
`stopped`. Los valores técnicos internos NO DEBERÁN aparecer como etiquetas
inconsistentes para el usuario final.

#### Scenario: Ejecución activa

- DADA una sesión cuyo estado interno es `running`
- CUANDO se actualizan la barra de estado y la telemetría en Web y Tkinter
- ENTONCES ambas muestran `Ejecutando` y el mismo color semántico accesible.

