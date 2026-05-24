## Simulador EV3 Pybricks v1.3.1

Release de mantenimiento y despliegue web.

### Novedades principales
- Mejora de la ayuda web con enfoque didactico y tutoriales guiados.
- Integracion de recursos visuales en la ayuda para facilitar el aprendizaje.
- Adaptacion de la ayuda para entorno publicado en:
  - http://nyquist.app/simuladorlego
- Ajustes de UX en editor de mundos:
  - Se elimina la opcion Guardar.
  - Flujo centrado en Guardar como (selector nativo del sistema).
  - El nombre del mundo pasa a etiqueta informativa al abrir/importar.
- Soporte de despliegue en cPanel:
  - Guia de instalacion especifica.
  - Plantilla WSGI para cPanel.
  - Checklist post-deploy.
  - Archivo requirements.txt para instalacion en servidor.

### Archivos clave actualizados
- pyproject.toml (version 1.3.1)
- README.md
- CHANGELOG.md
- Documentos/GUIA_INSTALACION_CPANEL.md
- Documentos/wsgi_cpanel.py
- Documentos/CHECKLIST_POST_DEPLOY_CPANEL.md
- requirements.txt

### Notas de despliegue
- Requisito de Python del proyecto: >= 3.11.
- En cPanel, usar startup file wsgi.py y entry point app (segun configuracion actual).
