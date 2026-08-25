## MODIFIED Requirements

### Requirement: La aplicación de escritorio debe abrir contenido local de forma segura

La aplicación Tkinter MUST validar rutas, extensiones y tamaños de scripts,
mundos, configuraciones y activos que abre o guarda. MUST rechazar rutas que
salgan de los directorios permitidos cuando la acción requiera un recurso
gestionado por la aplicación.

#### Scenario: Archivo de mundo no permitido

- **WHEN** una ruta de mundo gestionado contiene recorrido de directorios,
  extensión no permitida o supera el límite configurado
- **THEN** la interfaz rechaza la operación sin modificar el mundo activo
- **AND** muestra un mensaje seguro sin revelar rutas internas

### Requirement: El código de usuario debe ejecutarse aislado en escritorio

La aplicación de escritorio MUST usar el worker aislado como ruta predeterminada
para ejecutar scripts. El modo de compatibilidad local MUST requerir una
configuración explícita destinada a desarrollo o pruebas.

#### Scenario: Script abierto desde Tkinter

- **WHEN** la persona ejecuta un script desde el editor de escritorio
- **THEN** el script se inicia en un worker con entorno saneado, directorio
  temporal privado y límites configurados
- **AND** no recibe secretos heredados del proceso de escritorio

### Requirement: Los diagnósticos de escritorio deben proteger información local

Los diálogos visibles MUST resumir fallos sin mostrar rutas absolutas, variables
de entorno, tokens ni trazas de bajo nivel. Los detalles técnicos, cuando se
registren, MUST mantenerse solo en los registros locales autorizados.

#### Scenario: Falla al abrir o ejecutar contenido

- **WHEN** se produce una excepción técnica durante una operación local
- **THEN** la interfaz presenta una explicación segura y accionable
- **AND** no revela información sensible del sistema
