# Checklist post-deploy cPanel (nyquist.app/simuladorlego)

Usa este checklist despues de publicar en cPanel.

## 1. Configuracion en cPanel

- [ ] Python App creada/actualizada.
- [ ] Python version en 3.11+.
- [ ] Application root: `simuladorlego`.
- [ ] Application URL: `nyquist.app/simuladorlego`.
- [ ] Startup file: `wsgi.py`.
- [ ] Entry point: `app`.
- [ ] Boton Restart ejecutado.

## 2. Dependencias y entorno

- [ ] Entorno virtual activado correctamente.
- [ ] `pip install -e .` ejecutado sin errores.
- [ ] Variables EV3_WEB configuradas (`SECRET_KEY`, `WORLDS_DIR`, `EXAMPLES_DIR`, `IMAGE_ASSETS_DIR`).
- [ ] Permisos de escritura en `Documentos/Mundos`.

## 3. Validacion funcional web

Abrir y validar:

- [ ] `http://nyquist.app/simuladorlego`
- [ ] `http://nyquist.app/simuladorlego/worlds`
- [ ] `http://nyquist.app/simuladorlego/help`
- [ ] `http://nyquist.app/simuladorlego/healthz` responde OK

## 4. Flujo minimo de usuario final

- [ ] En **Mundos**, crear un mundo simple.
- [ ] Pulsar **Validar** sin errores bloqueantes.
- [ ] Pulsar **Guardar como** y exportar JSON.
- [ ] Ir a **Simulacion** por menu superior.
- [ ] Cargar un ejemplo y ejecutar script.
- [ ] Ver telemetria y estado del robot.

## 5. Problemas rapidos

Si algo falla:

- [ ] Revisar log Passenger: `/home/ur5cxigur1qs/logs/simuladorlego_passenger.log`.
- [ ] Confirmar que `wsgi.py` existe en app root y exporta `app`.
- [ ] Confirmar Python 3.11+ (si 3.10, corregir version en cPanel).
- [ ] Reinstalar dependencias y reiniciar app.

## 6. Cierre

- [ ] Navegacion por menu funciona sin escribir rutas manuales.
- [ ] Ayuda muestra URL publicada (`nyquist.app/simuladorlego`) y flujo para usuario final.
