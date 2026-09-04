window.EV3TraceControls = {
  bind(api, log, refreshSnapshot) {
    document.querySelectorAll("[data-trace-action]").forEach((button) => {
      button.addEventListener("click", async () => {
        const action = button.dataset.traceAction;
        try {
          if (action === "start") { await api.startTrace(); log("Registro de traza iniciado."); }
          else if (action === "stop") { await api.stopTrace(); log("Registro de traza detenido."); }
          else if (action === "step") {
            const before = Number(document.getElementById("telemetryTick")?.textContent);
            const snapshot = await api.stepTick();
            await refreshSnapshot();
            const after = Number(snapshot?.tick);
            if (Number.isFinite(before) && Number.isFinite(after) && after > before) {
              log("Se avanzo un tick de simulacion.");
            } else {
              log("No se avanzo el tick de simulacion.");
            }
          }
          else window.open(api.traceUrl(action), "_blank", "noopener");
        } catch (err) { log(`No se pudo gestionar la traza: ${err.message}`); }
      });
    });
  },
};
