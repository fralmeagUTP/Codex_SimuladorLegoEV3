# gestion-mundos Specification

## Purpose
TBD - created by archiving change habilitar-eliminacion-segura-mundos-tkinter. Update Purpose after archive.
## Requirements
### Requirement: eliminación segura de mundo guardado

El Editor de Mundos MUST permitir eliminar el archivo de mundo abierto cuando
sea un archivo editable del directorio de mundos configurado. MUST solicitar
confirmación y MUST NOT eliminar mundos preestablecidos ni rutas externas.

#### Scenario: eliminar un mundo editable

- **Dado** un mundo editable abierto y guardado
- **Cuando** el usuario confirma la eliminación
- **Entonces** se elimina ese archivo, el editor vuelve a un mundo vacío y se
  informa el resultado.

#### Scenario: proteger recursos incluidos

- **Dado** un mundo preestablecido abierto
- **Cuando** el usuario intenta eliminarlo
- **Entonces** la acción permanece deshabilitada o se rechaza sin borrar el
  archivo.
