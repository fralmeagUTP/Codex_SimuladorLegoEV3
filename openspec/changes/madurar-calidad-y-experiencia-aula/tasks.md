# Tareas: madurar calidad y experiencia de aula

## Fase 1 - Paridad completa y documentacion fiable

- [ ] 1.1 Auditar UC-WORLD-01, UC-WORLD-02, UC-WORLD-03 y UC-HELP-01 en Web y Tkinter.
- [ ] 1.2 Completar funciones faltantes o registrar limitaciones explicitamente aceptadas.
- [ ] 1.3 Añadir pruebas de contrato y matriz de trazabilidad para esos casos de uso.
- [ ] 1.4 Corregir roadmap, manuales y checklist para separar evidencia historica de estado actual.
- [ ] 1.5 Añadir una prueba que detecte version, comandos o resultados de calidad obsoletos.

## Fase 2 - Automatizacion de escritorio y regresion visual

- [ ] 2.1 Seleccionar y documentar el driver grafico Windows compatible con Tkinter y CI.
- [ ] 2.2 Implementar recorridos de escritorio para menus, teclado, ejecucion, pausa, mundo, depuracion y recuperacion.
- [ ] 2.3 Definir regiones, mascaras nativas y umbrales de comparacion visual Web/Tkinter.
- [ ] 2.4 Ejecutar capturas y comparacion visual en CI; adjuntar artefactos ante fallo.
- [ ] 2.5 Mantener aprobacion explicita de referencias visuales y evidencia reproducible.

## Fase 3 - Conformidad Pybricks avanzada

- [ ] 3.1 Especificar semantica y limites de `Motor.run_target` y `Motor.run_until_stalled`.
- [ ] 3.2 Implementar y probar ambos metodos en todos los perfiles de simulacion aplicables.
- [ ] 3.3 Especificar e implementar curvas de `DriveBase` con comportamiento declarado.
- [ ] 3.4 Añadir `ColorSensor.hsv` y configuracion de colores detectables con pruebas de borde.
- [ ] 3.5 Actualizar matriz de conformidad y diferencias simulador-robot por cada metodo.

## Fase 4 - Experiencia docente local

- [ ] 4.1 Definir esquema versionado de mision, rubrica y resultado sin datos personales.
- [ ] 4.2 Implementar catalogo de misiones y carga equivalente en Web y Tkinter.
- [ ] 4.3 Ejecutar pruebas de aceptacion de una mision contra una traza determinista.
- [ ] 4.4 Exportar resultado local JSON/CSV y validar su portabilidad.
- [ ] 4.5 Documentar flujo docente, limites del simulador y politica de privacidad local.

## Criterios de cierre

- Todas las tareas incluyen pruebas y evidencia enlazada.
- Ninguna diferencia Web/Tkinter queda sin clasificar en la matriz de paridad.
- La cobertura y quality gates existentes se mantienen o aumentan.
- La propuesta se archiva solo con CI verde en Windows y Linux cuando aplique.
