# Diseño: campaña exhaustiva de calidad Web

## Principios

1. El inventario se obtiene de la instancia por API y UI al inicio; el término
   “todos” significa cada elemento descubierto y visible en esa ejecución.
2. Un PASS de UI requiere clic/teclado y verificación visible en navegador;
   inspeccionar código, DOM o API no sustituye la prueba manual.
3. Datos de prueba usan prefijo `QA_WEB_`, directorio temporal y limpieza
   verificable; si la limpieza falla se registra sin borrar datos del usuario.
4. Un bloqueo técnico es `BLOCKED`, nunca PASS ni FAIL del producto.
5. Cada defecto confirmado se convierte en regresión automatizada cuando sea
   viable y conserva captura, consola, red y pasos exactos.

## Matriz de ejecución

| Línea | Método | Criterio mínimo |
|---|---|---|
| Inventario | API + navegador | catálogo versionado de menús, ejemplos, mundos, escenarios y misiones |
| Manual visible | navegador gráfico | clic/teclado, diálogo, resultado visual, consola y red por flujo |
| API/contrato | pytest/cliente Flask | errores, autorización de token, DTO, SSE, polling, idempotencia |
| E2E | Playwright real | recorridos críticos y regresiones de UI |
| Multiusuario | dos o más contextos aislados | sin fugas de estado, eventos, mundo, código ni token |
| No funcional | herramientas existentes | accesibilidad, seguridad, carga, recuperación y responsividad |

## Validación de tiempo real

La campaña medirá reloj de pared, `sim_time_s`, ticks, snapshots y frames para
scripts con `wait`, movimiento recto, giro, bucles finitos y radar. La
desviación aceptable se declarará por entorno antes de ejecutar. La evidencia
deberá identificar si cualquier diferencia procede de motor, worker, transporte
o dibujo; ninguna optimización visual puede cambiar la semántica temporal.

## Catálogo manual obligatorio

- Cada elemento de Archivo, Ejemplos, Mundos, Escenarios, Misiones, Tema,
  Fidelidad, Tiempo máximo, Trazas y Ayuda.
- Ejecutar, pausar, reanudar, detener/reiniciar, ubicar robot, theta, haces,
  zoom, paneo y ajuste de mapa.
- Scripts Pybricks correctos, sintaxis inválida, error de runtime, puerto
  inválido, importación no soportada, espera larga, bucle cancelable, LCD,
  motores A–D, DriveBase, sensores y radar.
- Depuración con breakpoint, paso, continuar, watches válidos/inválidos y
  recuperación después de cancelar/error.
- Crear, guardar, cargar, editar, duplicar si existe, cancelar y eliminar
  mundos; validar límites, nombre, sensores, obstáculos, inicio y persistencia.

## Entornos y evidencia

- Navegador gráfico: escritorio 1920×1080, 1280×800 y 1024×768; móvil 390×844.
- Tema claro y oscuro; teclado Tab/Shift+Tab/Enter/Escape y contraste.
- Sesiones: una sesión base, dos usuarios simultáneos y recuperación tras
  recarga, caída de SSE, polling y reinicio de worker cuando aplique.
- Directorio: `Documentos/EVIDENCIA_QA_TOTAL_WEB_YYYY-MM-DD/`.
- Informe: `Documentos/INFORME_QA_TOTAL_WEB_YYYY-MM-DD.md`.

## Criterio de liberación

No apta si falla ejecución, cancelación, aislamiento de sesión, persistencia de
mundos, seguridad del runtime o coherencia terminal. Apta con observaciones
solo si los riesgos medios/bajos tienen responsable, regresión y mitigación.
