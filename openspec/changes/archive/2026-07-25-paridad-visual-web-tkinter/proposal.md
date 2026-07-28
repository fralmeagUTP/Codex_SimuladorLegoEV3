# Propuesta: paridad visual Web–Tkinter

## Motivo

Web y Tkinter comparten funciones pero difieren en paleta, disposición, tamaños, etiquetas y estados. Esto aumenta la carga cognitiva en aula.

## Cambio propuesto

Tomar la Web como fuente de verdad visual y aplicar su sistema de diseño a Tkinter: controles, colores, tipografía, espaciado, iconos, estados, mensajes y accesibilidad. No cambia el contrato de sesión ni las reglas de simulación.

## Impacto

Se afectan `simulador_ev3/ui/`, `shared/ui_settings.py`, documentación y pruebas UI. Tkinter conserva capacidades locales, pero no puede divergir visualmente sin un nuevo delta OpenSpec.
