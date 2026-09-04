# Propuesta: preparar despliegue Web para VPS de producción

## Motivo

BotLab Studio Web se desplegará inicialmente en un VPS KVM con 2 vCPU y 8 GB
de RAM. La aplicación ya dispone de Docker, Waitress, límites de sesión y
controles de seguridad, pero requiere un contrato operativo reproducible para
que una instalación real no dependa de valores de desarrollo, secretos dentro
del repositorio ni decisiones manuales no verificadas.

## Cambio propuesto

Entregar un perfil de producción verificable para un VPS único: configuración
externa segura, contenedor sin privilegios, proxy HTTPS, límites conservadores
de concurrencia, almacenamiento temporal privado, salud/observabilidad y
procedimientos de instalación, actualización y reversión. La capacidad inicial
se fijará en 20 sesiones activas y 4 simulaciones concurrentes; cualquier
aumento deberá sustentarse en una prueba de carga documentada.

## Alcance

- Plantilla de variables de entorno sin secretos reales y validación de inicio.
- Perfil Docker/Compose para VPS de 2 vCPU/8 GB y documentación del proxy.
- Directorios privados para workers y espejo de sesiones, con limpieza segura.
- Endpoints de salud y métricas protegidos para uso operativo.
- Guías ejecutables de instalación, respaldo, actualización y reversión.
- Pruebas automatizadas de configuración productiva y una campaña de carga
  local equivalente a los límites iniciales.

## Fuera de alcance

- Autenticación, cuentas de usuario, roles o cobros.
- Alta disponibilidad, balanceo y despliegue multi-VPS en la primera versión.
- Prometer una cantidad de usuarios sin evidencia de pruebas sobre el VPS.

## Éxito esperado

Una persona con acceso root puede publicar la aplicación detrás de HTTPS sin
exponer secretos ni puertos internos; el sistema rechaza configuración insegura,
mantiene simulaciones aisladas dentro de los límites y ofrece evidencia clara
para aceptar o ajustar la capacidad del VPS.
