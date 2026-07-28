/* Política de transporte para actualizaciones en vivo. */
window.EV3LiveUpdateController = {
  create({ sseEnabled, startStream, startPolling, stop }) {
    return {
      start() { if (sseEnabled) startStream(); else startPolling(); },
      fallback() { startPolling(); },
      stop,
    };
  },
};
