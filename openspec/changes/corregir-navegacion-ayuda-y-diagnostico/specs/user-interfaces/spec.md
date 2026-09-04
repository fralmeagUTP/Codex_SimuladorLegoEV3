## ADDED Requirements

### Requirement: Menú de ayuda coherente y no redundante

Las interfaces Web y Tkinter MUST ofrecer, en el mismo orden, los comandos
`Centro de ayuda`, `Guía rápida: primera simulación`, `Diagnóstico de sesión`,
`Exportar diagnóstico JSON` y `Acerca de`. Cada comando MUST indicar mediante
su etiqueta el destino que realmente abre.

#### Scenario: Guía rápida desde el menú Ayuda

- **WHEN** el usuario selecciona `Guía rápida: primera simulación`
- **THEN** la interfaz abre o enfoca la guía compartida `first-simulation`
- **AND** no presenta el catálogo completo como si fuese un destino distinto.

#### Scenario: Centro de ayuda desde el menú Ayuda

- **WHEN** el usuario selecciona `Centro de ayuda`
- **THEN** la interfaz presenta el catálogo completo navegable de guías
- **AND** conserva la acción rápida como acceso específico no ambiguo.

### Requirement: Diagnóstico con identidad propia

La interfaz MUST mostrar el diagnóstico de sesión en una superficie titulada
`Diagnóstico de sesión`, separada visual y semánticamente de `Acerca de`.

#### Scenario: Apertura de diagnóstico

- **WHEN** el usuario selecciona `Diagnóstico de sesión`
- **THEN** ve el título `Diagnóstico de sesión` y datos seguros de la sesión
- **AND** el diálogo se puede cerrar con Escape y devuelve el foco al menú.

### Requirement: Exportación de diagnóstico paritaria

Web y Tkinter MUST permitir exportar un documento JSON UTF-8 con diagnóstico
de la sesión actual, sin fuente de usuario, secretos ni datos de otra sesión.

#### Scenario: Exportación exitosa

- **WHEN** el usuario confirma `Exportar diagnóstico JSON`
- **THEN** la interfaz guarda o descarga un archivo `.json` válido
- **AND** su contenido coincide con el esquema de diagnóstico permitido.
