# Manual de Usuario - Simulador EV3 Pybricks

Version documentada: 1.5.0
Fecha de actualización: 2026-08-05

## 1. Objetivo

Este programa permite:

- Escribir y ejecutar scripts Python compatibles con Pybricks.
- Simular el robot EV3 en un mundo 2D.
- Crear y editar mundos personalizados con el Editor de Mundos EV3.

## 1.1 Estado de interfaces

- La Web es la referencia de diseno, etiquetas, orden de controles y estados.
- La interfaz de escritorio Tkinter ofrece el mismo flujo de simulacion y el
  mismo catalogo de controles para uso local y sin navegador.
- Toda funcion nueva de simulacion debe conservar la paridad funcional y visual
  entre ambas interfaces.

## 2. Uso Web con Flask

La version web separa dos funcionalidades que antes estaban juntas en la aplicacion de escritorio:

- **Simulacion del robot**: `http://127.0.0.1:5050/`
- **Creacion de mundos**: `http://127.0.0.1:5050/worlds`

Esta separacion evita ejecutar codigo mientras se esta construyendo un mundo y permite que cada flujo tenga controles propios.

### 2.1 Iniciar el servidor web

Desde PowerShell:

```powershell
cd <ruta-del-repositorio>
.\scripts\start_web.cmd
```

Si Windows bloquea la ejecucion de `.ps1`, usar:

```powershell
.\scripts\start_web.cmd
```

Abrir en el navegador:

```text
http://127.0.0.1:5050/
```

### 2.2 Pagina de simulacion

Ruta: `http://127.0.0.1:5050/`

Funciones:

- Escribir o cargar codigo Pybricks.
- Seleccionar ejemplos desde `examples/`.
- Seleccionar mundos guardados desde `worlds/`.
- Ejecutar, pausar y reanudar simulacion.
- Detener y reiniciar simulacion con un unico boton: `Detener y reiniciar`.
- Ver canvas, telemetria, motores, sensores, LED y pantalla EV3.
- Usar depuracion con breakpoints, step y continue.
- Ver resaltado de la linea actual durante depuracion.
- Ubicar robot desde el canvas y ajustar `theta`.

La pagina de simulacion no incluye controles para crear o editar mundos.

Nota: cuando un script finaliza naturalmente, la sesion publica `finished` y
conserva el estado final visible. Usa `Detener y reiniciar` para iniciar un
nuevo ciclo de simulacion.

### 2.3 Pagina de creacion de mundos

Ruta: `http://127.0.0.1:5050/worlds`

Funciones:

- Crear un mundo nuevo.
- Colocar robot, muros, lineas, zonas y pisos.
- Mover, rotar, duplicar y eliminar assets.
- Arrastrar assets directamente sobre el canvas.
- Editar propiedades de asset desde el panel lateral.
- Definir pose inicial del robot.
- Validar el mundo.
- Importar y exportar JSON.
- Guardar mundos en `worlds/`.

La pagina de mundos no incluye editor de codigo ni botones para ejecutar la simulacion.

### 2.4 Flujo recomendado web

1. Abrir `http://127.0.0.1:5050/worlds`.
2. Crear el mundo y colocar los assets requeridos.
3. Colocar el robot o definir su pose inicial.
4. Validar el mundo.
5. Guardar el mundo con un nombre, por ejemplo `prueba_lineas`.
6. Usar el enlace **Simular mundo guardado**.
7. La simulacion abre `/?world=prueba_lineas.json` y carga el mundo automaticamente.
8. Escribir o cargar el script Pybricks.
9. Ejecutar y observar telemetria/canvas.

### 2.5 Sesiones de usuario

Cada pestana crea una sesion web independiente con `session_id` y token interno. Las sesiones separan codigo, mundo cargado, estado de simulacion y eventos SSE.

La version actual usa sesiones temporales en memoria. Si se reinicia el servidor, las pestanas abiertas deben recargarse para crear una sesion nueva.

### 2.6 Depuracion, perfiles y trazas

Las dos interfaces permiten configurar puntos de interrupcion, watches, avanzar
un paso y continuar la ejecucion. El estado de depuracion se recibe mediante el
contrato de sesion y muestra la linea actual cuando el script se pausa.

En **Configuración > Precisión de simulación** se eligen los perfiles disponibles. Los
perfiles no sustituyen la calibracion de un robot fisico; consultar
`Documentos/DIFERENCIAS_SIMULADOR_ROBOT.md` antes de usar una actividad en aula.

En **Diagnóstico > Trazas de simulación** se inicia o detiene el registro, permite avanzar un tick y
exportar la evidencia en JSON/CSV. Las trazas no dependen de la interfaz usada.

### 2.7 Accesibilidad y teclado

- `Ctrl+N`: crear script.
- `Ctrl+O`: abrir script.
- `Ctrl+S`: guardar script.
- `Escape`: cerrar cuadros de ayuda o acerca de cuando estan abiertos.
- Los controles de ejecucion cambian de estado al ejecutar, pausar, finalizar o
  reiniciar para impedir comandos incompatibles.

