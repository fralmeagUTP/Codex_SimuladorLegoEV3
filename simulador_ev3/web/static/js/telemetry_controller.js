/* Renderiza telemetría sin conocer el ciclo de sesión ni el canvas. */
window.EV3TelemetryController = {
  create({ formatDistance, formatNumber, renderMotor, renderSensor }) {
    const telemetry = document.getElementById("telemetry");
    const motors = document.getElementById("motors");
    const sensors = document.getElementById("sensors");
    return {
      render(snapshot) {
        if (!snapshot) return;
        const robot = snapshot.robot || {};
        telemetry.innerHTML = `
          <dt>Tick</dt><dd>${snapshot.tick}</dd>
          <dt>Tiempo</dt><dd>${snapshot.sim_time_s}s</dd>
          <dt>X</dt><dd>${formatDistance(robot.x_mm, 1)} cm</dd>
          <dt>Y</dt><dd>${formatDistance(robot.y_mm, 1)} cm</dd>
          <dt>Theta</dt><dd>${formatNumber(robot.theta_deg)} °</dd>
          <dt>Colision</dt><dd>${snapshot.colliding ? "si" : "no"}</dd>
        `;
        const motorItems = snapshot.motors || [];
        motors.innerHTML = motorItems.length
          ? motorItems.map(renderMotor).join("")
          : '<p class="telemetry-empty">Sin motores</p>';
        const sensorItems = snapshot.sensors || [];
        sensors.innerHTML = sensorItems.length
          ? sensorItems.map(renderSensor).join("")
          : '<p class="telemetry-empty">Sin sensores</p>';
      },
    };
  },
};
