# Reporte de Diseño Adaptivo Web

Fecha: 2026-05-24  
Proyecto: Simulador EV3 Pybricks (Web Flask)  
Version evaluada: `STATIC_ASSET_VERSION=2026-05-24-responsive-audit-v5`

## 1. Objetivo

Verificar que la app web sea usable en dispositivos con navegador (movil, tablet y escritorio), evaluando:

- Estructura responsive.
- Accesibilidad visual de controles principales.
- Ausencia de scroll horizontal de pagina.
- Comportamiento en motores de navegador distintos.

## 2. Evidencia generada

Carpeta de evidencias:

- [EVIDENCIA_RESPONSIVE_2026-05-24](/c:/Users/fralm/Desktop/Codex_SimuladorLegoEV3/Documentos/EVIDENCIA_RESPONSIVE_2026-05-24)

Métricas consolidadas:

- [responsive_metrics.json](/c:/Users/fralm/Desktop/Codex_SimuladorLegoEV3/Documentos/EVIDENCIA_RESPONSIVE_2026-05-24/responsive_metrics.json)

Se capturaron 24 imagenes (vista superior e inferior de `/` y `/worlds` en 6 viewports).

## 3. Matriz de viewports

Viewports evaluados:

- `360x740` (mobile_s)
- `390x844` (mobile_m)
- `430x932` (mobile_l)
- `768x1024` (tablet_portrait)
- `1024x768` (tablet_landscape)
- `1366x768` (laptop)

Resultado global en ambas rutas (`/` y `/worlds`):

- Scroll horizontal de pagina: **No detectado** (`horizontalPageOverflow=false`).
- Flujo vertical: **Disponible** en moviles/tablet portrait para navegar paneles apilados.
- Desktop/tablet landscape: layout compacto de una sola pantalla sin scroll vertical global.

## 4. Compatibilidad por motor

Smoke responsivo ejecutado en Playwright:

- Chromium: `390x844` y `1366x768` -> OK
- Firefox: `390x844` y `1366x768` -> OK
- WebKit: `390x844` y `1366x768` -> OK

Checks usados:

- `pageOverflowX = false`
- `#runBtn` visible
- `#codeEditor` visible
- `#sessionStatus` visible

## 5. Checklist QA (adaptivo)

Estado actual:

- [x] La barra de menu se adapta con wrap en ancho reducido.
- [x] Controles de ejecucion se redistribuyen en filas (botones tocables).
- [x] Panel debug reduce friccion en movil (inputs a ancho completo).
- [x] Editor de codigo visible en moviles (con scroll vertical de pagina).
- [x] Ruta `/worlds` usable con toolbar adaptada y panel de propiedades apilado.
- [x] Sin scroll horizontal de pagina en los viewports validados.
- [x] Funciona en Chromium/Firefox/WebKit (smoke responsivo basico).

## 6. Observaciones de diseño

- En moviles, la pagina de simulacion prioriza legibilidad y control sobre densidad: los paneles se apilan verticalmente.
- El mapa/canvas conserva tamano fisico para paridad didactica; por eso su desplazamiento ocurre dentro del panel de mapa y no como overflow de pagina.
- La altura total en movil es grande por cantidad de modulos (telemetria, brick, editor, debug). Es un compromiso esperado para mantener todas las funciones en una sola vista.

## 7. Recomendacion siguiente (opcional)

Para una UX movil aun mejor en uso docente:

- Implementar modo de pestanas en movil (`Mapa | Telemetria | Editor | Brick`) para reducir scroll vertical continuo.

