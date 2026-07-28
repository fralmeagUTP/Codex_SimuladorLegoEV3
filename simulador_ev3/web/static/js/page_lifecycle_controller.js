/* Centraliza la limpieza y recuperación del ciclo de vida de la página. */
window.EV3PageLifecycleController = {
  bind({ stopLiveUpdates, closeSession, recoverLiveState, onRecoveryError }) {
    const close = () => { stopLiveUpdates(); closeSession(); };
    window.addEventListener("pagehide", close);
    window.addEventListener("beforeunload", close);
    window.addEventListener("ev3-session-recovered", async () => {
      try {
        await recoverLiveState();
      } catch {
        onRecoveryError();
      }
    });
  },
};
