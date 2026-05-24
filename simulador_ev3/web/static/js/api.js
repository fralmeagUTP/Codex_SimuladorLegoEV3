window.EV3Api = (() => {
  let sessionId = null;
  let ownerToken = null;

  const rootData = document.documentElement?.dataset?.ev3BasePath || "";
  const basePath = rootData === "/" ? "" : rootData.replace(/\/+$/, "");

  function resolvePath(path) {
    if (!path) return basePath || "/";
    if (/^[a-zA-Z][a-zA-Z\d+\-.]*:/.test(path)) return path;
    if (path.startsWith("/")) return `${basePath}${path}`;
    return `${basePath}/${path}`;
  }

  async function request(path, options = {}) {
    const headers = Object.assign({}, options.headers || {});
    if (!(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }
    if (ownerToken) {
      headers["X-Session-Token"] = ownerToken;
    }
    const response = await fetch(resolvePath(path), Object.assign({}, options, { headers }));
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const message = data.error?.message || `HTTP ${response.status}`;
      const error = new Error(message);
      error.status = response.status;
      error.code = data.error?.code || null;
      throw error;
    }
    return data;
  }

  async function createSession(options = {}) {
    const data = await request("/api/sessions", {
      method: "POST",
      body: JSON.stringify({ reuse: Boolean(options.reuse) }),
    });
    sessionId = data.session_id;
    ownerToken = data.owner_token;
    return data;
  }

  async function closeSession() {
    if (!sessionId) return null;
    const closedSessionId = sessionId;
    try {
      return await request(`/api/sessions/${closedSessionId}`, {
        method: "DELETE",
        body: "{}",
      });
    } finally {
      if (sessionId === closedSessionId) {
        sessionId = null;
        ownerToken = null;
      }
    }
  }

  function closeSessionOnUnload() {
    if (!sessionId) return;
    fetch(resolvePath(`/api/sessions/${sessionId}`), {
      method: "DELETE",
      headers: Object.assign(
        { "Content-Type": "application/json" },
        ownerToken ? { "X-Session-Token": ownerToken } : {},
      ),
      body: "{}",
      keepalive: true,
    }).catch(() => {});
  }

  return {
    get sessionId() { return sessionId; },
    createSession,
    closeSession,
    closeSessionOnUnload,
    resolvePath,
    openSnapshotStream: (handlers = {}) => {
      if (!sessionId) throw new Error("No hay sesion activa.");
      const source = new EventSource(resolvePath(`/api/sessions/${sessionId}/stream`));
      const parse = (event) => JSON.parse(event.data || "{}");
      source.addEventListener("snapshot", (event) => handlers.snapshot?.(parse(event)));
      source.addEventListener("status", (event) => handlers.status?.(parse(event)));
      source.addEventListener("debug", (event) => handlers.debug?.(parse(event)));
      source.addEventListener("debug_state", (event) => handlers.debugState?.(parse(event)));
      source.addEventListener("debug_context", (event) => handlers.debugContext?.(parse(event)));
      source.addEventListener("error", (event) => {
        if (event.data) {
          handlers.error?.(parse(event));
        }
      });
      source.addEventListener("world", (event) => handlers.world?.(parse(event)));
      source.addEventListener("heartbeat", () => handlers.heartbeat?.());
      source.onerror = () => handlers.connectionError?.(source);
      return source;
    },
    loadScript: (source) => request(`/api/sessions/${sessionId}/script`, {
      method: "POST",
      body: JSON.stringify({ source }),
    }),
    start: (options = {}) => request(`/api/sessions/${sessionId}/start`, {
      method: "POST",
      body: JSON.stringify(options),
    }),
    pause: () => request(`/api/sessions/${sessionId}/pause`, { method: "POST", body: "{}" }),
    resume: () => request(`/api/sessions/${sessionId}/resume`, { method: "POST", body: "{}" }),
    stop: () => request(`/api/sessions/${sessionId}/stop`, { method: "POST", body: "{}" }),
    reset: () => request(`/api/sessions/${sessionId}/reset`, { method: "POST", body: "{}" }),
    setBreakpoints: (breakpoints) => request(`/api/sessions/${sessionId}/debug/breakpoints`, {
      method: "POST",
      body: JSON.stringify({ breakpoints }),
    }),
    setWatches: (watches) => request(`/api/sessions/${sessionId}/debug/watches`, {
      method: "POST",
      body: JSON.stringify({ watches }),
    }),
    debugStep: () => request(`/api/sessions/${sessionId}/debug/step`, {
      method: "POST",
      body: "{}",
    }),
    debugContinue: () => request(`/api/sessions/${sessionId}/debug/continue`, {
      method: "POST",
      body: "{}",
    }),
    snapshot: () => request(`/api/sessions/${sessionId}/snapshot`),
    listExamples: () => request("/api/examples"),
    getExample: (name) => request(`/api/examples/${encodeURIComponent(name)}`),
    listWorlds: () => request("/api/worlds"),
    loadWorld: (name) => request(`/api/sessions/${sessionId}/world`, {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
    loadBlankWorld: (payload = {}) => request(`/api/sessions/${sessionId}/world/blank`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    uploadWorldJson: (world) => request(`/api/sessions/${sessionId}/world/upload`, {
      method: "POST",
      body: JSON.stringify(world),
    }),
    uploadWorld: (file) => {
      const formData = new FormData();
      formData.append("file", file);
      return request(`/api/sessions/${sessionId}/world/upload`, {
        method: "POST",
        body: formData,
      });
    },
    setRobotStart: (payload) => request(`/api/sessions/${sessionId}/robot/start`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    getEditorAssets: () => request("/api/editor/assets"),
    createEditorWorld: (widthCells = 20, heightCells = 20) => request(`/api/sessions/${sessionId}/editor/world`, {
      method: "POST",
      body: JSON.stringify({ width_cells: widthCells, height_cells: heightCells }),
    }),
    importEditorWorld: (world) => request(`/api/sessions/${sessionId}/editor/world`, {
      method: "POST",
      body: JSON.stringify(world),
    }),
    getEditorWorld: () => request(`/api/sessions/${sessionId}/editor/world`),
    placeAsset: (payload) => request(`/api/sessions/${sessionId}/editor/world/place`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    rotateAsset: (payload) => request(`/api/sessions/${sessionId}/editor/world/rotate`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    updateAsset: (payload) => request(`/api/sessions/${sessionId}/editor/world/update`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    moveAsset: (payload) => request(`/api/sessions/${sessionId}/editor/world/move`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    duplicateAsset: (payload) => request(`/api/sessions/${sessionId}/editor/world/duplicate`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    removeAsset: (assetId) => request(`/api/sessions/${sessionId}/editor/world/placements/${encodeURIComponent(assetId)}`, {
      method: "DELETE",
    }),
    validateEditorWorld: () => request(`/api/sessions/${sessionId}/editor/world/validate`, {
      method: "POST",
      body: "{}",
    }),
    applyEditorWorld: () => request(`/api/sessions/${sessionId}/editor/world/apply-to-simulation`, {
      method: "POST",
      body: "{}",
    }),
    saveEditorWorld: (name) => request(`/api/sessions/${sessionId}/editor/world/save`, {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
  };
})();
