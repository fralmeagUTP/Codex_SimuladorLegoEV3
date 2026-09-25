# Propuesta: rediseñar el centro de ayuda orientado al usuario

## Motivo

La ayuda actual contiene información útil y tres tutoriales compartidos, pero
la experiencia no es suficientemente guiada ni visual. La Web combina tarjetas
de tutorial con secciones extensas de texto y la aplicación Tkinter presenta el
manual como texto Markdown de lectura lineal. Esto aumenta la carga cognitiva,
mezcla instrucciones para estudiantes, docentes y personal técnico, y obliga a
buscar manualmente la solución ante dudas o errores.

También hay inconsistencias editoriales: se alternan los nombres **BotLab
Studio** y **Simulador EV3 Pybricks**, y se muestran URLs fijas que no siempre
corresponden a la instancia que el usuario está utilizando.

## Cambio propuesto

Crear un Centro de ayuda común, centrado en tareas, que mantenga la paridad
funcional entre Web y Tkinter y permita a una persona aprender sin depender de
un instructor. El cambio:

- establece una única identidad visible: **Simulador EV3 Pybricks**;
- organiza el contenido por tareas y perfiles: empezar, simular, crear mundos,
  programar, depurar, enseñar y resolver problemas;
- presenta rutas de aprendizaje breves, imágenes anotadas, resultados
  esperados y recuperación ante fallos;
- reemplaza la lectura de Markdown plano de Tkinter por una ventana navegable
  con índice, contenido estructurado y acciones directas;
- mejora la página Web con búsqueda, navegación por secciones, enlaces internos
  y tarjetas de aprendizaje, sin perder su comportamiento responsivo;
- añade ayuda contextual y enlaces de recuperación desde controles y mensajes
  de error de alto impacto;
- conserva un único catálogo de contenidos, de modo que Web y Tkinter no
  diverjan en instrucciones, terminología o capacidades anunciadas.

## Fuera de alcance

- Cambiar la semántica del motor, del runtime o de las APIs Pybricks.
- Crear contenido que anuncie funciones no disponibles.
- Sustituir toda la documentación técnica de operación o despliegue; esta se
  enlazará desde el área destinada a personal técnico.

## Impacto

- Se introducirán modelos de contenido y recursos didácticos compartidos.
- Se actualizarán la plantilla Web, la ventana de ayuda de Tkinter, el manual
  de usuario y la documentación de diferencias de interfaz cuando corresponda.
- Se añadirán pruebas de navegación, búsqueda, tema, teclado, enlaces de
  recuperación y paridad de contenido.
