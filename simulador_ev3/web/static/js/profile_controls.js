window.EV3ProfileControls = {
  bind(api, log) {
    document.querySelectorAll("[data-simulation-profile]").forEach((button) => {
      button.addEventListener("click", async () => {
        try {
          const profile = button.dataset.simulationProfile;
          await api.setSimulationProfile(profile);
          log(`Perfil de simulacion aplicado: ${profile}.`);
        } catch (err) {
          log(`No se pudo cambiar el perfil: ${err.message}`);
        }
      });
    });
  },
};
