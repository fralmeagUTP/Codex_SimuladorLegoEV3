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

La carpeta de codigo debe conservar la estructura del repo (incluyendo `simulador_ev3/`, `Documentos/`, `pyproject.toml`).

## 4. Subir el proyecto

### Opcion A: File Manager (ZIP)

1. Comprime el proyecto local en un `.zip`.
2. En cPanel -> **File Manager**, sube el ZIP a `/home/ur5cxigur1qs/simuladorlego`.
3. Extrae el contenido.
4. Verifica que exista:
   - `pyproject.toml`
   - `simulador_ev3/web/wsgi.py`
   - `Documentos/Ejemplos`
   - `Documentos/Mundos`

### Opcion B: Git (si esta disponible)

1. Clona el repo dentro de `/home/ur5cxigur1qs/simuladorlego`.
2. Verifica la rama/version deseada.

## 5. Crear/ajustar la aplicacion Python en cPanel

En cPanel -> **Setup Python App** -> edita la app `NYQUIST.APP/SIMULADORLEGO`:

- Python version: `3.11` (o superior)
- Application root: `simuladorlego`
- Application URL: `simuladorlego` (ruta)
- Application startup file: `wsgi.py`
- Application Entry point: `app`

Guarda la app.

## 6. Instalar dependencias

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

## 7. Crear `wsgi.py` en la raiz del app root

Como en tu cPanel el startup file es `wsgi.py`, crea este archivo en:

- `/home/ur5cxigur1qs/simuladorlego/wsgi.py`

Contenido recomendado:

```python
import os
import sys

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from simulador_ev3.web.app import create_app

app = create_app()
```

Notas:

- En tu configuracion actual el Entry point es `app`, por eso el objeto debe llamarse `app`.
- Si cambias el nombre del objeto, cambia tambien el Entry point en cPanel.

## 8. Variables de entorno recomendadas en cPanel

En **Setup Python App** -> **Environment Variables**, agrega:

```text
EV3_WEB_SECRET_KEY=<una-clave-larga-y-unica>
EV3_WEB_SESSION_COOKIE_SECURE=true
EV3_WEB_EXAMPLES_DIR=/home/ur5cxigur1qs/simuladorlego/Documentos/Ejemplos
EV3_WEB_WORLDS_DIR=/home/ur5cxigur1qs/simuladorlego/Documentos/Mundos
EV3_WEB_IMAGE_ASSETS_DIR=/home/ur5cxigur1qs/simuladorlego/simulador_ev3/images
EV3_WEB_ENABLE_SECURITY_HEADERS=true
EV3_WEB_STATIC_ASSET_VERSION=cpanel-2026-05-22
```

Opcional (segun carga esperada):

```text
EV3_WEB_MAX_ACTIVE_SESSIONS=40
EV3_WEB_MAX_RUNNING_SIMULATIONS=12
EV3_WEB_SESSION_IDLE_TIMEOUT_MIN=45
```

## 9. Permisos de escritura (mundos)

La app guarda/carga mundos JSON. Verifica permisos de escritura en:

- `/home/ur5cxigur1qs/simuladorlego/Documentos/Mundos`

Ejemplo por SSH:

```bash
chmod -R 775 /home/ur5cxigur1qs/simuladorlego/Documentos/Mundos
```

Si el servidor usa otro usuario de proceso, ajusta owner/group segun tu hosting.

## 10. Reiniciar y probar

1. En Setup Python App, pulsa **Restart**.
2. Abre:
   - `http://nyquist.app/simuladorlego`
3. Prueba endpoints:
   - `http://nyquist.app/simuladorlego/healthz`
   - `http://nyquist.app/simuladorlego/worlds`
   - `http://nyquist.app/simuladorlego/help`

Validaciones minimas:

- La pagina principal carga.
- El editor de mundos carga.
- La ayuda carga.
- `healthz` responde con estado OK.

## 11. Actualizacion de version (deploy futuro)

1. Sube nueva version del codigo.
2. Activa el venv.
3. Reinstala paquete:

```bash
cd /home/ur5cxigur1qs/simuladorlego
source /home/ur5cxigur1qs/virtualenv/simuladorlego/3.11/bin/activate
pip install -e .
```

4. Incrementa `EV3_WEB_STATIC_ASSET_VERSION` para invalidar cache.
5. Restart en Setup Python App.

## 12. Problemas comunes

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

## 13. Recomendaciones de operacion

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
