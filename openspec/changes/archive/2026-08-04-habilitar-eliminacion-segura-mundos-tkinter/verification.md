# Verificación

## Cobertura automatizada

- `tests/ui/test_world_editor_navigation.py`: confirma eliminación de un mundo
  temporal autorizado, reinicio del editor, protección de preestablecidos y
  rechazo de rutas externas.
- `tests/web/test_world_deletion_api.py`: confirma la eliminación autorizada
  por sesión en Web y el bloqueo de un mundo incluido.

## Evidencia interactiva

En sesión Windows visible se ejecutó un ciclo aislado con un directorio
temporal: guardar, abrir, editar, eliminar y volver a un mundo nuevo. La
captura del editor muestra el control **Eliminar archivo** habilitado para un
mundo editable.

## Comandos ejecutados

```text
.\.venv\Scripts\python.exe -m pytest tests\ui\test_world_editor_navigation.py -q
.\.venv\Scripts\python.exe -m pytest tests\web\test_world_deletion_api.py -q
.\.venv\Scripts\ruff.exe check simulador_ev3\ui\world_editor_window.py tests\ui\test_world_editor_navigation.py
.\.venv\Scripts\mypy.exe simulador_ev3\ui\world_editor_window.py
node --check simulador_ev3\web\static\js\world_editor_app.js
```

Todos los comandos anteriores finalizaron correctamente.
