FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 EV3_APP_ENV=production
WORKDIR /app
RUN useradd --create-home --uid 10001 ev3
COPY pyproject.toml README.md ./
COPY simulador_ev3 ./simulador_ev3
RUN pip install --no-cache-dir .[web-prod]
USER ev3
EXPOSE 5050
CMD ["python", "-m", "simulador_ev3.web.waitress_server"]
