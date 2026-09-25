# Tareas: validar sesiones concurrentes locales

## Fase 1 — Preparación y contrato

- [x] 1.1 Inventariar límites, endpoints, métricas y mecanismos de cierre de sesión.
- [x] 1.2 Definir perfiles de carga moderada, capacidad excedida y aislamiento.
- [x] 1.3 Documentar límites de interpretación para Nyquist y producción.

## Fase 2 — Ejecutor HTTP reproducible

- [x] 2.1 Implementar un servidor temporal y clientes HTTP concurrentes sin estado compartido.
- [x] 2.2 Verificar alta, tokens únicos, carga de script, lectura autorizada y acceso cruzado prohibido.
- [x] 2.3 Verificar `429`, métricas y cierre de todos los recursos creados.
- [x] 2.4 Guardar evidencia JSON y resumen Markdown de cada campaña.

## Fase 3 — Calidad y liberación

- [x] 3.1 Ejecutar carga moderada y prueba de límite en Windows local.
- [x] 3.2 Ejecutar pruebas unitarias, de carga y análisis estático relacionados.
- [x] 3.3 Actualizar la guía de despliegue Nyquist con configuración recomendada y criterios de salida.
- [x] 3.4 Registrar resultados, riesgos y capacidad pendiente de medir en el servidor final.
