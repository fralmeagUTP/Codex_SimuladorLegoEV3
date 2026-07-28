/* Aplica snapshots de forma ordenada y descarta datos obsoletos. */
window.EV3SnapshotController = {
  create({ contractVersion, getState, setState, onUnsupportedVersion, render }) {
    return {
      apply(snapshot) {
        const version = Number(snapshot?.snapshot_version ?? contractVersion);
        if (Number.isFinite(version) && version !== contractVersion) {
          onUnsupportedVersion(version);
          return false;
        }
        const state = getState();
        const generation = Number(snapshot?.snapshot_generation ?? 0);
        const tick = Number(snapshot?.tick ?? -1);
        if (Number.isFinite(generation) && Number.isFinite(tick)) {
          const olderGeneration = generation < state.generation;
          const olderTick = generation === state.generation && tick < state.tick;
          if (olderGeneration || olderTick) return false;
          state.generation = generation;
          state.tick = tick;
        }
        state.snapshot = snapshot;
        state.receivedAtMs = Date.now();
        if (snapshot && Number.isFinite(Number(snapshot.sim_time_s))) state.simTimeS = Number(snapshot.sim_time_s);
        setState(state);
        render(snapshot);
        return true;
      },
    };
  },
};