La Web es la referencia visual. Tkinter reproduce etiquetas, orden, estados y
paleta, con diferencias limitadas a bordes, menus y scrollbars nativos.

### 2.8 Tamano del mapa web

El mapa web usa la misma escala que la aplicacion Tkinter:

- `32 px = 100 mm`.
- Mundo base `2000 x 2000 mm` = `640 x 640 px`.
- Si el panel visible es menor que el mapa, se usa scroll dentro del panel.

Esta regla mantiene proporciones y posiciones de objetos iguales entre escritorio y web.

### 2.9 Detener el servidor web

En PowerShell:

```powershell
.\scripts\stop_web.ps1
```

Alternativa:

```powershell
.\scripts\stop_web.cmd
```

Para reiniciar:

```powershell
.\scripts\restart_web.ps1
```

Alternativa:

```powershell
.\scripts\restart_web.cmd
```

La guia completa de operacion web esta en `Documentos/GUIA_WEB_FLASK_WINDOWS.md`.
Compatibilidad temporal: si todavia no migraste recursos, la app tambien admite `Documentos/Ejemplos` y `Documentos/Mundos`.

## 3. Aplicacion de Escritorio

Las siguientes secciones corresponden a la version de escritorio basada en `tkinter`.

## 4. Ventana Principal

La ventana de escritorio sigue el mismo orden de la pagina de simulacion Web:

- Barra de menús: Archivo, Aprender, Mundos, Prácticas guiadas, Configuración,
  Configuración, Diagnóstico y Ayuda.
- Barra de simulacion: Ejecutar, Pausar, Reanudar y Detener y reiniciar.
- Mundo a la izquierda y editor/depuracion a la derecha.
- Telemetria y EV3 Brick debajo del mundo; la telemetria se divide en Robot,
  Motores y Sensores.
- Franja de estado al pie de la ventana.

Los temas Claro y Oscuro, el foco de teclado y los estados deshabilitados usan
la misma semantica de color que la Web. Las diferencias limitadas a bordes,
desplegables y barras de desplazamiento son propias de los controles nativos
de Windows.

### 4.0 Editor de codigo y colores de sintaxis

El editor identifica palabras clave, nombres integrados, numeros, cadenas y
comentarios. Los comentarios que comienzan con `#`, incluidos los que aparecen
al final de una instruccion, usan un color propio. Los bloques documentales
entre triples comillas (`"""..."""` o `'''...'''`) se muestran como una unica
cadena aunque ocupen varias lineas.

El resaltado se actualiza al escribir y al cambiar entre los temas Claro y
Oscuro; los colores se ajustan para conservar contraste y legibilidad. Un
script incompleto mientras se escribe no bloquea el editor.

### 4.1 Menu Archivo

- `Nuevo script`: limpia el editor para iniciar un script nuevo.
- `Abrir script...`: abre un archivo `.py`.
- `Guardar script...`: guarda el script actual en un archivo `.py`.
- `Salir`: cierra la aplicacion.

Atajos:

- `Ctrl+N`: nuevo script.
- `Ctrl+O`: abrir script.
- `Ctrl+S`: guardar script.

### 4.2 Menú Aprender

Carga scripts de ejemplo desde `examples/`, agrupados en Empezar, Movimiento,
Sensores, Control y navegación y Retos avanzados.

### 4.3 Menu Mundos

- `Cargar mundo JSON...`: carga un mundo desde archivo.
- `Editor de mundos...`: abre el editor visual.
- Lista de mundos detectados en `worlds/`.

### 4.4 Menú Prácticas guiadas

Carga combinaciones predefinidas de objetivo + mundo + script. Antes de confirmar
se informa qué recursos cambiarán; si hay cambios sin guardar, puede cancelar sin
perder el programa actual.

### 4.5 Centro de ayuda contextual

El menú `Ayuda > Centro de ayuda...` abre el mismo catálogo de guías de la
Web. Puedes buscar por una tarea o error, filtrar por categoría y abrir el
flujo correspondiente sin tener que recorrer de nuevo los menús. Cada guía
indica requisitos, pasos, resultado esperado y una forma de recuperación.

### 4.6 Diagnóstico de sesión y soporte

En ambas interfaces, `Diagnóstico` concentra `Diagnóstico de sesión`, trazas y
`Exportar diagnóstico JSON`. `Ayuda` contiene `Centro de ayuda`, `Guía rápida:
primera simulación`, `Libro: Programación en Python para robótica (LEGO EV3)` y
`Acerca de`.

El diagnóstico muestra datos técnicos seguros de la sesión actual (estado,
tick, tiempo y worker cuando exista). En la Web añade métricas de renderizado;
en el escritorio se muestra mediante un diálogo nativo. `Exportar diagnóstico
JSON` crea un archivo UTF-8 versionado para soporte. El archivo no contiene el
código del editor, tokens, contraseñas ni credenciales. `Acerca de` queda
reservado para créditos, versión e información institucional.

