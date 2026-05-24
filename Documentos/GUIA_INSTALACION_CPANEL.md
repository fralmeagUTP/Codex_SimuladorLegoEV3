# Guia de instalacion en cPanel (Hosting Web)

Esta guia explica como publicar la app web del simulador EV3 en cPanel, usando **Setup Python App** (Passenger).
Esta version ya viene adaptada al panel que mostraste en captura.

Objetivo de despliegue:

- URL publica: `http://nyquist.app/simuladorlego`
- Navegacion por interfaz web (sin que el usuario final escriba rutas manuales)

## 1. Requisitos previos

- Hosting con cPanel que incluya:
  - Python App (Passenger)
  - Python 3.11 o superior (recomendado)
  - Acceso a File Manager
  - Ideal: Terminal/SSH en cPanel
- Dominio/subdominio activo en cPanel.
- Proyecto disponible en ZIP o por Git.

## 2. Configuracion detectada en tu cPanel

Segun tu captura, hoy tienes:

- Python version: `3.10.19`
- Application root: `simuladorlego`
- Application URL: `nyquist.app/simuladorlego`
- Startup file: `wsgi.py`
- Entry point: `app`
- Virtualenv: `/home/ur5cxigur1qs/virtualenv/simuladorlego/3.10`
- App root fisico: `/home/ur5cxigur1qs/simuladorlego`

### Importante: bloqueo por version de Python

El proyecto declara `requires-python >=3.11` en `pyproject.toml`.
Con Python `3.10.19` el despliegue puede fallar al instalar dependencias.

Opciones:

1. Recomendado: cambiar la app en cPanel a Python `3.11` o superior.
2. Alternativa temporal (no recomendada): adaptar el proyecto para 3.10 y volver a validar pruebas.

## 3. Estructura recomendada en el hosting

Para tu cuenta:

- Codigo fuente: `/home/ur5cxigur1qs/simuladorlego`
- URL publica: `/simuladorlego`

La carpeta de codigo debe conservar la estructura del repo, pero en produccion solo necesitas subir lo que la app usa realmente.

## 4. Que archivos y carpetas debes subir

Si quieres una respuesta directa, sube al servidor estas rutas del proyecto:

```text
/home/ur5cxigur1qs/simuladorlego/wsgi.py
/home/ur5cxigur1qs/simuladorlego/pyproject.toml
/home/ur5cxigur1qs/simuladorlego/requirements.txt
/home/ur5cxigur1qs/simuladorlego/README.md
/home/ur5cxigur1qs/simuladorlego/simulador_ev3/
/home/ur5cxigur1qs/simuladorlego/examples/
/home/ur5cxigur1qs/simuladorlego/worlds/
/home/ur5cxigur1qs/simuladorlego/docs/
```

Y, si quieres conservar compatibilidad con contenido antiguo, tambien puedes subir:

```text
/home/ur5cxigur1qs/simuladorlego/Documentos/
/home/ur5cxigur1qs/simuladorlego/scripts/
```

### Obligatorios para la app web

Sube estos elementos al raiz del Application root (`/home/ur5cxigur1qs/simuladorlego`):

- `simulador_ev3/`
- `examples/`
- `worlds/`
- `docs/` si quieres servir la documentacion canonica nueva
- `pyproject.toml`
- `requirements.txt`
- `README.md` si quieres conservar informacion del proyecto en el hosting
- `wsgi.py` en la raiz del Application root

### Recomendados para operacion y mantenimiento

- `Documentos/` solo si todavia dependes de material legacy o quieres mantener compatibilidad con rutas antiguas
- `scripts/` si vas a ejecutar verificaciones o despliegues desde SSH
- `tests/` solo si vas a correr pruebas en el hosting; no es necesario para produccion
- `CHANGELOG.md` y `ROADMAP.md` solo como referencia, no son requeridos para ejecutar la app

### No es necesario subir en produccion

- `build/`
- `simulador_ev3.egg-info/`
- `.pytest_cache/`
- `.venv/` o cualquier entorno virtual local
- archivos temporales o de evidencia que no usa la app en runtime

## 5. Archivo de arranque `wsgi.py`

En cPanel el startup file debe llamarse `wsgi.py` y vivir en la raiz del Application root.

Ya existe un entrypoint de produccion en `simulador_ev3/web/wsgi.py`, pero en cPanel conviene crear un wrapper en la raiz del hosting que importe `create_app()`.

Contenido recomendado para `/home/ur5cxigur1qs/simuladorlego/wsgi.py`:

