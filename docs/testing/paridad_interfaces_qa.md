# Paridad funcional Web y Tkinter

| Caso de uso compartido | Contrato / automatización | Estado |
|---|---|---|
| Ejecutar y finalizar script | `test_web_and_desktop_finish_same_program_with_equivalent_snapshot` | Cubierto |
| Pausar y reanudar | `test_web_and_desktop_pause_resume_before_finishing` | Cubierto |
| Perfil de simulación | `test_web_and_desktop_apply_the_same_simulation_profile` | Cubierto |
| Trazas y depuración | `test_web_and_desktop_export_equivalent_trace_contract`, configuración de debug | Cubierto |
| Colocar assets en editor | `test_web_and_desktop_world_editors_place_equivalent_asset` | Cubierto |
| Estado terminal de error | `QA-REG-001`, adaptador y UI Tkinter | Cubierto por contrato; UI Web requiere campaña visible vigente |
| Aviso de ejecución exitosa | pruebas UI/Tkinter y Web | Cubierto por plataforma |

## Diferencias justificadas

- Web usa notificación toast accesible y no modal; Tkinter usa `messagebox`
  nativo. Ambas comunican el mismo mensaje y solo para `finished`.
- Web se prueba también a 390×844; Tkinter se ajusta a tamaños de escritorio y
  diálogos del sistema operativo.
- La apariencia exacta depende de los controles nativos Tk, pero los casos de
  uso, estados terminales, datos de telemetría y controles de simulación deben
  conservar la misma semántica.

Una diferencia no presente en esta tabla requiere requisito, prueba y decisión
explícita antes de ser aceptada como divergencia de plataforma.
