# Especificación: interfaces de usuario

## Propósito

Presentar simulador, editor educativo de código, brick virtual, telemetría y creación de mundos mediante la web principal y Tkinter heredado.

## Requisitos

### Requisito: Rutas web principales

La aplicación Flask DEBERÁ proporcionar simulación en `/`, creación de mundos en `/worlds` y ayuda en `/help`. Los flujos de simulación y editor DEBERÁN estar separados en sus páginas respectivas.

#### Escenario: Abrir simulador

- CUANDO un usuario abre `/`
- ENTONCES la UI DEBERÁ crear o recuperar una sesión de simulación propia
- Y DEBERÁ mostrar controles de código, canvas de mundo, panel del brick y telemetría.

### Requisito: Renderizado del estado web

La UI web DEBERÁ renderizar el último snapshot válido del backend para pose, telemetría de motores, sensores, colisión, LED, LCD y altavoz. DEBERÁ usar SSE cuando esté disponible y polling como alternativa.

#### Escenario: Snapshot actualiza brick

- DADO que el último snapshot informa un tono de altavoz activo
- CUANDO la UI procesa ese snapshot
- ENTONCES el panel del brick DEBERÁ mostrar frecuencia, duración y volumen.

### Requisito: Edición y depuración en navegador

La UI web DEBERÁ proporcionar edición de código con números de línea y ayudas soportadas, además de controles run, stop/reset, breakpoint, step y continue.

#### Escenario: Establecer breakpoint

- DADO un código cargado en modo debug
- CUANDO el usuario alterna una línea válida en el gutter
- ENTONCES la UI DEBERÁ enviar el conjunto de breakpoints a la sesión propietaria.

### Requisito: Flujo del editor de mundos

La UI de mundos DEBERÁ permitir seleccionar, ubicar, mover, rotar, duplicar, eliminar, validar, guardar, importar y exportar assets soportados. Un mundo válido guardado DEBERÁ exponer una ruta directa para cargarlo en la UI de simulación.

#### Escenario: Guardar mundo válido

- DADO un mundo que supera la validación
- CUANDO el usuario lo guarda con nombre válido
- ENTONCES la UI DEBERÁ persistirlo y proporcionar el enlace de simulación.

### Requisito: Escala visual y acceso responsivo

El mapa web DEBERÁ preservar la escala compartida de 32 píxeles por 100 mm y las dimensiones base de 2000 mm. Cuando el panel sea menor que el mapa, la UI DEBERÁ permitir navegación sin deformar proporciones físicas.

#### Escenario: Viewport pequeño

- DADO un viewport más pequeño que el mapa base
- CUANDO el usuario visualiza un mundo
- ENTONCES el mapa DEBERÁ conservar proporciones y ser navegable mediante diseño responsivo y scroll.

### Requisito: Compatibilidad de escritorio heredado

La interfaz Tkinter DEBERÁ seguir operando contra la fachada de aplicación en los flujos existentes. Las nuevas funcionalidades de usuario DEBERÍAN dirigirse primero a web; los cambios de escritorio DEBERÁN limitarse a compatibilidad y correcciones salvo cambio OpenSpec aprobado que amplíe su alcance.
