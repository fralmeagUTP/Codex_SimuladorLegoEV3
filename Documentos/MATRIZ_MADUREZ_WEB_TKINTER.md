# Matriz MMI: madurez integral Web y Tkinter

Versión de manifiesto: `1`
Estado: **línea base de gobierno**; una fila solo puede pasar a `Cerrada` con
los enlaces de evidencia automatizada y manual de las dos interfaces.

## Línea base reproducible

Ejecute desde el commit a evaluar:

```powershell
.\.venv\Scripts\python.exe scripts\generate_mmi_baseline.py `
  --output artifacts\mmi\baseline.json --browser "Chrome <versión>"
```

El archivo registra commit, Windows/Linux, Python, navegador, resoluciones
`1920x1080`, `1280x800`, `1024x768`, `390x844` y temas claro/oscuro. La
evidencia manual se guarda bajo `Documentos/EVIDENCIA_MMI_<fecha>/web` y
`Documentos/EVIDENCIA_MMI_<fecha>/tkinter`.

## Inventario y compuerta de cierre

| Caso | Clasificación | Web automatizada | Web manual | Tkinter automatizada | Tkinter manual | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| UC-SESSION-01 | Equivalente | requerida | requerida | requerida | requerida | Abierta |
| UC-CODE-01 | Equivalente | requerida | requerida | requerida | requerida | Abierta |
| UC-RUN-01 | Equivalente | requerida | requerida | requerida | requerida | Abierta |
| UC-RUN-02 | Equivalente | requerida | requerida | requerida | requerida | Abierta |
| UC-DEBUG-01 | Equivalente | requerida | requerida | requerida | requerida | Abierta |
| UC-ROBOT-01 | Equivalente | requerida | requerida | requerida | requerida | Abierta |
| UC-OBSERVE-01 | Equivalente | requerida | requerida | requerida | requerida | Abierta |
| UC-EXAMPLE-01 | Equivalente | requerida | requerida | requerida | requerida | Abierta |
| UC-WORLD-01 | Equivalente | requerida | requerida | requerida | requerida | Abierta |
| UC-WORLD-02 | Equivalente | requerida | requerida | requerida | requerida | Abierta |
| UC-WORLD-03 | Equivalente | requerida | requerida | requerida | requerida | Abierta |
| UC-HELP-01 | Equivalente | requerida | requerida | requerida | requerida | Abierta |
| UC-TRACE-01 | Equivalente | requerida | requerida | requerida | requerida | Abierta |
| UC-PROFILE-01 | Equivalente | requerida | requerida | requerida | requerida | Abierta |
| UC-ASSESS-01 | Brecha planificada | requerida | requerida | requerida | requerida | Abierta |

Las diferencias de navegador móvil, instalación Windows y transporte/persistencia
se registran como **Adaptación**, con evidencia equivalente, nunca como una
exclusión de la paridad funcional.

## Inventario de recursos visuales

`simulador_ev3.shared.asset_catalog.AssetCatalog` es la fuente canónica de los
asset_id de escenario, editor, introducción y marcas. La Web recibe el mismo
manifiesto mediante `/api/editor/assets` y la plantilla de simulación; Tkinter
lo resuelve con `resolve_image_assets_dir()`. Las pruebas verifican presencia y
hash de todos los archivos canónicos antes de empaquetar.
