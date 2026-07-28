# Diseño: elevar calidad, seguridad y paridad de interfaces

## Decisiones arquitectónicas

### 1. Núcleo de experiencia compartido

Se definirá un contrato de casos de uso independiente de la interfaz. Cada caso
de uso tendrá una acción, precondiciones, entrada, transición esperada, snapshot
final y resultado de error. Web y Tkinter serán adaptadores del mismo contrato.

```text
Contrato de experiencia / casos de uso
              │
    ┌─────────┴─────────┐
    │                   │
Adaptador Web      Adaptador Tkinter
    │                   │
    └──── Application Facade ────┘
                 │
        Sesión + Runtime + Motor
```

La paridad es funcional, no exige identidad visual pixel a pixel. Deben coincidir
acciones disponibles, validaciones, semántica, estados, telemetría, depuración,
resultados, errores y accesibilidad equivalente por teclado/ratón donde aplique.

### 2. Máquina de estados única

Las sesiones usarán estados explícitos y transiciones validadas:

```text
created → ready → running ⇄ paused
                    │        │
                    ├────────┘
                    ↓
          finished | stopped | error | timed_out
                    ↓
                 resetting → ready
```

`finished` conserva el último snapshot y eventos de salida. El reinicio sólo se
produce mediante una intención explícita de UI o una política configurada que
otorgue un período visible mínimo y nunca descarte eventos no entregados.

### 3. Worker de ejecución aislado

La ejecución se moverá a un proceso trabajador por sesión activa, o a un pool de
procesos aislados. El proceso API/UI intercambiará comandos, snapshots, errores y
eventos de depuración a través de IPC versionado. El worker se ejecutará con:

- límite de CPU, memoria y tiempo;
- directorio temporal aislado;
- red deshabilitada;
- usuario de mínimos privilegios;
- terminación forzada cuando alcance límites o se solicite stop.

El actual sandbox seguirá validando imports y API permitida como defensa adicional,
pero no será considerado el límite de seguridad principal.

### 4. Contrato de snapshot y trazas

Se versionará el DTO de snapshot. Cada evento incluirá `session_id`, `sequence`,
`snapshot_version`, estado, tiempo simulado y origen. El registrador de trazas
guardará comandos, snapshots, errores y eventos para exportación JSON/CSV y
reproducción determinista.

### 5. Fidelidad por perfiles

Se implementarán perfiles configurables:

- `ideal`: comportamiento determinista actual para aprendizaje inicial;
- `realista`: latencia, ruido, rango, cono ultrasónico, deriva gyro, variación de
  superficie y limitaciones de movimiento;
- `calibrado`: parámetros de un robot o aula concreta.

La semántica de `COAST`, `BRAKE`, `HOLD`, curvas y operaciones bloqueantes será
centralizada en el dominio y la API virtual no accederá a atributos privados del
motor.

### 6. Modularización y calidad

La capa web se dividirá en módulos de transporte, estado, editor, depuración,
telemetría, brick y render de mundo. La capa de aplicación separará coordinación
de runtime, mundo, debug y transformación de DTOs. Se añadirán Ruff, formatter,
type checker, Bandit, cobertura con umbral, escaneo de dependencias y pre-commit.

### 7. Conformidad y calidad de producto

Una matriz Pybricks será fuente de verdad para soporte de métodos. Se incorporarán
pruebas de conformidad, carga, resiliencia de Redis/archivo, métricas de tick,
latencia y sesiones. Los escenarios educativos verificables se ejecutarán como
misiones con criterios de aprobación.

## Compatibilidad y migración

1. Mantener esquema JSON de mundos versión 1 y añadir migradores explícitos antes
   de cualquier cambio incompatible.
2. Mantener API REST existente durante una versión con adaptadores de transición.
3. Añadir `snapshot_version` antes de ampliar el DTO.
4. Implementar primero contratos y pruebas de paridad; luego mover funciones UI.
5. Activar workers aislados detrás de feature flag; retirar ejecución in-process
   sólo después de completar compatibilidad y pruebas de carga.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Diferencia Web/Tkinter | Matriz de paridad y pruebas de contrato obligatorias. |
| IPC aumenta latencia | Snapshots limitados por frecuencia y medición de presupuesto. |
| Cambio de runtime rompe ejemplos | Suite completa de ejemplos y compatibilidad progresiva. |
| Física más realista rompe lecciones | Perfil `ideal` como valor inicial y perfiles opt-in. |
| Dependencia de procesos en Windows | Adaptador de worker compatible con Windows y Linux, validado en CI. |
