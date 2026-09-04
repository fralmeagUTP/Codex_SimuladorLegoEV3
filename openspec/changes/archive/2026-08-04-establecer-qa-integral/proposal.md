# Propuesta: establecer QA integral y compuerta de calidad

## Motivo

El simulador dispone de pruebas unitarias, de integración y algunas pruebas de
interfaz, pero no existe un contrato único que obligue a planificar, ejecutar y
reportar de manera trazable todas las dimensiones de calidad. La campaña real
de Tkinter del 2026-07-28 demostró además que una prueba automatizada no basta
para acreditar que una interacción visual funciona: los estados terminales y
los diálogos deben comprobarse desde una sesión gráfica real.

## Cambio propuesto

Establecer un programa de aseguramiento de calidad para Web y Tkinter que:

- mantenga inventario funcional, matriz de riesgos y trazabilidad requisito →
  caso → automatización → evidencia;
- cubra pruebas unitarias, integración, contratos, API, UI, E2E, regresión,
  accesibilidad, compatibilidad, seguridad, rendimiento, carga, resiliencia,
  instalación/despliegue y recuperación ante fallos;
- exija evidencia visual y de consola/red para cada flujo crítico ejercitado
  realmente en navegador o escritorio;
- defina casos de regresión para los defectos confirmados y evite marcar como
  `PASS` una capacidad no ejecutada;
- incorpore criterios de calidad y decisión de liberación reproducibles.

## Fuera de alcance

- Cambiar reglas de negocio o reescribir el motor solo para facilitar pruebas.
- Declarar conformidad completa con el hardware Pybricks físico.
- Usar datos reales, secretos, servicios de producción o pruebas destructivas.

## Impacto

- Se añadirán documentación de calidad, fixtures/datos sintéticos y pruebas
  automatizadas por capa cuando la cobertura indique una brecha real.
- Se actualizarán CI y guías de ejecución para distinguir suites rápidas,
  completas, visuales, E2E y no funcionales.
- Las interfaces Web y Tkinter compartirán catálogo de casos de uso y criterios
  de paridad funcional donde corresponda.
