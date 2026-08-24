# interface-parity Specification

## Purpose
TBD - created by archiving change elevar-calidad-y-paridad-de-interfaz. Update Purpose after archive.
## Requirements
### Requirement: Paridad funcional obligatoria
Las interfaces MUST cumplir este requisito.

El sistema DEBERÁ proporcionar en Web y Tkinter el mismo conjunto de casos de uso
de simulación, edición de código, depuración, gestión de mundos, telemetría,
brick virtual, trazas, ayuda y recuperación de sesión que sea aplicable a una UI.
Una función nueva NO DEBERÁ considerarse terminada hasta estar disponible y
verificada en ambas interfaces.

#### Scenario: Nueva función de simulación

- DADA una función nueva aprobada para el simulador
- CUANDO se integra en el producto
- ENTONCES DEBERÁ estar accesible desde Web y Tkinter
- Y ambas interfaces DEBERÁN producir el mismo resultado de dominio, estado y error para la misma entrada.

### Requirement: Contrato compartido de experiencia
Las interfaces MUST cumplir este requisito.

Cada función de UI DEBERÁ estar representada por un caso de uso y contrato común
que defina precondiciones, entrada, transición de estado, snapshot esperado,
resultado y errores. Las interfaces DEBERÁN ser adaptadores de ese contrato.

#### Scenario: Ejecución de un mismo programa

- DADO el mismo mundo, programa y perfil de simulación
- CUANDO se ejecuta desde Web y desde Tkinter
- ENTONCES ambas ejecuciones DEBERÁN producir trazas y snapshots equivalentes dentro de la tolerancia definida.

### Requirement: Pruebas de paridad
Las interfaces MUST cumplir este requisito.

CI DEBERÁ ejecutar una matriz de paridad con pruebas de contrato y E2E para ambas
interfaces. Una divergencia funcional DEBERÁ bloquear la integración.

#### Scenario: Divergencia de interfaz detectada

- DADA una capacidad disponible sólo en una interfaz
- CUANDO se ejecuta la matriz de paridad
- ENTONCES CI DEBERÁ fallar
- Y el cambio NO DEBERÁ integrarse hasta restaurar la paridad.

### Requirement: Catálogo verificable de paridad

Las interfaces MUST mantener un catálogo versionado de los casos de uso
aplicables, con identificador, entrada, resultado de dominio, estado visual y
resultado observado por plataforma.

#### Scenario: Capacidad disponible en una interfaz

- **DADO** un comando, menú, diálogo o flujo disponible en Web o Tkinter;
- **CUANDO** se actualice el catálogo de paridad;
- **ENTONCES** se clasificará como equivalente, adaptación aceptada o brecha;
- **Y** una brecha impedirá declarar paridad completa hasta corregirla o
  aprobar explícitamente su no aplicabilidad.

### Requirement: Equivalencia de estados críticos

Para el mismo mundo, programa y perfil, Web y Tkinter MUST reflejar un estado
equivalente al iniciar, pausar, reanudar, finalizar, fallar y reiniciar.

#### Scenario: Reinicio desde ejecución activa

- **DADO** una simulación activa que cambió pose, telemetría y LCD;
- **CUANDO** el usuario selecciona detener y reiniciar en cualquiera de las UI;
- **ENTONCES** canvas, robot, LCD, telemetría y estado se restauran al snapshot
  inicial del mundo;
- **Y** no quedan trazas, robots o eventos de la ejecución anterior.

### Requirement: Madurez integral equivalente

Web y Tkinter MUST alcanzar el mismo nivel verificable de arquitectura,
diseño, funcionalidad, pedagogía, ayuda, calidad y observabilidad para toda
capacidad aplicable. La matriz MMI DEBERÁ identificar evidencia, estado,
limitación y alternativa por plataforma.

#### Scenario: Capacidad nueva aplicable

- DADO un caso de uso nuevo que puede realizarse en Web y Tkinter;
- CUANDO se solicita su cierre;
- ENTONCES tendrá contrato, implementación, ayuda, telemetría diagnóstica y
  pruebas equivalentes en ambas UI;
- Y no podrá declararse terminada mientras una plataforma carezca de evidencia.

### Requirement: Excepción de plataforma explícita

Una capacidad exclusiva de navegador o escritorio MUST clasificarse como
`N/A` solo si documenta la razón técnica y una alternativa equivalente para el
objetivo de usuario.

#### Scenario: Función móvil Web

- DADO un requisito de viewport móvil;
- CUANDO se evalúa Tkinter;
- ENTONCES Tkinter se clasifica como `N/A` por plataforma;
- Y la matriz registra la alternativa de escritorio en resoluciones soportadas.

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

