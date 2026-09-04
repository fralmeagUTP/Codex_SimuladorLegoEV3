## Context

El proyecto cuenta con una base de pruebas y especificaciones archivadas, pero
las valoraciones de avance de Web y Tkinter se basan parcialmente en evidencia
de campañas diferentes. La liberación requiere una referencia común: el mismo
catálogo de casos, los mismos estados observables y resultados registrados por
plataforma, resolución y tema.

## Goals / Non-Goals

**Goals:**

- Producir evidencia reproducible para cada caso de uso aplicable a ambas UI.
- Corregir primero cualquier diferencia de resultado de dominio o snapshot.
- Garantizar una interfaz legible y operable en los tamaños y temas soportados.
- Convertir defectos confirmados en regresiones automatizadas cuando sea viable.
- Definir una compuerta de liberación objetiva y trazable a commit.

**Non-Goals:**

- No prometer equivalencia píxel a píxel entre HTML/CSS y widgets nativos.
- No sustituir Tkinter ni modificar la API Pybricks por motivos estéticos.
- No declarar PASS a una prueba que no pueda ejercitarse en una UI real.

## Decisions

1. **Catálogo común de casos de uso.** Se mantendrá un manifiesto versionado
   con identificador, precondiciones, acción, oráculo y aplicabilidad. Evita que
   el catálogo Web y el de escritorio evolucionen de forma independiente.
2. **Oráculo por snapshot terminal y de reinicio.** Canvas, robot, LCD,
   telemetría, editor y barra de estado se contrastarán contra el mismo snapshot
   de sesión. Es preferible a comparar detalles internos o la presentación
   píxel a píxel.
3. **Automatización de dos niveles.** Pytest/contrato cubre determinismo y
   Playwright/pywinauto ejercita la UI real. Los pasos que no puedan automatizarse
   se conservan como manuales con captura, consola y resultado.
4. **Presupuesto de experiencia.** Web se medirá con frames intermedios y
   latencia de controles; escritorio con disponibilidad de la ventana y
   actualización de telemetría. Se registrará el hardware/entorno, sin convertir
   mediciones locales en una garantía universal.
5. **Liberación por evidencia.** Un informe no puede marcar la versión apta si
   queda un defecto crítico/alto abierto, un flujo crítico BLOCKED o una
   divergencia de paridad sin decisión documentada.

## Risks / Trade-offs

- [Automatización de Tkinter depende de sesión gráfica Windows] → ejecutar
  pywinauto en CI Windows o marcar el caso BLOCKED con instrucciones manuales.
- [E2E Web puede ser inestable por temporización] → usar oráculos de estado,
  esperas explícitas y conservar HAR/consola sólo ante fallo.
- [Un catálogo completo aumenta el coste de mantenimiento] → descubrir menús,
  ejemplos, mundos, escenarios y misiones desde recursos de la aplicación.
- [Diferencias nativas visuales] → validar jerarquía, contraste, datos y
  operabilidad, no identidad de píxeles.

## Migration Plan

1. Crear el catálogo, la matriz y los datos aislados.
2. Ejecutar campañas de diagnóstico; registrar fallos antes de corregirlos.
3. Implementar y probar correcciones por flujo crítico.
4. Ejecutar la compuerta completa en Windows y Web con navegadores instalados.
5. Publicar informe ligado al commit y, sólo si cumple los criterios, etiquetar
   o proponer la liberación. Si falla, mantener la versión como no apta y abrir
   un cambio correctivo.

## Open Questions

- La aceptación final requiere que el titular defina navegadores y versiones
  mínimas oficialmente soportadas.
- Debe decidirse si las evidencias binarias E2E se conservan en Git o se
  adjuntan exclusivamente al artefacto de CI.
