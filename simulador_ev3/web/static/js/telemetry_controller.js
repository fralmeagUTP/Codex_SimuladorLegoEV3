/* Renderiza el tablero de telemetría sin conocer el ciclo de sesión ni el canvas. */
window.EV3TelemetryController = {
  create({ formatDistance, formatNumber, renderMotor, renderSensor }) {
    const telemetry = document.getElementById("telemetry");
    const motorsAB = document.getElementById("motorsAB");
    const motorsCD = document.getElementById("motorsCD");
    const sensors = document.getElementById("sensors");
    const status = document.getElementById("telemetryStatus");
    const time = document.getElementById("telemetryTime");
    const tick = document.getElementById("telemetryTick");
    const collision = document.getElementById("telemetryCollision");

    function emptyMotor(port) {
      return `
        <article class="telemetry-card motor-card is-disconnected">
          <div class="telemetry-card-title"><span>Motor ${port}</span><span class="telemetry-state">Sin conectar</span></div>
          <div class="motor-metrics"><span><b>Vel.</b> -- °/s</span><span><b>Ángulo 0-360</b> -- °</span></div>
        </article>`;
    }

    function emptySensor(port) {
      return `
        <article class="telemetry-card is-disconnected">
          <div class="telemetry-card-title"><span>Sensor ${port}</span><span class="sensor-type">Sin conectar</span></div>
          <dl class="telemetry-mini-list"><dt>Tipo</dt><dd>--</dd><dt>Valor</dt><dd>--</dd></dl>
        </article>`;
    }

    function renderPort(port, itemsByPort, renderItem, renderEmpty) {
      const item = itemsByPort.get(port);
      return item ? renderItem(item) : renderEmpty(port);
    }

    return {
      render(snapshot) {
        if (!snapshot) return;
        const robot = snapshot.robot || {};
        telemetry.innerHTML = `
          <dt>X</dt><dd>${formatDistance(robot.x_mm, 1)} cm</dd>
          <dt>Y</dt><dd>${formatDistance(robot.y_mm, 1)} cm</dd>
          <dt>Theta</dt><dd>${formatNumber(robot.theta_deg)} °</dd>
          <dt>Colisión</dt><dd>${snapshot.colliding ? "Sí" : "No"}</dd>
        `;
        const motorsByPort = new Map((snapshot.motors || []).map((motor) => [motor.port, motor]));
        const sensorsByPort = new Map((snapshot.sensors || []).map((sensor) => [sensor.port, sensor]));
        motorsAB.innerHTML = ["A", "B"].map((port) => renderPort(port, motorsByPort, renderMotor, emptyMotor)).join("");
        motorsCD.innerHTML = ["C", "D"].map((port) => renderPort(port, motorsByPort, renderMotor, emptyMotor)).join("");
        sensors.innerHTML = ["S1", "S2", "S3", "S4"].map((port) => renderPort(port, sensorsByPort, renderSensor, emptySensor)).join("");
        status.textContent = snapshot.status || "ACTIVO";
        time.textContent = `${snapshot.sim_time_s}s`;
        tick.textContent = snapshot.tick;
        collision.textContent = snapshot.colliding ? "COLISIÓN" : "OK";
        collision.classList.toggle("is-alert", Boolean(snapshot.colliding));
      },
    };
  },
};