```python
import os
import sys

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from simulador_ev3.web.app import create_app

app = create_app()
```

## 6. Subir el proyecto

### Opcion A: File Manager (ZIP)

1. Comprime el proyecto local en un `.zip`.
2. Antes de comprimir, elimina si quieres los elementos no necesarios de produccion: `build/`, `.pytest_cache/`, `simulador_ev3.egg-info/`.
3. En cPanel -> **File Manager**, sube el ZIP a `/home/ur5cxigur1qs/simuladorlego`.
4. Extrae el contenido.
5. Verifica que existan: `pyproject.toml`, `wsgi.py`, `simulador_ev3/`, `examples/` y `worlds/`.

### Opcion B: Git (si esta disponible)

1. Clona el repo dentro de `/home/ur5cxigur1qs/simuladorlego`.
2. Verifica la rama/version deseada.

## 7. Crear/ajustar la aplicacion Python en cPanel

En cPanel -> **Setup Python App** -> edita la app `NYQUIST.APP/SIMULADORLEGO`:

- Python version: `3.11` (o superior)
- Application root: `simuladorlego`
- Application URL: `simuladorlego` (ruta)
- Application startup file: `wsgi.py`
- Application Entry point: `app`

Guarda la app.

## 8. Instalar dependencias

Con Terminal/SSH (recomendado), entra a la carpeta de la app y usa el venv creado por cPanel:

```bash
cd /home/ur5cxigur1qs/simuladorlego
source /home/ur5cxigur1qs/virtualenv/simuladorlego/3.11/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e .
```

### Opcion cPanel directa con archivo de requerimientos

Si prefieres instalar desde el boton **Run Pip Install** en cPanel, usa el archivo:

- `requirements.txt`

Comando equivalente por terminal:

```bash
cd /home/ur5cxigur1qs/simuladorlego
source /home/ur5cxigur1qs/virtualenv/simuladorlego/3.11/bin/activate
pip install -r requirements.txt
```

Si cPanel sigue en Python 3.10, usa el venv que te muestra la propia interfaz:

```bash
source /home/ur5cxigur1qs/virtualenv/simuladorlego/3.10/bin/activate
cd /home/ur5cxigur1qs/simuladorlego
pip install --upgrade pip setuptools wheel
pip install -e .
```

Si falla por version de Python, vuelve al paso 5 y cambia a 3.11.

Opcional (si usas servidor alternativo como waitress para pruebas internas):

```bash
pip install -e .[web-prod]
```

Si tu plan no permite `pip install -e .`, usa:

```bash
pip install .
```

## 9. Variables de entorno recomendadas en cPanel

En **Setup Python App** -> **Environment Variables**, agrega:

```text
EV3_WEB_SECRET_KEY=<una-clave-larga-y-unica>
EV3_WEB_SESSION_COOKIE_SECURE=true
EV3_WEB_EXAMPLES_DIR=/home/ur5cxigur1qs/simuladorlego/examples
EV3_WEB_WORLDS_DIR=/home/ur5cxigur1qs/simuladorlego/worlds
EV3_WEB_IMAGE_ASSETS_DIR=/home/ur5cxigur1qs/simuladorlego/simulador_ev3/assets
EV3_WEB_ENABLE_SECURITY_HEADERS=true
EV3_WEB_STATIC_ASSET_VERSION=cpanel-2026-05-22
```

### Como quedan las variables de sesion

Estas son las variables que controlan el comportamiento de sesion y concurrencia en hosting:

- `EV3_WEB_SECRET_KEY`: clave de firma de Flask. Debe ser larga, unica y privada.
- `EV3_WEB_SESSION_COOKIE_SECURE`: activa cookies solo por HTTPS. En hosting real debe quedar en `true`.
- `EV3_WEB_SESSION_IDLE_TIMEOUT_MIN`: minutos de inactividad antes de cerrar sesiones. Valor recomendado: `30` o `45`.
- `EV3_WEB_MAX_ACTIVE_SESSIONS`: cantidad maxima de sesiones web abiertas. Valor recomendado: `20` o `40` segun carga.
- `EV3_WEB_MAX_RUNNING_SIMULATIONS`: cantidad maxima de simulaciones corriendo al mismo tiempo. Valor recomendado: `8` o `12`.
- `EV3_WEB_SCRIPT_MAX_RUNTIME_S`: limite opcional de ejecucion por script. Si lo dejas en `0.0`, queda sin limite duro desde config.
- `EV3_WEB_SESSION_CLEANUP_INTERVAL_S`: intervalo de limpieza de sesiones inactivas.
- `EV3_WEB_ENABLE_SECURITY_HEADERS`: mantiene cabeceras de seguridad activas.

