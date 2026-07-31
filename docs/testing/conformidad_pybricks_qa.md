# Conformidad Pybricks verificada por QA

La matriz contractual vigente está en
`openspec/changes/archive/2026-07-25-elevar-calidad-y-paridad-de-interfaz/pybricks-conformance-v1.md`.
Esta hoja vincula su cobertura con pruebas ejecutables y evidencia de interfaz.

| Área | Cobertura automatizada | Evidencia UI real | Estado |
|---|---|---|---|
| Motores A–D | `TestMotorAPI`, dominio y runtime | campaña Tkinter: `motor_a_real.png`, `motores_abcd_real.png` | Cubierto |
| `DriveBase` | `TestDriveBaseAPI`, core y runtime | campaña Tkinter: `drivebase_real.png` | Cubierto |
| Sensor táctil / ultrasónico | `TestSensorAPI`, dominio | campaña Tkinter: `sensores_s1_s4_real.png` | Cubierto |
| LCD soportada | `print`, `clear`, `draw_pixel`, `draw_line`, `draw_circle`, `draw_box` en `TestEV3BrickAPI` | `ejecucion_exitosa_pyautogui.png` | Cubierto |
| Temporizadores y espera | `TestWait`, `TestStopWatch`, runtime | scripts de espera y pausa Tkinter | Cubierto |
| Errores, puerto e importación | runtime, sandbox y API | error de sintaxis Tkinter | Cubierto parcialmente |
| `Screen.draw_text` | No está en matriz ni en `_Screen` | TK-2026-07-28-002 | **No soportado declarado** |

Una API ausente de la matriz no se debe presentar como compatible. Si se añade
`Screen.draw_text`, deberá cambiar esta clasificación, añadir prueba de API,
snapshot de LCD y recorrido visible Web/Tkinter.
