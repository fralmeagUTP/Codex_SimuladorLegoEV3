window.EV3ProfileControls = {
  bind(api, log) {
    const setActiveProfile = (profile) => {
      document.querySelectorAll("[data-simulation-profile]").forEach((button) => {
        const active = button.dataset.simulationProfile === profile;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-pressed", active ? "true" : "false");
      });
    };
    document.querySelectorAll("[data-simulation-profile]").forEach((button) => {
      button.addEventListener("click", async () => {
        try {
          const profile = button.dataset.simulationProfile;
          const result = await api.setSimulationProfile(profile);
          setActiveProfile(result.profile || profile);
          log(`Perfil de simulacion aplicado: ${profile}.`);
        } catch (err) {
          log(`No se pudo cambiar el perfil: ${err.message}`);
        }
      });
    });
    return { setActiveProfile };
  },
};
