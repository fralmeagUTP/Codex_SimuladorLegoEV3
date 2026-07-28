/* Controlador de comandos de sesión, independiente de la representación DOM. */
window.EV3SessionController = {
  create({ api, onStatus, onError, beforeStart, afterStart, onDebug, onBreakpoints }) {
    async function invoke(action) {
      try {
        return await action();
      } catch (error) {
        onError(error);
        return null;
      }
    }

    return {
      async run(source) {
        return invoke(async () => {
          beforeStart();
          await api.loadScript(source);
          const result = await api.start();
          onStatus(result.status);
          await afterStart();
          return result;
        });
      },
      async pause() {
        return invoke(async () => {
          const result = await api.pause();
          onStatus(result.status);
          return result;
        });
      },
      async resume() {
        return invoke(async () => {
          const result = await api.resume();
          onStatus(result.status);
          return result;
        });
      },
      async debugContinue() {
        return invoke(async () => {
          const result = await api.debugContinue();
          onDebug(result);
          return result;
        });
      },
      async debugStart({ source, breakpoints, watches, stepMode = false }) {
        return invoke(async () => {
          beforeStart();
          await api.loadScript(source);
          const breakpointResult = await api.setBreakpoints(breakpoints);
          await api.setWatches(watches);
          onBreakpoints(breakpointResult.breakpoints);
          const result = await api.start({ debug: true, step_mode: stepMode });
          onStatus(result.status);
          await afterStart();
          return result;
        });
      },
      async debugStep({ source, breakpoints, watches, active }) {
        if (active) {
          return invoke(async () => {
            const result = await api.debugStep();
            onDebug(result);
            return result;
          });
        }
        return this.debugStart({ source, breakpoints, watches, stepMode: true });
      },
    };
  },
};
