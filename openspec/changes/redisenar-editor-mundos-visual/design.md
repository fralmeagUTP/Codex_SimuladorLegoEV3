# Diseño

## Principios

El editor conserva el lienzo como superficie de trabajo dominante, pero separa
las decisiones de archivo, edición y simulación. La interfaz presenta términos
del dominio educativo; los identificadores internos y píxeles quedan limitados
a depuración y serialización.

## Estructura

La ventana se compone de cuatro regiones estables:

1. Cabecera: grupos Archivo, Edición y Simulación.
2. Biblioteca izquierda: búsqueda, categorías y assets.
3. Lienzo central: nombre del mundo, controles de vista, cuadrícula y guía
   cuando no hay elementos.
4. Inspector derecho: propiedades del elemento seleccionado y acciones
   contextuales.
5. Barra inferior: dimensiones, cursor, snap y resultado de validación.

En áreas estrechas, biblioteca e inspector pueden contraerse o mostrarse como
paneles desplegables; el lienzo y sus controles no deben crear desplazamiento
horizontal global.

## Biblioteca e inspector

Los assets se agrupan en Robot, Obstáculos, Suelos, Líneas, Zonas y metas, y
Sensores. Cada tarjeta tiene previsualización, nombre, tooltip y nombre
accesible. El filtro de búsqueda opera por nombre y categoría.

El inspector adapta los campos al tipo de objeto. Expone posición en celdas o
centímetros y orientación en grados. El adaptador de presentación convierte
estos valores a las unidades internas sin cambiar el JSON existente. Sin
selección, el inspector explica la siguiente acción y no muestra campos
inactivos.

## Capas y acciones

La lista de capas consume la colección actual de objetos; seleccionar una fila
selecciona el objeto en el lienzo y viceversa. Visibilidad, bloqueo y orden se
reflejan en el renderizado sin cambiar la semántica física del mundo.

Eliminar existe solo como acción contextual sobre la selección. La eliminación
simple de un objeto no requiere confirmación; la eliminación de múltiples
objetos o de un archivo de mundo utiliza el mecanismo seguro ya definido.

## Compatibilidad

Las capas, favoritos, recientes y preferencias de presentación no forman parte
del modelo físico de mundo salvo que una capacidad existente ya las persista.
La carga y guardado de JSON siguen usando el modelo actual. La conversión de
mundo de editor a mundo físico no cambia.

## Paridad

Web y Tkinter comparten acciones, categorías, nombres de propiedad, unidades,
validaciones y semántica. Cada plataforma puede adaptar paneles y controles a
sus patrones nativos, sin introducir diferencias en operaciones o resultados.
