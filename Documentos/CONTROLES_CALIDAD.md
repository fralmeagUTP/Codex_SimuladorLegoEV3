# Controles de calidad

La integracion continua ejecuta pruebas, Ruff, Mypy, Bandit y Pip-Audit en cada cambio.
La auditoria resuelve las dependencias directas declaradas en `requirements-audit.txt`,
por lo que no mezcla vulnerabilidades de herramientas instaladas globalmente en el equipo.

Mypy se aplica a núcleo, dominio, aplicación y runtime, además de estados de sesión
y configuración de depuración. La ampliación del perímetro continúa hacia Web y Tkinter
sin ocultar errores de los contratos ya estabilizados.

Bandit omite las reglas `B102` y `B307` exclusivamente porque el simulador necesita
ejecutar programas Pybricks y expresiones de inspeccion de depuracion. Ambas operaciones
se realizan dentro de `RuntimeSandbox` y, en modo aislado, dentro del worker con limites
de tiempo, memoria, red y sistema de archivos. Tambien se omiten `B110` y `B112` para
callbacks opcionales de interfaz: esos callbacks no pueden interrumpir la simulacion.
No se omiten reglas de severidad alta ni se ignoran hallazgos de credenciales.
