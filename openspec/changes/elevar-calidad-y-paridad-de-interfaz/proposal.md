# Propuesta: elevar calidad, seguridad y paridad de interfaces

## Resumen

Evolucionar el Simulador EV3 Pybricks desde su estado actual hacia una plataforma
educativa más segura, medible y mantenible. La evolución incluye aislamiento de
scripts, fidelidad creciente del modelo EV3, máquina de estados explícita,
observabilidad, calidad continua y una política obligatoria de paridad entre la
aplicación web y la aplicación Tkinter.

## Problema

El núcleo de simulación es reutilizable y cuenta con amplia cobertura de pruebas,
pero existen riesgos y divergencias que limitan la calidad del producto:

- los scripts de usuario se ejecutan mediante `exec` en el proceso de la app;
- el timeout web puede quedar sin límite por configuración;
- el auto-reinicio puede borrar el estado final antes de que una UI lo muestre;
- web y Tkinter tienen políticas de evolución diferentes y pueden divergir;
- la fidelidad de sensores, física y algunos métodos Pybricks es aproximada;
- el frontend web y servicios de aplicación concentran responsabilidades;
- no hay métricas, pruebas de carga, matriz de conformidad Pybricks ni quality
  gates estáticos obligatorios;
- la documentación de versión y compatibilidad puede divergir del código.

## Objetivos

1. Garantizar que Web y Tkinter proporcionen exactamente los mismos casos de
   uso, controles, resultados y mensajes funcionales.
2. Aislar la ejecución de scripts no confiables fuera del proceso de la UI/API.
3. Definir una máquina de estados única y observable para toda sesión.
4. Aumentar la fidelidad EV3 de forma configurable, sin perder el modo educativo
   determinista actual.
5. Convertir requisitos de calidad, seguridad, rendimiento y compatibilidad en
   controles verificables por CI.
6. Incorporar trazas, reproducción y escenarios evaluables para uso docente.

## Fuera de alcance

- Reescribir por completo el motor 2D como un motor de física 3D.
- Prometer compatibilidad total con cada versión de Pybricks o hardware EV3.
- Eliminar Tkinter; por esta propuesta ambas interfaces pasan a ser productos
  funcionalmente equivalentes.
- Añadir autenticación institucional o un LMS específico; se conservarán puntos
  de extensión para estas integraciones.

## Impacto

- Afecta runtime, core, API Pybricks, application, web, UI Tkinter, pruebas,
  configuración, empaquetado, documentación y CI.
- Introduce contratos compartidos de interfaz y snapshots versionados.
- Requiere migración incremental, manteniendo los ejemplos y mundos existentes.

## Criterios de éxito

- Cada caso de uso funcional se ejecuta y verifica en web y Tkinter con el mismo
  resultado observable.
- El proceso principal puede terminar una ejecución de usuario sin depender de
  detener un hilo Python cooperativo.
- El estado final de una ejecución permanece visible hasta la confirmación del
  usuario o una transición explícita de reinicio.
- CI aprueba pruebas unitarias, integración, contratos, E2E de ambas UI, análisis
  estático, cobertura, seguridad y pruebas de carga acordadas.
- La matriz de compatibilidad Pybricks indica con precisión si una capacidad es
  completa, aproximada, parcial o no soportada.
