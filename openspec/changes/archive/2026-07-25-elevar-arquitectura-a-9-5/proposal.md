# Propuesta: elevar arquitectura a 9.5

## Motivo

El simulador ya dispone de paridad funcional y worker aislado, pero necesita
consolidar un contrato de sesión único, modernizar ambas interfaces y operar de
forma reproducible en aula local y servidor Linux.

## Cambio propuesto

- Hacer del worker aislado la ruta predeterminada de ejecución.
- Publicar contratos versionados compartidos por Web y Tkinter.
- Separar responsabilidades de UI, runtime, mundos y observabilidad.
- Añadir métricas Prometheus, trazas OpenTelemetry, contenedor Linux y CI E2E.

## Impacto

Se preserva la compatibilidad Pybricks y los contratos HTTP existentes. El modo
de ejecución local queda disponible únicamente como compatibilidad explícita
para desarrollo y pruebas.