### Cookies de sesion que usa la app

La app tambien escribe estas cookies HTTP-only al crear una sesion:

- `ev3_owner_token`: token privado del propietario de la sesion.
- `ev3_session_id`: identificador de la sesion activa.

Estas cookies no se configuran manualmente en cPanel; las emite la aplicacion.

Compatibilidad temporal:

- Si en tu servidor todavia no migraste recursos, tambien funciona con:
  - `/home/ur5cxigur1qs/simuladorlego/Documentos/Ejemplos`
  - `/home/ur5cxigur1qs/simuladorlego/Documentos/Mundos`

Opcional (segun carga esperada):

```text
EV3_WEB_MAX_ACTIVE_SESSIONS=40
EV3_WEB_MAX_RUNNING_SIMULATIONS=12
EV3_WEB_SESSION_IDLE_TIMEOUT_MIN=45
```

## 10. Permisos de escritura (mundos)

La app guarda/carga mundos JSON. Verifica permisos de escritura en:

- `/home/ur5cxigur1qs/simuladorlego/worlds`

Ejemplo por SSH:

```bash
chmod -R 775 /home/ur5cxigur1qs/simuladorlego/worlds
```

Compatibilidad temporal:

- Si aun usas estructura legacy, ajusta permisos sobre `Documentos/Mundos`.

Si el servidor usa otro usuario de proceso, ajusta owner/group segun tu hosting.

## 11. Reiniciar y probar

1. En Setup Python App, pulsa **Restart**.
2. Abre `http://nyquist.app/simuladorlego`.
3. Prueba endpoints: `http://nyquist.app/simuladorlego/healthz`, `http://nyquist.app/simuladorlego/worlds`, `http://nyquist.app/simuladorlego/help`.

Validaciones minimas:

- La pagina principal carga.
- El editor de mundos carga.
- La ayuda carga.
- `healthz` responde con estado OK.

## 12. Actualizacion de version (deploy futuro)

1. Sube nueva version del codigo.
2. Activa el venv.
3. Reinstala paquete:

```bash
cd /home/ur5cxigur1qs/simuladorlego
source /home/ur5cxigur1qs/virtualenv/simuladorlego/3.11/bin/activate
pip install -e .
```

1. Incrementa `EV3_WEB_STATIC_ASSET_VERSION` para invalidar cache.
2. Restart en Setup Python App.

## 13. Problemas comunes

### Fallo al instalar por Python 3.10

- Sintoma comun: `Requires-Python >=3.11`.
- Solucion: en Setup Python App cambia la version a `3.11` y reinstala.

### Error 500 al abrir la app

- Revisa `wsgi.py` (import y nombre `app`, segun tu Entry point actual).
- Verifica que `simulador_ev3` exista en el app root.
- Reinstala dependencias en el venv de cPanel.

### `ModuleNotFoundError: simulador_ev3`

- Falta instalar el paquete en el venv o ruta no incluida en `sys.path`.
- Ejecuta `pip install -e .` y reinicia app.

### No cargan ejemplos o mundos

- Revisa `EV3_WEB_EXAMPLES_DIR` y `EV3_WEB_WORLDS_DIR`.
- Verifica permisos de lectura/escritura.

### Cambios de CSS/JS no se ven

- Actualiza `EV3_WEB_STATIC_ASSET_VERSION` y reinicia.
- Limpia cache del navegador.

## 14. Recomendaciones de operacion

- Mantener `SESSION_COOKIE_SECURE=true` en HTTPS.
- Usar una `SECRET_KEY` robusta y privada.
- No exponer rutas internas del servidor en la ayuda para usuario final.
- El usuario final debe navegar por menu interno de la app (Simulacion, Mundos, Ayuda).

## 14. Archivos listos para copiar

Esta guia se acompana de:

- `Documentos/wsgi_cpanel.py`: contenido exacto para copiar a `/home/ur5cxigur1qs/simuladorlego/wsgi.py`.
- `Documentos/CHECKLIST_POST_DEPLOY_CPANEL.md`: checklist de validacion final (home, worlds, help, healthz, carga de mundo y script).

---

Con esos dos archivos puedes ejecutar el deploy y validar paso a paso sin improvisar comandos.

