# Diseño: endurecimiento anónimo de la aplicación Web

## Principio de acceso

El sistema conserva sesiones anónimas. El `owner_token` autoriza exclusivamente
operaciones sobre la sesión que lo emitió; no representa una identidad de
persona. Las cuotas se aplicarán por huella de cliente de confianza, obtenida
del proxy solo cuando este esté configurado explícitamente.

## Controles de aplicación

1. Un limitador en memoria por ventana deslizante protegerá creación de sesión,
   carga de scripts/mundos y comandos de ejecución. Devolverá `429` con
   `Retry-After` sin crear workers.
2. Los endpoints operativos usarán una política `public`, `local` o `token`.
   La instalación productiva usará `local` detrás del proxy de monitoreo.
3. Los comandos mutables validarán `Origin` o cabeceras Fetch Metadata cuando
   la petición provenga de navegador. Las llamadas de servicio podrán usar un
   token operativo configurado fuera del repositorio.
4. Las cookies mantendrán `HttpOnly`, `SameSite=Lax` y `Secure`; en HTTPS se
   añadirá preferentemente el prefijo `__Host-` cuando la ruta raíz lo permita.
5. La CSP incluirá `object-src 'none'`, `form-action 'self'` y se documentará
   HSTS como responsabilidad del terminador TLS/proxy.

## Límites de ejecución

El worker mantiene el namespace Pybricks restringido, pero el perfil Linux de
producción añadirá una frontera externa: usuario sin privilegios, cgroups v2
para CPU/memoria/PIDs, filesystem temporal escribible y denegación de egress.
Docker documentará estos límites sin requerir privilegios de contenedor.

## Aplicación de escritorio

Tkinter no expone una API de red ni requiere identidad de usuario. El riesgo
principal es abrir mundos, ejemplos o scripts locales no confiables. El mismo
worker aislado será la ruta predeterminada de ejecución; el modo local de
compatibilidad permanecerá explícito y solo para desarrollo/pruebas. Las rutas
de archivos se validarán contra directorios permitidos, la persistencia usará
permisos restrictivos del usuario actual y el ejecutable no solicitará privilegios
elevados ni heredará secretos hacia el worker.

Los errores técnicos quedarán en log local seguro y la interfaz mostrará un
mensaje genérico, sin rutas absolutas, variables de entorno o trazas internas.

## Persistencia y telemetría

El espejo de archivos se creará con permisos solo para el usuario de servicio.
Los diagnósticos públicos no expondrán PID, ruta local, backend ni errores
internos. Los detalles se registrarán de forma estructurada sin tokens ni
contenido completo de scripts.

## Ciclo de vida de memoria, workers y temporales

Cada `SimulationSession` registrará de forma privada los PID y directorios
temporales de sus workers. El cierre normal, la expiración de sesión y el cierre
de la aplicación deberán detener, esperar y verificar la finalización del
worker, antes de liberar colas y referencias. Al iniciar, la aplicación podrá
limpiar únicamente residuos identificados como propios y expirados; nunca
terminará procesos ajenos ni borrará temporales no administrados.

La carga de un mundo JSON usará un temporal dentro de un bloque `try/finally`,
que se eliminará incluso si falla el parseo o la carga. Se añadirá un barrido
con antigüedad máxima configurable para temporales y metadatos de sesión.

`SimulationTrace` tendrá una capacidad máxima configurable y reportará cuando
la traza se trunque. El valor predeterminado preservará el uso didáctico sin
permitir crecimiento de memoria no acotado. Las preferencias de escritorio se
guardarán mediante archivo temporal y reemplazo atómico.

## Verificación

Las pruebas cubrirán límite por cliente, rechazo de origen cruzado, acceso
operativo denegado, cabeceras, permisos del espejo, configuración productiva y
recuperación/cancelación de worker. Se mantendrá una campaña HTTP concurrente
contra servidor temporal, sin datos reales ni Nyquist.
