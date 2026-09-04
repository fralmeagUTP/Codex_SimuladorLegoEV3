# Diseño: menú principal unificado

## Arquitectura de información

| Categoría | Contenido | Audiencia principal |
|---|---|---|
| Archivo | Nuevo, abrir, guardar y estado de cambios | Todos |
| Aprender | Ejemplos por nivel: iniciar, movimiento, sensores, control y retos | Estudiantes y docentes |
| Mundos | Editor, mundo en blanco, importar y mundos preestablecidos | Todos |
| Prácticas guiadas | Paquetes de objetivo + mundo + programa + pasos | Estudiantes |
| Misiones | Actividades evaluables y su progreso | Estudiantes y docentes |
| Configuración | Tema, fidelidad, tiempo máximo y explicación de impacto | Todos |
| Diagnóstico | Estado de sesión, trazas y exportación de diagnóstico | Soporte y docentes |
| Ayuda | Centro, guía rápida, libro y Acerca de | Todos |

## Reglas de interacción

1. Una acción solo tiene un punto de acceso principal; los atajos contextuales pueden enlazarla sin duplicar su responsabilidad.
2. Las preferencias muestran valor actual, unidad y efecto antes de modificarse.
3. Una práctica guiada muestra una ficha de confirmación con su objetivo, mundo y programa; la carga es atómica o informa el error y conserva el estado previo.
4. Las opciones diagnósticas no se mezclan con material de aprendizaje.
5. Los menús se pueden usar con teclado, lector de pantalla y ventana reducida.

## Compatibilidad y migración

- Se conservarán identificadores de acciones y rutas públicas cuando sea posible.
- Los enlaces antiguos de ayuda redirigirán a la nueva categoría equivalente.
- Las preferencias existentes se migrarán sin cambiar su valor.
- Web y escritorio compartirán un catálogo declarativo de categorías y acciones, adaptable a sus controles nativos.

## Manejo de errores

La carga de ejemplo, mundo, práctica o misión deberá tratar una sesión expirada como fallo recuperable: mostrar un mensaje claro, renovar o solicitar recarga, y nunca declarar éxito mientras el editor o mundo no se haya actualizado.
## Contrato de paridad entre productos

| Aspecto | Contrato Web / escritorio |
|---|---|
| Catálogo | Mismos ocho identificadores, etiquetas, orden y descripciones funcionales. |
| Acciones | Una acción tiene una categoría principal idéntica; pueden diferir los controles nativos, no la intención ni el resultado. |
| Contenido | Ejemplos, mundos, prácticas y misiones resuelven el mismo catálogo distribuido. |
| Estados | Durante ejecución, depuración, error y sesión expirada, ambos explican qué está bloqueado, qué se conserva y cómo continuar. |
| Accesibilidad | Web expone nombre, descripción y estado ARIA; escritorio conserva foco visible, atajos y contraste suficiente. |
| Evidencia | Una prueba contractual compara taxonomía y una matriz manual comprueba flujos equivalentes. |

## Matriz de migración visible

| Nombre anterior | Destino final | Mensaje orientador |
|---|---|---|
| Ejemplos | Aprender | “Explora programas por nivel y tema”. |
| Escenarios | Prácticas guiadas | “Carga una actividad con objetivo, mundo y programa”. |
| Tema | Configuración › Apariencia | “Cambia la apariencia de la aplicación”. |
| Fidelidad | Configuración › Precisión de simulación | “Equilibra precisión y rendimiento”. |
| Tiempo máximo | Configuración › Límite de ejecución | “Evita ejecuciones demasiado largas”. |
| Trazas | Diagnóstico › Trazas de simulación | “Revisa información técnica para soporte”. |
| Diagnóstico de sesión | Diagnóstico › Estado de sesión | “Comprueba la conexión y recupera la sesión si es necesario”. |

Las cargas de contenido tratarán la sesión expirada como fallo recuperable y nunca declararán éxito si editor y mundo no se actualizaron. Los mensajes y exportaciones de diagnóstico no incluirán secretos, tokens, cabeceras, rutas privadas ni trazas internas de servidor.
