window.EV3Api = (() => {
  let sessionId = null;
  let ownerToken = null;
  let sessionRecoveryPromise = null;
  let lastWorkerInfo = null;
  const inFlightByKey = new Map();
  const MAX_SESSION_RECOVERY_ATTEMPTS = 4;
  const TRANSIENT_HTTP_STATUS = new Set([408, 425, 429, 500, 502, 503, 504]);

  const rootData = document.documentElement?.dataset?.ev3BasePath || "";
  const basePath = rootData === "/" ? "" : rootData.replace(/\/+$/, "");

  function resolvePath(path) {
    if (!path) return basePath || "/";
    if (/^[a-zA-Z][a-zA-Z\d+\-.]*:/.test(path)) return path;
    if (path.startsWith("/")) return `${basePath}${path}`;
    return `${basePath}/${path}`;
  }

  function withSessionPath(path, newSessionId) {
    if (!path || !newSessionId) return path;
    return path.replace(/^\/api\/sessions\/[^/]+/i, `/api/sessions/${newSessionId}`);
  }

  async function rawRequest(path, options = {}) {
    const headers = Object.assign({}, options.headers || {});
    if (!(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }
    if (ownerToken) {
      headers["X-Session-Token"] = ownerToken;
    }
    const response = await fetch(resolvePath(path), Object.assign({}, options, { headers }));
    const workerId = response.headers.get("X-Worker-Id");
    const workerPid = response.headers.get("X-Worker-Pid");
    if (workerId || workerPid) {
      lastWorkerInfo = { workerId: workerId || null, workerPid: workerPid || null };
    }
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const message = data.error?.message || `HTTP ${response.status}`;
      const error = new Error(message);
      error.status = response.status;
      error.code = data.error?.code || null;
      error.workerId = workerId || null;
      error.workerPid = workerPid || null;
      if (error.workerId || error.workerPid) {
        const workerLabel = [
          error.workerId ? `worker=${error.workerId}` : null,
          error.workerPid ? `pid=${error.workerPid}` : null,
        ].filter(Boolean).join(", ");
        error.message = `${message} [${workerLabel}]`;
      }
      throw error;
    }
    return data;
  }

  async function recoverSession() {
    if (sessionRecoveryPromise) return sessionRecoveryPromise;
    sessionRecoveryPromise = (async () => {
      const data = await rawRequest("/api/sessions", {
        method: "POST",
        body: JSON.stringify({ reuse: true }),
      });
      sessionId = data.session_id;
      ownerToken = data.owner_token;
      if (typeof window !== "undefined" && window.dispatchEvent) {
        window.dispatchEvent(
          new CustomEvent("ev3-session-recovered", {
            detail: {
              sessionId,
              worker: lastWorkerInfo,
            },
          }),
        );
      }
      return data;
    })();
    try {
      return await sessionRecoveryPromise;
    } finally {
      sessionRecoveryPromise = null;
    }
  }

  async function request(path, options = {}) {
    let requestPath = path;
    let lastError = null;
    for (let attempt = 0; attempt <= MAX_SESSION_RECOVERY_ATTEMPTS; attempt += 1) {
      try {
        return await rawRequest(requestPath, options);
      } catch (error) {
        lastError = error;
        const canRecover = error?.status === 404 && error?.code === "SESSION_NOT_FOUND";
        if (!canRecover || attempt >= MAX_SESSION_RECOVERY_ATTEMPTS) break;
        const recovered = await recoverSession();
        requestPath = withSessionPath(path, recovered?.session_id || sessionId);
      }
    }
    throw lastError;
  }

  function isTransientError(error) {
    if (!error) return false;
    if (TRANSIENT_HTTP_STATUS.has(Number(error.status))) return true;
    if (error.name === "TypeError") return true; // fetch network failure
    const code = String(error.code || "").toUpperCase();
    if (code.includes("NETWORK") || code.includes("TIMEOUT")) return true;
    const msg = String(error.message || "").toLowerCase();
    return msg.includes("http2") || msg.includes("networkerror");
  }

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async function requestWithPolicy(path, options = {}, policy = {}) {
    const retries = Number.isFinite(policy.retries) ? Number(policy.retries) : 0;
    const baseDelayMs = Number.isFinite(policy.baseDelayMs) ? Number(policy.baseDelayMs) : 120;
    for (let attempt = 0; attempt <= retries; attempt += 1) {
      try {
        return await request(path, options);
      } catch (error) {
        if (!isTransientError(error) || attempt >= retries) {
          throw error;
        }
        const delayMs = Math.min(1600, baseDelayMs * (2 ** attempt));
        await sleep(delayMs);
      }
    }
    throw new Error("No se pudo completar la solicitud.");
  }

  function randomRequestId() {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
      return crypto.randomUUID();
    }
    return `req-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  function singleFlight(key, factory) {
    const normalized = String(key || "").trim();
    if (!normalized) {
      return factory();
    }
    const existing = inFlightByKey.get(normalized);
    if (existing) {
      return existing;
    }
    const promise = Promise.resolve()
      .then(factory)
      .finally(() => {
        if (inFlightByKey.get(normalized) === promise) {
          inFlightByKey.delete(normalized);
        }
      });
    inFlightByKey.set(normalized, promise);
    return promise;
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
    get lastWorkerInfo() { return lastWorkerInfo; },
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
    loadScript: (source) => singleFlight(
      `script:${sessionId}`,
      () => requestWithPolicy(`/api/sessions/${sessionId}/script`, {
        method: "POST",
        body: JSON.stringify({ source }),
      }, { retries: 2, baseDelayMs: 120 }),
    ),
    start: (options = {}) => singleFlight(
      `start:${sessionId}`,
      () => requestWithPolicy(`/api/sessions/${sessionId}/start`, {
        method: "POST",
        body: JSON.stringify(Object.assign({}, options, { request_id: randomRequestId() })),
      }, { retries: 2, baseDelayMs: 160 }),
    ),
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
    snapshot: () => singleFlight(
      `snapshot:${sessionId}`,
      () => requestWithPolicy(`/api/sessions/${sessionId}/snapshot`, {
        method: "POST",
        body: "{}",
      }, { retries: 2, baseDelayMs: 100 }),
    ),
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
