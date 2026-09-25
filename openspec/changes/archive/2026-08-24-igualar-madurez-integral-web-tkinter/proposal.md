## Why

Web y Tkinter comparten el motor, el contrato de sesión y el catálogo
educativo principal, pero no cuentan aún con una definición única de madurez
que los obligue a evolucionar al mismo nivel en arquitectura, experiencia,
pedagogía, ayuda, calidad y observabilidad. La paridad funcional actual no es
suficiente si una interfaz tiene mejor capacidad de operación, evaluación
didáctica, accesibilidad, diagnóstico o evidencia de calidad.

## What Changes

- Establecer un Modelo de Madurez de Interfaz (MMI) común y verificable para
  Web y Tkinter, con criterios, métricas y evidencia por dimensión.
- Convertir ambas UI en adaptadores equivalentes de los mismos puertos de
  sesión, presentación, ayuda, pedagogía y observabilidad.
- Unificar el sistema de diseño, los estados, la navegación, la accesibilidad y
  el contenido de ayuda, respetando las diferencias inevitables de navegador y
  controles nativos.
- Consolidar un catálogo único, versionado y verificable de imágenes, figuras,
  sprites, texturas e iconos para que Web y Tkinter rendericen los mismos
  recursos visuales, sin que el escritorio quede como fuente informal de
  assets más recientes.
- Crear una experiencia pedagógica común: objetivos, prerrequisitos, prácticas,
  retroalimentación, errores recuperables y progreso local por actividad.
- Exigir una misma compuerta de calidad, trazabilidad y evidencia real de UI
  para los casos aplicables de ambas plataformas.
- Exponer un diagnóstico equivalente de ejecución en escritorio y Web; los
  formatos pueden variar, pero los datos y correlaciones deben ser los mismos.

## Capabilities

### New Capabilities

- `educational-experience`: contrato común para rutas de aprendizaje,
  objetivos, retroalimentación y accesibilidad pedagógica.

### Modified Capabilities

- `interface-parity`: amplía la paridad desde casos de uso a madurez integral y
  evita que una interfaz avance sin una adaptación verificable en la otra.
- `user-interfaces`: exige sistema de diseño, navegación, ayuda contextual y
  estados accesibles equivalentes.
- `quality-assurance`: exige compuerta gemela de pruebas, cobertura por
  plataforma, regresiones cruzadas y evidencia de interfaz real.
- `observability`: define una vista diagnóstica común correlacionada para Web y
  escritorio.
- `project-documentation`: exige documentación y manuales equivalentes por
  capacidad, plataforma y nivel de audiencia.

## Impact

Se verán afectados los controladores Web, presentadores/adaptadores Tkinter,
contratos compartidos, catálogos de ayuda y pedagogía, temas, pruebas
Playwright/Pywinauto/Pytest, CI, métricas, trazas y documentación. No se
cambiará la semántica educativa de Pybricks ni el modelo físico salvo para
corregir una divergencia confirmada.
