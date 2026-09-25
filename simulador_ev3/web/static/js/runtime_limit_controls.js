window.EV3RuntimeLimitControls = {
  bind(api, log) {
  const setActiveRuntimeLimit = (value) => {
    document.querySelectorAll("[data-runtime-limit]").forEach((button) => {
      const active = Number(button.dataset.runtimeLimit) === Number(value);
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
  };
  document.querySelectorAll("[data-runtime-limit]").forEach((button) => {
    button.addEventListener("click", async () => {
      const value = Number(button.dataset.runtimeLimit);
      try {
        const result = await api.setRuntimeLimit(value);
        setActiveRuntimeLimit(result.max_runtime_s ?? value);
        const label = value === 0 ? "sin limite" : `${value} s`;
        log(`Tiempo maximo configurado: ${label}.`);
      } catch (error) {
        log(`No se pudo configurar el tiempo maximo: ${error.message}`);
      }
    });
  });
  return { setActiveRuntimeLimit };
  },
};
