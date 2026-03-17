# ROADMAP — Simulador EV3 Pybricks

Estado actualizado: 2026-03-16

## Fases completadas

- ✅ **Fase 1 — Domain (robot base)**
  - Modelos principales del robot y base de movimiento.

- ✅ **Fase 2 — Domain (sensores y mundo)**
  - Sensores de dominio, mundo 2D, colisiones base.

- ✅ **Fase 3 — Core (simulación)**
  - `CommandQueue`, `EventBus`, `SimulationEngine`.
  - Snapshot de estado para UI y telemetría.

- ✅ **Fase 4 — Runtime (ejecución de scripts)**
  - `ExecutionPolicy`, `RuntimeSandbox`, `RuntimeController`.

- ✅ **Fase 5 — API Pybricks virtual**
  - `pybricks.hubs`, `ev3devices`, `robotics`, `tools`, `parameters`.
  - `PybricksFactory` y contexto global de sesión.

- ✅ **Fase 6 — Application Layer**
  - `SimulationService` como fachada de alto nivel.
  - `SnapshotDTO` para serialización/consumo UI.

- ✅ **Fase 7 — UI Tkinter**
  - Ventana principal, canvas de mundo, editor, panel brick y telemetría.

- ✅ **Fase 8 — Infraestructura**
  - Persistencia JSON del mundo.
  - Catálogo de ejemplos.

## Ajustes y fixes posteriores (post-fase 8)

- ✅ Ejecución correcta de scripts con guardia:
  - `if __name__ == "__main__":`

- ✅ Compatibilidad de movimiento por motores individuales:
  - `Motor.run()` en pares tipo tanque (A/C o B/C).

- ✅ Fix de altavoz en engine (`duration_ms`) y estabilidad del hilo de simulación.

- ✅ Audio real en Windows:
  - Backend `winsound` con fallback seguro (`NullAudioOutput`).

- ✅ Ejemplo de prueba A/V agregado:
  - `Documentos/Ejemplos/12_pantalla_altavoz_test.py`

## Fase 9 — Pulido y Release (completada)

- ✅ UX de pruebas
  - Menú de mundos (`Mundos`) con carga JSON.
  - Menú de escenarios (`Escenarios`) para cargar mundo+ejemplo en un clic.
  - Mejor feedback de errores y estado en la UI.

- ✅ Escenarios preconfigurados de sensores
  - `01_linea_negra.json` (línea negra para color sensor).
  - `02_obstaculos_beacon.json` (obstáculos + beacon).

- ✅ Empaquetado Windows y guía de distribución
  - Guía: `Documentos/GUIA_RELEASE_WINDOWS.md`.

- ✅ Smoke tests E2E de ejemplos críticos
  - `tests/release/test_smoke_examples.py`.

## Mejoras visuales y UX (post-fase 9)

- ✅ **Robot visual tipo EV3 (vista superior)**
  - Sprite con cuerpo, ruedas, pantalla, D-pad, puertos y barra sensora.
  - Dimensiones: 175×140 mm en coordenadas del mundo.
  - Colisión mostrada sólo como cambio de color de borde.

- ✅ **Layout verdaderamente responsivo**
  - Debounce 60 ms en `<Configure>` → `_apply_responsive_layout()`.
  - `sash_place()` proporcional en los tres `PanedWindow`.

- ✅ **Mapa ocupa todo el espacio del canvas sin distorsión**
  - Transformación no uniforme: `sx = cw/world_w`, `sy = ch/world_h`.
  - Trail almacenado en mm → reconvertido a px en cada redibujado (resize-safe).

- ✅ **Editor de código con tema oscuro y sintaxis coloreada**
  - Fondo `#0D1117`, texto `#E6EDF3`.
  - Colores tipo GitHub: keywords azul, builtins violeta, strings naranja,
    comentarios verde, números azul claro (con highlighting de dígitos).

- ✅ **Panel de telemetría con scroll único**
  - Un solo `tk.Canvas` + `tk.Scrollbar` para toda la información.
  - `_bind_mousewheel_recursive()` propaga la rueda del ratón a todos los hijos.
  - Ángulo de motor mostrado en grados (°).

- ✅ **Colocación inicial del robot con el ratón**
  - Antes de ejecutar, el canvas activa `placement_mode` (cursor en cruz).
  - Al mover el ratón: contorno fantasma punteado (azul `#4FC3F7`) del robot.
  - Al hacer clic: marcador naranja (`#FF6F00`, círculo + cruz) fija la posición.
  - Barra informativa sobre el canvas muestra la posición elegida.
  - Llama a `SimulationService.set_robot_start(x_mm, y_mm)`.
  - Se desactiva al pulsar Ejecutar y se reactiva al detener/error.
  - Marcador se reposiciona correctamente al redimensionar la ventana.

## Estado de pruebas

- ✅ **26 tests de UI** pasando (`tests/ui/test_ui.py`) con mock Tkinter.
  - Mock incluye: `bind`, `unbind`, `winfo_children`, `create_window`, `bbox`.
- ✅ **3 smoke tests** E2E (`tests/release/test_smoke_examples.py`).

## Fase 10 — Distribución y calidad continua (en curso)

- ✅ Script de build release reproducible (PowerShell) para PyInstaller.
  - `scripts/build_release_windows.ps1`

- ⏳ **Pendiente:**
  - CI automatizada de tests (`pytest`) en Windows (GitHub Actions).
  - Checklist de QA de release (funcional + rendimiento básico).
  - Versionado y changelog por release (`v0.2.0+`).

## Funcionalidades sugeridas para siguientes iteraciones

- ⬜ Rotar el robot con el ratón antes de ejecutar (ajuste de `theta_deg`
  mediante arrastre o rueda del ratón tras fijar posición).
- ⬜ Tooltip con coordenadas en tiempo real mientras se coloca el robot.
- ⬜ Múltiples robots en el mismo mundo.
- ⬜ Exportar traza de simulación a CSV/JSON.
