## ADDED Requirements

### Requirement: categorías comunes y sin duplicidad

Ambas aplicaciones MUST presentar Archivo, Aprender, Mundos, Prácticas guiadas, Misiones, Configuración, Diagnóstico y Ayuda, en ese orden lógico o una adaptación visual equivalente para el espacio disponible. Una acción MUST tener una sola categoría principal y la interfaz NO DEBE conservar rótulos anteriores como rutas principales redundantes.

#### Scenario: usuario cambia de producto

- **Dado** que una acción existe en Web y escritorio,
- **cuando** el usuario la busque en cualquiera de los productos,
- **entonces** deberá encontrarla bajo la misma categoría y una etiqueta equivalente.

#### Scenario: migración de categorías anteriores

- **Dado** que el usuario conoce Ejemplos, Escenarios, Tema, Fidelidad, Tiempo máximo o Trazas,
- **cuando** use la versión actualizada,
- **entonces** encontrará la función en Aprender, Prácticas guiadas, Configuración o Diagnóstico según la matriz documentada,
- **y** no verá ambos nombres como rutas principales para la misma responsabilidad.

### Requirement: intención didáctica diferenciada

La aplicación MUST diferenciar Aprender, Prácticas guiadas y Misiones con una descripción visible y accesible de su propósito. Aprender permite explorar código; Prácticas guiadas carga una actividad preparada; Misiones presenta un reto evaluable.

#### Scenario: seleccionar una práctica guiada

- **Dado** que el usuario abre Prácticas guiadas,
- **cuando** seleccione una actividad,
- **entonces** verá objetivo, mundo y programa antes de confirmar,
- **y** al cancelar conservará programa y mundo anteriores.

#### Scenario: explorar una misión

- **Dado** que el usuario abre Misiones,
- **cuando** consulte una misión,
- **entonces** podrá identificar propósito, requisitos, progreso y resultado disponible sin confundirla con un ejemplo libre.

### Requirement: carga confiable y recuperación

La aplicación MUST actualizar de forma verificable editor y mundo al cargar un ejemplo, mundo, práctica o misión. MUST advertir antes de sustituir trabajo sin guardar y preservar el estado previo si una carga, recuperación o reintento falla.

#### Scenario: sesión expirada durante la carga

- **Dado** que la sesión vence durante una solicitud de carga,
- **cuando** el usuario elija contenido,
- **entonces** la aplicación NO mostrará éxito ni dejará controles en estado ambiguo,
- **y** explicará la recuperación disponible y preservará el contenido previo.

#### Scenario: sustitución con cambios sin guardar

- **Dado** que el programa actual contiene cambios sin guardar,
- **cuando** una carga vaya a sustituir programa, mundo o misión,
- **entonces** la aplicación advertirá antes de sustituirlo,
- **y** conservará el estado previo si la operación falla.

### Requirement: opciones técnicas explicadas

Configuración y Diagnóstico MUST indicar valor actual, propósito e impacto de cada ajuste técnico antes de permitir su modificación o exportación.

#### Scenario: usuario consulta un ajuste técnico

- **Dado** que el usuario abre Configuración o Diagnóstico,
- **cuando** revise una preferencia o herramienta,
- **entonces** verá su valor o estado actual, para qué sirve y el efecto esperado antes de modificarlo o exportarlo.

### Requirement: accesibilidad, estado coherente y diagnóstico seguro

Ambas aplicaciones MUST comunicar por teclado y tecnologías de asistencia el nombre de cada categoría, su descripción y si una acción está temporalmente no disponible. Los mensajes y exportaciones de diagnóstico NO DEBEN exponer secretos, tokens, cabeceras, rutas privadas ni trazas internas de servidor.

#### Scenario: simulación en ejecución

- **Dado** que hay simulación o depuración activa,
- **cuando** una opción no pueda modificar el estado de forma segura,
- **entonces** quedará inhabilitada de forma coherente en ambos productos,
- **y** conservará una explicación de su estado y de cómo volver a habilitarla.

#### Scenario: error de carga

- **Dado** que falla una carga o recuperación de sesión,
- **cuando** se informe el error,
- **entonces** el mensaje describirá una acción de recuperación sin revelar detalles sensibles,
- **y** la evidencia técnica incluirá únicamente datos sanitizados.