El enlace del libro abre en el navegador predeterminado y dirige al repositorio
institucional de UTP para la obra escrita por los autores del proyecto:
**Programación en Python para robótica: de la teoría a la práctica con LEGO
EV3**.

Las instrucciones de instalación, despliegue y operación técnica permanecen
separadas en `GUIA_WEB_FLASK_WINDOWS.md`, `GUIA_DESPLIEGUE_LINUX.md` y
`CONTROLES_CALIDAD.md` para no mezclar el aprendizaje del simulador con tareas
de administración.

Para verificar la navegación nativa con ratón en un equipo Windows con sesión
gráfica, instala `.[desktop-e2e]` y ejecuta:

```powershell
$env:EV3_RUN_DESKTOP_E2E = "1"
.\.venv\Scripts\python.exe -m pytest tests/e2e/test_desktop_pywinauto.py -q
```

## 5. Flujo Basico de Uso

1. Carga o crea un script en el editor.
2. Carga un mundo desde `Mundos` o abre `Editor de mundos...`.
3. Coloca el robot en el mapa (clic y orientacion).
4. Pulsa `Ejecutar`.
5. Observa telemetria, trayectoria y pantalla LCD.
6. Usa `Detener y reiniciar` para cancelar y restaurar el estado inicial, o
   permite que el programa termine y conserva su snapshot final.

## 6. Colocacion del Robot

Antes de ejecutar:

- Haz clic en el mapa para definir `X` y `Y`.
- Arrastra o usa la rueda del mouse para ajustar `theta`.
- La barra informativa muestra coordenadas y orientacion.

Convencion de unidades:

- Las coordenadas visibles de `X` y `Y` se muestran en `cm`.
- `theta` se mantiene en grados (`deg`).

Al iniciar la simulacion, el modo de colocacion se desactiva.

## 7. Telemetria

La telemetria muestra:

- Estado del robot (X, Y, theta, colision).
- Motores A/B/C/D (velocidad, angulo, estado).
- Sensores S1/S2/S3/S4 (tipo y valor).
- Tiempo/ticks de simulacion.

Convencion de unidades en UI:

- Distancias visibles (`X`, `Y`, sensor ultrasónico) en `cm`.
- Angulos en `deg`.
- Velocidad angular de motor en `deg/s`.

## 8. Editor de Mundos EV3

Funciones principales:

- Nuevo, abrir, guardar y guardar como.
- Paleta de objetos (robot, muros, zonas, lineas, fondos).
- Colocacion por rejilla.
- Propiedades del objeto seleccionado.
- Validacion del mundo.
- Después de guardar un mundo válido, el botón `Simular mundo guardado` lo
  aplica directamente a la ventana principal. No es necesario volver a buscar
  el archivo JSON desde el menú Mundos.

Reglas clave:

- Solo se permite un robot por mapa.
- El robot del mapa define la posicion inicial en la simulacion.

## 9. Formato de Mundos

Los mundos se guardan en JSON y pueden incluir:

- Dimensiones del mundo.
- Obstaculos y superficies.
- Datos visuales del editor (`editor_spec`).

## 10. Recomendaciones

- Guarda frecuentemente el script y el mundo.
- Usa escenarios para pruebas rapidas.
- Si cambias de mundo, revisa la pose inicial del robot.

## 11. Resolucion de Problemas

- Si un script no ejecuta: revisar errores en la ventana de mensaje.
- Si no ves cambios: confirmar que el mundo correcto esta cargado.
- Si la telemetria no cambia: verificar puertos y creacion de dispositivos en el script.
- Si la web parece colgada: revisar `http://127.0.0.1:5050/healthz`; debe responder HTTP 200 y mostrar `running_simulations`.
- Si un script corto no termina: verificar que la sesion alcance `finished`; el estado final permanece visible hasta que el usuario reinicie manualmente.
- Si el mapa parece cortado: usar scroll dentro del panel; el canvas conserva el tamano real de Tkinter.

## 12. Centro de ayuda y recorridos guiados

El menú **Ayuda** abre el Centro de ayuda en Web y escritorio. Cada guía ofrece
prerrequisitos, pasos marcables, resultado esperado, recuperación y acceso al
destino correcto. El avance se conserva de forma local: no incorpora código,
credenciales ni identificadores de sesión.

Las rutas cubren primera simulación, mundos, motores, sensores, depuración,
misiones, trazas, tiempo máximo y diagnóstico. En Web, las capturas incluyen
texto alternativo y transcripción; en Tkinter se muestran capturas reales de
escritorio con una explicación textual de respaldo.

Para una clase, active **Modo docente**. Propone una práctica de 25 minutos y
la evidencia mínima: captura del mundo, código final, resultado de misión y
explicación de una lectura de sensor. La simulación no reemplaza la validación
en un EV3 físico: confirme puertos, batería, montaje y sensores antes de una
demostración real.

## 13. Version

Manual actualizado para la versión `1.5.0` el 2026-08-05. Consulta
`Documentos/ESTADO_ACTUAL_PROYECTO.md` para la evidencia de liberación vigente.
