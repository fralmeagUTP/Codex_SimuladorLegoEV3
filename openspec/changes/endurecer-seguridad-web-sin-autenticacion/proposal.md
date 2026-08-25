# Propuesta: endurecer seguridad Web sin autenticación

## Motivo

La evaluación de seguridad confirmó que el simulador Web tiene aislamiento de
sesiones, límites globales y cabeceras de protección, pero aún requiere
controles de perímetro antes de exponerse en `nyquist.app`. El producto seguirá
siendo anónimo: no se incorporarán cuentas, inicio de sesión ni roles.

## Cambio propuesto

Endurecer la aplicación Web, el ejecutable de escritorio y sus despliegues con
cuotas por cliente, protección de endpoints operativos, cabeceras HTTPS
completas, controles anti-CSRF basados en origen, almacenamiento de metadatos
con permisos restrictivos, y perfiles de ejecución aislada para workers. La
aplicación conservará los tokens de propietario de sesión como autorización de
capacidad, sin identidad de usuario.

## Alcance

- Límite de solicitudes y creación de sesiones por dirección cliente.
- Protección configurable de `/healthz`, `/metrics` y `/operations`.
- Cabeceras de seguridad, HTTPS y validación de origen para comandos mutables.
- Endurecimiento del directorio de metadatos de sesión.
- Perfil de despliegue Linux para workers sin privilegios, con límites de
  procesos, memoria, CPU y salida de red restringida por infraestructura.
- Protección local Tkinter: sandbox de scripts, ficheros de mundos/preferencias,
  ejecución del binario y diagnósticos sin secretos.
- Ciclo de vida de recursos: cierre garantizado de workers, detección de
  huérfanos propios, borrado de temporales, trazas acotadas y persistencia local
  atómica.
- Pruebas automáticas, documentación de Nyquist y evidencia de verificación.

## Fuera de alcance

- Autenticación, cuentas de usuario, roles o persistencia personal.
- Modificar la semántica didáctica de scripts, mundos o misiones.
- Declarar que el sandbox Python es suficiente contra código hostil sin la
  frontera de sistema operativo definida en este cambio.

## Éxito esperado

Una instancia pública anónima resiste abuso básico de creación de sesiones,
oculta diagnósticos operativos al público, exige HTTPS correctamente configurado
y ejecuta scripts bajo límites verificables y documentados.
