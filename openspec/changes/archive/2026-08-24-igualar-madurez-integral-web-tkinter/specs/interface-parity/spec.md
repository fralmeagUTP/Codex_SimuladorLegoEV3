## ADDED Requirements

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
