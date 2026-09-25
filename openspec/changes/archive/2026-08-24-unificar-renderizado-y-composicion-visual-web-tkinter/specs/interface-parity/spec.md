## ADDED Requirements

### Requirement: Paridad de assets y geometría del mundo

Para un mismo mundo, `asset_id`, pose inicial y snapshot, Web y Tkinter
MUST resolver assets equivalentes y dibujarlos con la misma geometría física:
origen, ancla, tamaño lógico, rotación, capa y relación mm/píxel. El manifiesto
de assets será la fuente de verdad y las variantes por plataforma deberán estar
versionadas y verificadas por hash.

#### Scenario: Mundo de seguidor de línea

- DADO un mundo que contiene robot y piezas `line_*`
- CUANDO se abre en Web y Tkinter
- ENTONCES ambos muestran el robot sobre la misma coordenada y orientación
- Y las líneas tienen la misma forma, conectividad, grosor lógico y significado
  visual, sin transformarse en obstáculos o fondos no definidos.

#### Scenario: Asset desactualizado o faltante

- DADO un asset canónico que no coincide con su hash, dimensiones o variante
  declarada en una distribución
- CUANDO se ejecuta la validación de recursos
- ENTONCES la prueba falla
- Y la distribución no se considera apta para liberar.

### Requirement: Evidencia de paridad visual por regiones

La integración continua MUST generar capturas comparables de canvas,
telemetría, Brick/LCD, estado y editor para las resoluciones de referencia.
Las diferencias fuera de tolerancias nativas documentadas DEBERÁN bloquear la
liberación.

#### Scenario: Regresión del robot o pista

- DADA una captura de referencia aprobada de un mundo común
- CUANDO una modificación cambia la escala, forma, capa o posición visible del
  robot o una línea más allá de la tolerancia
- ENTONCES CI publica referencia, resultado y diferencia
- Y marca la comprobación como fallida.
