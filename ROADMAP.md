# Roadmap — Simulador EV3 Pybricks

Estado actualizado: 2026-08-05
Versión actual: 1.5.0
Repositorio: `fralmeagUTP/Codex_SimuladorLegoEV3`

## Producto consolidado en 1.5.0

- Dominio EV3, motor 2D determinista y hardware virtual.
- API Pybricks educativa, `DriveBase`, motores, sensores y EV3 Brick.
- Ejecución aislada, depuración, cancelación, timeout y recuperación.
- Web Flask multi-sesión y escritorio Tkinter con contrato compartido.
- Editor de mundos Web/Tkinter, escenarios, ejemplos y misiones.
- Telemetría, LCD, trazas, perfiles y resultados de misión.
- Temas, navegación por teclado, diseño adaptable y ayuda contextual.
- Observabilidad, contenedor Linux, paquete Windows y CI multiplataforma.
- Paridad funcional cerrada y liberación 1.5.0 apta con observaciones.

## Principios para próximas iteraciones

1. Mantener Web y Tkinter equivalentes para toda capacidad común.
2. Implementar cambios mediante OpenSpec y pruebas proporcionales al riesgo.
3. No ampliar la superficie Pybricks sin documentar conformidad y diferencias
   frente al hardware real.
4. Conservar el worker aislado como ruta normal y el runtime local solo como
   compatibilidad controlada.
5. Tratar rendimiento, accesibilidad, seguridad y observabilidad como criterios
   de aceptación, no como trabajo posterior.

## Próximas líneas de trabajo

### Prioridad alta

- Completar una política de autenticación y autorización antes de exponer el
  servicio fuera de un aula o red controlada.
- Definir SLO operativos de latencia, capacidad y recuperación con campañas de
  carga sostenida sobre infraestructura objetivo.
- Ampliar pruebas de mutación a escenarios críticos del motor y API Pybricks.
- Automatizar una liberación versionada que genere paquete Windows, imagen Linux,
  hashes, SBOM y notas desde el mismo commit.

### Prioridad media

- Ampliar conformidad Pybricks en funciones avanzadas únicamente con pruebas y
  documentación de diferencias físicas.
- Mejorar herramientas docentes: conjuntos de misiones, rúbricas, importación y
  exportación de actividades.
- Incorporar más métricas pedagógicas sin recopilar código o datos personales de
  estudiantes.
- Evaluar persistencia Redis en despliegues multiinstancia; no es necesaria para
  uso local.

### Investigación

- Compatibilidad con nuevos kits o perfiles robóticos sin acoplar el dominio a
  una interfaz.
- Reproducción determinista y comparación de trazas entre simulador y robot.
- Distribución firmada e instalador simplificado para aulas Windows.

## Fuera de alcance confirmado

- Equivalencia física exacta con un robot EV3 real.
- Ejecución pública de código arbitrario sin aislamiento adicional y control de
  identidad.
- Compatibilidad total con todas las versiones de Pybricks.

El estado verificable vigente se mantiene en
`Documentos/ESTADO_ACTUAL_PROYECTO.md`; los resultados anteriores permanecen en
informes fechados.
