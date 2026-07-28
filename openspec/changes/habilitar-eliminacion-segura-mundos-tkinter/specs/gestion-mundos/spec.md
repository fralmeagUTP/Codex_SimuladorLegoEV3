## Requisito: eliminación segura de mundo guardado

El Editor de Mundos DEBE permitir eliminar el archivo de mundo abierto cuando
sea un archivo editable del directorio de mundos configurado. DEBE solicitar
confirmación y no DEBE eliminar mundos preestablecidos ni rutas externas.

### Escenario: eliminar un mundo editable

- **Dado** un mundo editable abierto y guardado
- **Cuando** el usuario confirma la eliminación
- **Entonces** se elimina ese archivo, el editor vuelve a un mundo vacío y se
  informa el resultado.

### Escenario: proteger recursos incluidos

- **Dado** un mundo preestablecido abierto
- **Cuando** el usuario intenta eliminarlo
- **Entonces** la acción permanece deshabilitada o se rechaza sin borrar el
  archivo.
