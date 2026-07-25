# Propuesta: madurar calidad y experiencia de aula

## Motivo

El simulador cuenta con arquitectura aislada, contrato de sesion comun y una
suite de regresion amplia. El siguiente incremento debe convertir esas bases en
garantias de producto: paridad verificable tambien en editor de mundos y ayuda,
pruebas reales de escritorio, regresion visual, mayor compatibilidad Pybricks y
flujos docentes reutilizables.

## Cambio propuesto

- Auditar y cerrar el catalogo de casos de uso de mundos y ayuda para Web y
  Tkinter.
- Incorporar automatizacion de escritorio y comparacion visual reproducible en
  CI, con una revision humana cuando la diferencia sea intencional.
- Extender de forma incremental la API Pybricks avanzada y su matriz de
  conformidad, sin declarar soporte total del hardware real.
- Crear biblioteca versionada de misiones, resultados exportables y criterios
  evaluables para aula local.
- Actualizar evidencia, roadmap y guias para que reflejen la version y la
  suite de pruebas realmente vigentes.

## Fuera de alcance

- Autenticacion institucional, LMS o acceso publico a Internet. Se documentaran
  puntos de extension, pero la aplicacion seguira orientada a aula local.
- Reescribir Tkinter, migrar de framework o sustituir el motor 2D.
- Afirmar equivalencia fisica absoluta con un robot EV3 real.

## Impacto

Se afectan el catalogo OpenSpec, interfaces Web/Tkinter, capturadores visuales,
CI, API virtual Pybricks, ejemplos/misiones y documentacion. Se mantienen los
contratos de sesion y los mundos JSON existentes.

## Criterios de exito

- Todos los casos de uso compartidos, incluidos mundos y ayuda, tienen estado
  auditado, evidencia y prueba automatizada o una limitacion documentada.
- CI detecta regresiones funcionales de escritorio y diferencias visuales no
  aprobadas en los viewports de referencia.
- Cada metodo Pybricks nuevo tiene estado de conformidad y pruebas de limites,
  error y comportamiento nominal.
- Una mision puede distribuirse, ejecutarse, calificarse y exportarse sin datos
  reales ni dependencia de un servicio externo.
- El roadmap, version, comandos y resultados de calidad no contienen cifras
  historicas presentadas como estado actual.
