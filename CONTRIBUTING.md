# Contribuir al Simulador EV3 Pybricks

## Antes de abrir un cambio

1. Crear o actualizar el cambio OpenSpec con propuesta, diseno, tareas y deltas.
2. Mantener Web y Tkinter equivalentes para toda capacidad de simulacion nueva.
3. Añadir o actualizar pruebas unitarias, contrato, UI o E2E segun el riesgo.
4. No incluir secretos, datos personales, trazas privadas ni mundos de terceros.

## Checklist de documentacion

- Actualizar `README.md` si cambian instalacion, comandos, interfaces o version.
- Actualizar el manual, arquitectura, seguridad, configuracion o guias de
  despliegue que el cambio afecte.
- Registrar resultados de prueba con fecha, entorno y comando; no reemplazar
  evidencia historica por cifras nuevas sin fecha.
- Actualizar `Documentos/INDICE_DOCUMENTACION.md` para documentos nuevos,
  reubicados u obsoletos.
- Ejecutar las pruebas documentales y `git diff --check` antes de cerrar tareas.

## Verificacion minima

```powershell
py -3.12 -m pytest -q
py -3.12 -m ruff check simulador_ev3 tests
py -3.12 -m mypy
```

Consultar `docs/testing/estrategia_pruebas.md` para E2E, cobertura, seguridad y carga.
