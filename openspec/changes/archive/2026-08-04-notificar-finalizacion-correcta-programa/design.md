# Diseño

Cada interfaz mantiene un identificador local de ciclo de ejecución. Al iniciar se crea un ciclo; los estados `stopped`, `timed_out`, `error` y `reset` lo invalidan. Solo `finished` del ciclo activo puede emitir la notificación y, una vez emitida, el ciclo se marca como notificado.

En Web el aviso se programa en `requestAnimationFrame`. El backend publica el snapshot terminal antes del evento de estado y el sondeo renderiza su snapshot en el mismo ciclo, por lo que LCD, canvas, telemetría y estado ya están sincronizados antes del toast.

En Tkinter se programa con `after_idle`, después de encolar la actualización de widgets. El diálogo nunca se muestra durante el cierre de la ventana.
