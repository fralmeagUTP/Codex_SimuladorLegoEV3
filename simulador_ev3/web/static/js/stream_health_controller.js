/* Vigila la salud de la actualización en vivo sin depender de la interfaz. */
window.EV3StreamHealthController = {
  create({ intervalMs = 1000, shouldCheck, onStale }) {
    let timer = null;
    return {
      start() {
        if (timer) return;
        timer = setInterval(() => { if (shouldCheck()) onStale(); }, intervalMs);
      },
      stop() {
        if (!timer) return;
        clearInterval(timer);
        timer = null;
      },
      get running() { return timer !== null; },
    };
  },
};
