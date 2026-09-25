# Diseño: perfil operativo para VPS de producción

## Arquitectura objetivo

`Internet -> Nginx/Caddy (TLS) -> contenedor Waitress -> workers Pybricks`.
El proxy será el único servicio expuesto a Internet; Waitress permanecerá en
una red interna o escuchará únicamente en loopback. El contenedor se ejecutará
como usuario sin privilegios, con filesystem raíz de solo lectura y directorios
temporales explícitamente escribibles.

## Configuración y secretos

La configuración se obtendrá únicamente de variables `EV3_WEB_*`. Un archivo
`.env.production.example` documentará nombres y valores seguros de ejemplo, y
`.env.production` quedará excluido de Git. El inicio en producción fallará con
un mensaje seguro si faltan secreto, HTTPS/cookie segura, HSTS, token operativo
o límites válidos.

Para el VPS inicial se usarán estos valores operativos:

| Parámetro | Valor inicial |
|---|---:|
| Sesiones activas | 20 |
| Simulaciones simultáneas | 4 |
| Ejecución máxima por script | 120 s |
| Hilos Waitress | 8 |
| Límite del contenedor | 2 CPU, 768 MB, 64 PID |

Los límites protegen el proceso de aplicación. El VPS conservará memoria para
el sistema operativo, proxy, caché y operaciones administrativas.

## Sesiones y escalamiento

La primera instalación tendrá una sola instancia, por lo que podrá mantener el
backend local existente. El contrato documentará Redis como requisito antes de
escalar a más de una instancia; no se permitirá levantar réplicas múltiples
que usen almacenamiento local de sesiones de forma silenciosa.

## Operación

Los temporales y metadatos irán a rutas privadas fuera del repositorio y de
`public_html`, propiedad del usuario del servicio y con permiso `0700`. Se
monitorizarán salud, sesiones, ejecuciones, errores 5xx, CPU, memoria, PID y
espacio de temporales. Las métricas no serán públicas: se consultarán desde el
host o con token operativo.

La actualización descargará una versión identificada, construirá la imagen,
ejecutará comprobaciones de salud y conservará la versión previa para una
reversión rápida. Los secretos nunca se incluirán en imágenes, documentación
con ejemplos ni registros.
