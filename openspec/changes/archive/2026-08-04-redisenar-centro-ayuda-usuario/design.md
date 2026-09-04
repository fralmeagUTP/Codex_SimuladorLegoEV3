# Diseño: centro de ayuda del Simulador EV3 Pybricks

## Principios de experiencia

1. **Aprender haciendo.** La ayuda comienza con la siguiente acción concreta,
   no con una descripción de arquitectura o instalación.
2. **Una tarea por pantalla.** Cada guía responde qué hacer, qué se debe ver y
   cómo recuperarse si el resultado no ocurre.
3. **Información progresiva.** Estudiantes ven primero lo esencial; docentes y
   personal técnico acceden a detalles desde enlaces explícitos.
4. **Paridad de significado.** Web y Tkinter comparten catálogo, texto,
   terminología, pasos, resultados y recuperación; solo varía el patrón nativo
   de presentación.
5. **Accesibilidad primero.** Todo contenido se navega con teclado, conserva
   foco visible, contraste suficiente y no depende exclusivamente de color o
   imagen.

## Arquitectura de contenido

El catálogo compartido reemplaza la tupla limitada de tutoriales por entradas
versionadas con: identificador estable, audiencia, categoría, título, resumen,
tiempo estimado, prerrequisitos, pasos, recurso visual, resultado esperado,
recuperación, enlaces relacionados y acción de destino opcional.

Las categorías iniciales son:

- **Empezar:** primera simulación y orientación de la interfaz.
- **Simular:** controles de ejecución, telemetría, LCD, trazas y posición.
- **Crear mundos:** assets, pose inicial, validación, guardado y carga.
- **Programar:** ejemplos, motores, sensores, temporizadores y límites.
- **Depurar:** breakpoints, paso, continuación y lectura de errores.
- **Docencia:** escenarios, misiones y recomendaciones para aula.
- **Resolver problemas:** errores frecuentes y recuperación.
- **Técnico:** instalación, sesiones, operación y límites conocidos.

La identidad textual visible será siempre **Simulador EV3 Pybricks**. Las URLs
se derivan de la configuración o se presentan como enlaces internos; no se
insertarán hosts publicados o locales en el contenido general.

## Presentación Web

La página `/help` contendrá:

1. cabecera con título, resumen, buscador y acceso al cambio de tema;
2. tarjetas de inicio rápido: *Mi primera simulación*, *Crear un mundo*,
   *Usar sensores* y *Depurar un error*;
3. índice lateral fijo o desplegable en pantallas estrechas;
4. área de contenido con bloques de pasos numerados, imagen anotada, resultado
   esperado, recuperación y acciones como **Abrir simulación**;
5. panel de temas relacionados y comentarios de limitación cuando una función
   no replica exactamente al robot físico.

El buscador filtra localmente título, resumen, etiquetas y pasos; anuncia la
cantidad de resultados con `aria-live`. En móvil el índice se convierte en un
desplegable y ninguna tarjeta, acción o imagen provoca scroll horizontal.

## Presentación Tkinter

`Ayuda > Centro de ayuda` abre una única ventana reutilizable, no modal, con:

- barra superior con búsqueda y selector de categoría;
- panel izquierdo con índice de categorías y rutas; en ventana estrecha se
  contrae mediante un botón accesible;
- panel central desplazable que renderiza encabezados, tarjetas, listas,
  avisos, imágenes y enlaces en widgets nativos, nunca Markdown crudo;
- panel o franja de acciones para abrir el flujo asociado: mundos, simulación o
  depuración;
- control para abrir el manual técnico externo cuando el usuario lo solicite.

Los estilos se resuelven desde los mismos tokens de tema existentes. La
ventana actualiza fondos, bordes, texto, selección, enlaces, scrollbars y
estados semánticos cuando se alterna claro/oscuro.

## Ayuda contextual y recuperación

Las superficies de alto riesgo incorporan una ayuda breve con acceso a la guía
completa: ejecución, detener/reiniciar, tiempo máximo, ubicación del robot,
haces, fidelidad, trazas, breakpoints, telemetría, validación y guardado de
mundos. Los errores de script, mundo o sesión muestran un enlace o comando
**Cómo solucionarlo** hacia la entrada contextual correspondiente.

## Compatibilidad y medición

El manual Markdown continúa como documento de operación y referencia técnica,
pero el contenido de usuario se genera desde el catálogo común. Las pruebas
validan que no haya capacidades anunciadas sin destino soportado, que los
identificadores sean equivalentes en ambas interfaces y que cada enlace de
acción lleve al flujo correcto.
