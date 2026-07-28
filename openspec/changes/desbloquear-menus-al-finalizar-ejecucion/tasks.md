# Tareas

## 1. Reproducción y contrato

- [x] 1.1 Documentar la matriz de estados y el conjunto de menús afectados para Web y Tkinter.
- [x] 1.2 Añadir casos de regresión que reproduzcan el bloqueo tras una finalización natural.

## 2. Implementación Web

- [x] 2.1 Extraer una predicación única de ejecución activa en `simulation_app.js`.
- [x] 2.2 Actualizar la disponibilidad de botones y submenús desde esa predicación.
- [x] 2.3 Verificar que los estados terminales se derivan como desbloqueados y que `finished` reactiva los menús en navegador real.

## 3. Implementación Tkinter

- [x] 3.1 Sustituir la política actual de `_on_status` por la matriz de estados definida.
- [x] 3.2 Mantener la actualización de los menús registrados en el hilo de interfaz mediante `after_idle`.
- [x] 3.3 Comprobar mediante regresión que los estados terminales y el reinicio reactivan los menús.

## 4. Verificación

- [x] 4.1 Ejecutar pruebas unitarias e integración de las transiciones de estado en ambas interfaces.
- [x] 4.2 Ejecutar una prueba Web en navegador: bloquear durante ejecución, habilitar al terminar naturalmente y habilitar tras detener y reiniciar.
- [ ] 4.3 Ejecutar una verificación manual Tkinter para los mismos tres flujos.
- [x] 4.4 Ejecutar análisis estático y registrar los resultados en la evidencia del cambio.
