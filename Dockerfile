FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 EV3_WEB_APP_ENV=production EV3_WEB_HOST=0.0.0.0 \
    TMPDIR=/tmp/ev3 EV3_WORKER_TEMP_ROOT=/tmp/ev3/workers
WORKDIR /app
RUN useradd --create-home --uid 10001 ev3
COPY pyproject.toml README.md ./
COPY simulador_ev3 ./simulador_ev3
# Los catálogos se resuelven junto al código en ejecución.  Deben formar
# parte de la imagen; de lo contrario los menús de mundos, ejemplos y
# escenarios quedan vacíos únicamente en producción.
COPY examples ./examples
COPY worlds ./worlds
RUN pip install --no-cache-dir .[web-prod]
USER ev3
EXPOSE 5050
CMD ["python", "-m", "simulador_ev3.web.waitress_server"]
