# Diseno: calidad verificable y experiencia de aula

## Estrategia de paridad

El catalogo `interface-parity-v1` seguira siendo la fuente de verdad. Cada caso
de uso tendra una de tres resoluciones: `verificado`, `limitacion_documentada`
o `no_soportado`. Ningun caso permanecera ambiguamente como pendiente. La
paridad se validara contra el contrato de sesion compartido, no mediante acceso
directo al motor desde una interfaz.

## Pruebas de escritorio y regresion visual

Las pruebas de Tkinter se dividiran en contrato/UI sin pantalla y recorridos
graficos Windows en un entorno dedicado. Los recorridos automatizaran teclado,
menus, dialogos no destructivos, ejecucion, mundo y depuracion. La comparacion
visual usara capturas de Web y Tkinter en resoluciones versionadas, mascara para
zonas nativas permitidas y umbrales por region. Una diferencia solo se acepta
actualizando la referencia, la matriz y su motivo.

## Compatibilidad Pybricks

Cada ampliacion se implementara en dominio, API virtual, matriz de conformidad
y pruebas. Se priorizan `Motor.run_target`, `Motor.run_until_stalled`, curvas
de `DriveBase`, `ColorSensor.hsv` y colores detectables. La fidelidad se
declarara como completa, aproximada, parcial o no soportada; los perfiles de
simulacion conservan comportamiento determinista reproducible.

## Flujo docente

Una mision sera un recurso JSON versionado que contiene objetivo, mundo,
script inicial, pruebas de aceptacion, rubrica y metadatos. El resultado se
generara con datos sinteticos locales: version de mision, resultado de pruebas,
traza, perfil y fecha. La exportacion JSON/CSV sera portable y no incluira
credenciales ni identificadores personales por defecto.

## Actualizacion documental

Un unico generador o prueba de consistencia comprobara que README, roadmap,
version, comandos y conteos de calidad se identifican como actuales o como
historicos fechados. La evidencia no reemplaza la ejecucion de CI, pero debe
referenciar el comando reproducible y su fecha.
