window.EV3RuntimeLimitControls = {
  bind(api, log) {
  document.querySelectorAll("[data-runtime-limit]").forEach((button) => {
    button.addEventListener("click", async () => {
      const value = Number(button.dataset.runtimeLimit);
      try {
        await api.setRuntimeLimit(value);
        const label = value === 0 ? "sin limite" : `${value} s`;
        log(`Tiempo maximo configurado: ${label}.`);
      } catch (error) {
        log(`No se pudo configurar el tiempo maximo: ${error.message}`);
      }
    });
  });
  },
};
