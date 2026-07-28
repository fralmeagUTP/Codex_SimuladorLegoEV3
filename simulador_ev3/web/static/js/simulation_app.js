(async () => {
  const api = window.EV3Api;
  const canvas = document.getElementById("worldCanvas");
  const codeEditor = document.getElementById("codeEditor");
  const codeEditorShell = codeEditor?.closest(".code-editor-shell");
  const editorGutter = document.getElementById("editorGutter");
  const syntaxHighlight = document.getElementById("syntaxHighlight");
  const autocompletePopup = document.getElementById("autocompletePopup");
  const statusEl = document.getElementById("sessionStatus");
  const consoleEl = document.getElementById("console");
  const statusWorld = document.getElementById("statusWorld");
  let statusProgram = document.getElementById("statusProgram");
  const statusSavePath = document.getElementById("statusSavePath");
  const examplesMenu = document.getElementById("examplesMenu");
  const missionsMenu = document.getElementById("missionsMenu");
  const missionResultEl = document.getElementById("missionResult");
  const worldsMenu = document.getElementById("worldsMenu");
  const scriptFileInput = document.getElementById("scriptFileInput");
  const worldFileInput = document.getElementById("worldFileInput");
  const placeRobotStartBtn = document.getElementById("placeRobotStartBtn");
  const robotThetaInput = document.getElementById("robotThetaInput");
  const robotStartReadout = document.getElementById("robotStartReadout");
  const breakpointsInput = document.getElementById("breakpointsInput");
  const watchesInput = document.getElementById("watchesInput");
  const debugState = document.getElementById("debugState");
  const debugWatchesPanel = document.getElementById("debugWatchesPanel");
  const debugWatchesBody = document.getElementById("debugWatchesBody");
  const debugWatchesEmpty = document.getElementById("debugWatchesEmpty");
  const runBtn = document.getElementById("runBtn");
  const stopBtn = document.getElementById("stopBtn");
  const pauseBtn = document.getElementById("pauseBtn");
  const resumeBtn = document.getElementById("resumeBtn");
  const debugRunBtn = document.getElementById("debugRunBtn");
  const debugStepBtn = document.getElementById("debugStepBtn");
  const debugContinueBtn = document.getElementById("debugContinueBtn");
  const executionSuccessToast = document.getElementById("executionSuccessToast");
  const executionSuccessToastClose = document.getElementById("executionSuccessToastClose");
  const mapZoomInBtn = document.getElementById("mapZoomInBtn");
  const mapZoomOutBtn = document.getElementById("mapZoomOutBtn");
  const mapZoomResetBtn = document.getElementById("mapZoomResetBtn");
  const toggleSensorBeamsBtn = document.getElementById("toggleSensorBeamsBtn");
  const aboutMenuBtn = document.getElementById("aboutMenuBtn");
  const APP_VERSION = document?.documentElement?.dataset?.ev3AppVersion || "desconocida";
  const ABOUT_MESSAGE =
    "Simulador LEGO Mindstorms EV3 basado en la libreria Pybricks\n"
    + `Version ${APP_VERSION}\n\n`
    + "Desarrollado por:\n"
    + "\t\tFrancisco Alejandro Medina Aguirre\n"
    + "\t\tJimy Alexander Cortés Osorio\n\n"
    + "Aliados academicos:\n"
    + "\t- Grupo Nyquist\n"
    + "\t- Robotica Aplicada\n"
    + "\t- Universidad Tecnologica de Pereira (UTP)\n";

  const sessionController = window.EV3SessionController.create({
    api,
    onStatus: setStatus,
    onError: (err) => log(err.message),
    beforeStart: () => {
      beginExecutionNotificationCycle();
      clearDebugState();
      hideRobotStartMarker();
      executionMenuLocked = true;
      updateMenuLockState();
    },
    afterStart: forceStateRefreshAfterStart,
    onDebug: handleDebug,
    onBreakpoints: (breakpoints) => setDebugState(`breakpoints: ${breakpoints.join(", ") || "ninguno"}`),
  });

  const streamHealthController = window.EV3StreamHealthController.create({
    shouldCheck: () => {
      if (recoveringSession || autoResetInProgress || currentStatus !== "running") return false;
      const staleMs = Date.now() - lastSnapshotAtMs;
      return lastSnapshotAtMs === 0 || staleMs >= SNAPSHOT_STALE_MS;
    },
    onStale: () => {
      if (!usingPollingFallback) startPollingFallback();
      void refreshSnapshot();
    },
  });
  const snapshotController = window.EV3SnapshotController.create({
    contractVersion: 1,
    getState: () => ({
      generation: latestSnapshotGeneration, tick: latestSnapshotTick, snapshot: latestSnapshot,
      receivedAtMs: lastSnapshotAtMs, simTimeS: lastSimTimeS,
    }),
    setState: (state) => {
      latestSnapshotGeneration = state.generation;
      latestSnapshotTick = state.tick;
      latestSnapshot = state.snapshot;
      lastSnapshotAtMs = state.receivedAtMs;
      lastSimTimeS = state.simTimeS;
    },
    onUnsupportedVersion: (version) => log(`Version de snapshot no soportada: ${version}`),
    render: (snapshot) => {
      updateExecutionIndicator();
      updateTelemetry(snapshot);
      updateBrick(snapshot);
      redrawCanvas();
    },
  });
  const telemetryController = window.EV3TelemetryController.create({
    formatDistance: formatDistanceCm,
    formatNumber: formatTelemetryNumber,
    renderMotor: renderMotorTelemetry,
    renderSensor: renderSensorTelemetry,
  });
  const worldViewController = window.EV3WorldViewController.create({
    canvas,
    getViewState: () => ({
      snapshot: latestSnapshot,
      world: currentWorld,
      robotStart: robotStartMode ? robotStartPreview : (showRobotStartMarker ? robotStart : null),
      showSensorBeams,
    }),
  });

  if (!statusProgram) {
    const editorShell = document.querySelector(".code-editor-shell");
    const strip = document.createElement("div");
    strip.className = "program-name-strip";
    strip.innerHTML = 'Programa actual: <span id="statusProgram">editor_actual.py</span>';
    if (editorShell?.parentElement) {
      editorShell.parentElement.insertBefore(strip, consoleEl || null);
      statusProgram = strip.querySelector("#statusProgram");
    }
  }
  const defaultScript = codeEditor.value;
  const scenarios = {
    line: {
      label: "Seguidor de linea",
      world: "01_linea_negra_basica.json",
      example: "11_siguelineas_basico.py",
    },
    ultrasonic: {
      label: "Ultrasonido + obstaculos",
      world: "05_obstaculos_baliza_ir.json",
      example: "15_esquiva_obstaculos.py",
    },
    brick: {
      label: "Test pantalla/altavoz",
      world: "05_obstaculos_baliza_ir.json",
      example: "02_intro_pantalla_altavoz.py",
    },
    radar: {
      label: "Radar 360 ultrasonido",
      world: "12_radar_ultrasonido_360.json",
      example: "23_radar_ultrasonido_5grados.py",
    },
  };
  const autocompleteWords = [
    "EV3Brick", "Motor", "ColorSensor", "UltrasonicSensor", "TouchSensor",
    "GyroSensor", "DriveBase", "Port", "Color", "Direction", "Stop", "Button",
    "wait", "run", "run_time", "run_angle", "dc", "hold", "brake", "stop",
    "angle", "speed", "drive", "turn", "straight", "distance", "state",
    "reflection", "rgb", "pressed", "beep", "screen", "clear", "print",
    "from", "import", "def", "class", "return", "if", "else", "elif", "for",
    "while", "in", "not", "and", "or", "True", "False", "None", "try",
    "except", "finally", "raise", "with", "as", "pass", "break", "continue",
    "print", "len", "range", "str", "int", "float", "list", "dict", "set",
    "tuple", "type",
  ];
  const contextHints = {
    EV3Brick: ["screen", "speaker", "light", "buttons"],
    Port: ["A", "B", "C", "D", "S1", "S2", "S3", "S4"],
    Color: ["BLACK", "BLUE", "BROWN", "CYAN", "GREEN", "ORANGE", "PURPLE", "RED", "WHITE", "YELLOW"],
    Stop: ["BRAKE", "COAST", "HOLD"],
    Direction: ["CLOCKWISE", "COUNTERCLOCKWISE"],
    Button: ["LEFT", "RIGHT", "UP", "DOWN", "CENTER"],
    Motor: ["run", "run_time", "run_angle", "dc", "hold", "brake", "stop", "angle", "speed"],
    DriveBase: ["drive", "stop", "straight", "turn", "distance", "state"],
    ColorSensor: ["reflection", "rgb", "color"],
    UltrasonicSensor: ["distance", "presence"],
    TouchSensor: ["pressed"],
    GyroSensor: ["angle", "speed", "reset_angle"],
    Screen: ["clear", "print"],
    Speaker: ["beep"],
    Light: ["on", "off"],
  };
  const attrTypeHints = {
    "EV3Brick.screen": "Screen",
    "EV3Brick.speaker": "Speaker",
    "EV3Brick.light": "Light",
  };
  const syntaxKeywords = new Set([
    "from", "import", "def", "class", "return", "if", "else", "elif", "for",
    "while", "in", "not", "and", "or", "True", "False", "None", "try",
    "except", "finally", "raise", "with", "as", "pass", "break", "continue",
    "lambda",
  ]);
  const syntaxLiteralKeywords = new Set(["True", "False", "None"]);
  const syntaxBuiltins = new Set([
    "print", "len", "range", "str", "int", "float", "list", "dict", "set",
    "tuple", "type", "EV3Brick", "Motor", "ColorSensor", "UltrasonicSensor",
    "TouchSensor", "GyroSensor", "DriveBase", "Port", "Color", "wait",
  ]);
  let currentWorld = null;
  let currentStatus = "created";
  let gutterBreakpoints = new Set();
  let watchExpressions = [];
  let currentDebugLine = null;
  let debugPaused = false;
  let currentDebugState = null;
  let currentDebugContext = null;
  let robotStartMode = false;
  let robotStart = null;
  let robotStartPreview = null;
  let showRobotStartMarker = false;
  let latestSnapshot = null;
  let latestSnapshotGeneration = -1;
  let latestSnapshotTick = -1;
  let timer = null;
  let stream = null;
  let streamBootstrapTimeout = null;
  let streamRetryTimer = null;
  let usingPollingFallback = false;
  let recoveringSession = false;
  let autoResetInProgress = false;
  let suppressStoppedAutoReset = false;
  let snapshotRequestInFlight = false;
  let recoveryFailures = 0;
  let autocompleteItems = [];
  let autocompleteSelected = 0;
  let loadedWorldNames = new Set();
  let selectedWorldName = null;
  let selectedBlankWorld = false;
  let currentScriptName = "editor_actual.py";
  const ACTIVE_EXECUTION_STATUSES = new Set(["running", "paused"]);
  let executionMenuLocked = false;
  let nextExecutionNotificationId = 0;
  let activeExecutionNotificationId = null;
  let notifiedExecutionNotificationId = null;
  let executionSuccessToastTimer = null;
  const initialSensorBeamsFlag =
    String(document?.documentElement?.dataset?.ev3SensorBeamsEnabled || "true").toLowerCase() !== "false";
  let showSensorBeams = initialSensorBeamsFlag;
  const STREAM_BOOTSTRAP_TIMEOUT_MS = 2500;
  const configuredPollingIntervalMs = Number.parseInt(
    document?.documentElement?.dataset?.ev3PollingIntervalMs || "900",
    10,
  );
  const POLLING_INTERVAL_MS = Number.isFinite(configuredPollingIntervalMs)
    ? Math.max(250, configuredPollingIntervalMs)
    : 900;
  const STREAM_RETRY_DELAY_MS = 5000;
  const SNAPSHOT_STALE_MS = 3000;
  const SNAPSHOT_CONTRACT_VERSION = 1;
  const SSE_ENABLED =
    String(document?.documentElement?.dataset?.ev3SseEnabled || "true").toLowerCase() !== "false";
  const AUTO_RESET_ON_FINISH = true;
  let lastSimTimeS = 0;
  let lastSnapshotAtMs = 0;
  const MENU_LOCK_MESSAGE = "Opciones de menu bloqueadas durante la ejecucion. Usa 'Detener y reiniciar' para habilitarlas.";
  const liveUpdateController = window.EV3LiveUpdateController.create({
    sseEnabled: SSE_ENABLED,
    startStream: startSnapshotStream,
    startPolling: startPollingFallback,
    stop: stopLiveUpdates,
  });

  function log(message) {
    consoleEl.textContent = message || "";
  }

  const aboutDialogController = window.EV3AboutDialog.create(ABOUT_MESSAGE);

  function setScriptName(name) {
    if (!name) return;
    currentScriptName = name;
    if (statusProgram) statusProgram.textContent = currentScriptName;
  }

  function setSavePath(text) {
    if (statusSavePath) statusSavePath.textContent = text || "sin guardar";
  }

  function setStatus(status) {
    currentStatus = status || currentStatus;
    statusEl.textContent = status;
    const resetDebugVisuals = ["created", "ready", "stopped", "finished", "timed_out", "error"].includes(currentStatus);
    executionMenuLocked = isExecutionActive(currentStatus);
    if (resetDebugVisuals) {
      debugPaused = false;
      currentDebugState = null;
      currentDebugContext = null;
      currentDebugLine = null;
      renderEditorGutter();
      renderDebugWatches();
    }
    if (currentStatus === "running") {
      suppressStoppedAutoReset = false;
    }
    if (currentStatus === "finished") {
      scheduleExecutionSuccessNotification();
    } else if (["stopped", "timed_out", "error", "created"].includes(currentStatus)) {
      invalidateExecutionNotificationCycle();
    }
    updateControlStates();
  }

  function beginExecutionNotificationCycle() {
    nextExecutionNotificationId += 1;
    activeExecutionNotificationId = nextExecutionNotificationId;
    hideExecutionSuccessToast();
  }

  function invalidateExecutionNotificationCycle() {
    activeExecutionNotificationId = null;
    hideExecutionSuccessToast();
  }

  function hideExecutionSuccessToast() {
    if (executionSuccessToastTimer) {
      clearTimeout(executionSuccessToastTimer);
      executionSuccessToastTimer = null;
    }
    if (executionSuccessToast) executionSuccessToast.hidden = true;
  }

  function showExecutionSuccessToast() {
    if (!executionSuccessToast) return;
    executionSuccessToast.hidden = false;
    executionSuccessToastTimer = setTimeout(hideExecutionSuccessToast, 4000);
  }

  function scheduleExecutionSuccessNotification() {
    const executionId = activeExecutionNotificationId;
    if (!executionId || notifiedExecutionNotificationId === executionId) return;
    // La cola de eventos publica primero el snapshot final. requestAnimationFrame
    // también cubre el sondeo, cuyo mismo ciclo renderiza el snapshot tras el estado.
    requestAnimationFrame(() => {
      if (currentStatus !== "finished" || activeExecutionNotificationId !== executionId) return;
      notifiedExecutionNotificationId = executionId;
      activeExecutionNotificationId = null;
      showExecutionSuccessToast();
    });
  }

  function updateExecutionIndicator() {
    if (!statusEl) return;
    if (currentStatus === "running") {
      const anim = [".", "..", "..."][Math.floor((Date.now() / 450) % 3)];
      statusEl.textContent = `running${anim} t=${lastSimTimeS.toFixed(2)}s`;
      return;
    }
    if (currentStatus === "paused") {
      statusEl.textContent = `paused t=${lastSimTimeS.toFixed(2)}s`;
      return;
    }
    statusEl.textContent = currentStatus;
  }

  function isExecutionActive(status) {
    return ACTIVE_EXECUTION_STATUSES.has(status);
  }

  function setMenuActionState(element, disabled) {
    if (!element) return;
    if ("disabled" in element) {
      element.disabled = disabled;
    }
    if (disabled) {
      element.setAttribute("aria-disabled", "true");
      element.classList.add("is-disabled");
      if (element.tagName === "A") {
        element.dataset.prevTabIndex = element.getAttribute("tabindex") ?? "";
        element.setAttribute("tabindex", "-1");
      }
    } else {
      element.removeAttribute("aria-disabled");
      element.classList.remove("is-disabled");
      if (element.tagName === "A" && "prevTabIndex" in element.dataset) {
        const prev = element.dataset.prevTabIndex;
        if (prev) {
          element.setAttribute("tabindex", prev);
        } else {
          element.removeAttribute("tabindex");
        }
        delete element.dataset.prevTabIndex;
      }
    }
  }

  function updateMenuLockState() {
    const locked = executionMenuLocked;
    for (const button of document.querySelectorAll("[data-execution-lockable] button")) {
      setMenuActionState(button, locked);
    }
    for (const anchor of document.querySelectorAll("[data-execution-lockable] a")) {
      setMenuActionState(anchor, locked);
    }
  }

  function guardMenuAction() {
    if (!executionMenuLocked) return false;
    log(MENU_LOCK_MESSAGE);
    return true;
  }

  function updateControlStates() {
    if (autoResetInProgress) {
      runBtn.disabled = true;
      debugRunBtn.disabled = true;
      debugStepBtn.disabled = true;
      debugContinueBtn.disabled = true;
      pauseBtn.disabled = true;
      resumeBtn.disabled = true;
      stopBtn.disabled = true;
      placeRobotStartBtn.disabled = true;
      robotThetaInput.disabled = true;
      breakpointsInput.disabled = true;
      if (watchesInput) watchesInput.disabled = true;
      updateMenuLockState();
      return;
    }

    const status = currentStatus || "created";
    const isRunning = status === "running";
    const isPaused = status === "paused";
    const isBusy = isRunning || isPaused;
    const canStart = ["created", "ready", "stopped", "finished", "timed_out", "error"].includes(status);
    const canonicalState = currentDebugState?.debug_state || "";
    const isCanonicalPaused = canonicalState.startsWith("paused_");
    const isEffectivelyPaused = isPaused || isCanonicalPaused || debugPaused;
    const canContinue = typeof currentDebugState?.can_continue === "boolean"
      ? currentDebugState.can_continue
      : isEffectivelyPaused;
    const canStep = typeof currentDebugState?.can_step === "boolean"
      ? currentDebugState.can_step
      : isEffectivelyPaused;

    runBtn.disabled = !canStart;
    debugRunBtn.disabled = !canStart;
    debugStepBtn.disabled = !(canStart || canStep);
    debugContinueBtn.disabled = !canContinue;
    pauseBtn.disabled = !isRunning || isCanonicalPaused || debugPaused;
    resumeBtn.disabled = !isEffectivelyPaused;
    stopBtn.disabled = status === "created";
    placeRobotStartBtn.disabled = isBusy;
    robotThetaInput.disabled = isBusy;
    const canEditDebugConfig = !(isRunning && !(debugPaused || isCanonicalPaused));
    breakpointsInput.disabled = !canEditDebugConfig;
    if (watchesInput) watchesInput.disabled = !canEditDebugConfig;
    updateMenuLockState();
  }

  function clearDebugState() {
    debugPaused = false;
    currentDebugState = null;
    currentDebugContext = null;
    currentDebugLine = null;
    setDebugState("");
    renderEditorGutter();
    renderDebugWatches();
    updateControlStates();
  }

  function clearBreakpoints() {
    gutterBreakpoints.clear();
    updateBreakpointsInput();
    renderEditorGutter();
  }

  function setDebugState(message) {
    debugState.textContent = message || "sin eventos";
  }

  function parseBreakpoints() {
    const parsed = breakpointsInput.value
      .split(/[,\s]+/)
      .map((item) => Number.parseInt(item, 10))
      .filter((line) => Number.isInteger(line) && line > 0);
    gutterBreakpoints = new Set(parsed);
    renderEditorGutter();
    return parsed;
  }

  function updateWatchesInput() {
    if (!watchesInput) return;
    watchesInput.value = watchExpressions.join(", ");
  }

  function parseWatches() {
    const raw = watchesInput?.value || "";
    const unique = new Set();
    const parsed = raw
      .split(/[,\n;]+/)
      .map((item) => item.trim())
      .filter((item) => item.length > 0 && item.length <= 200)
      .filter((item) => {
        if (unique.has(item)) return false;
        unique.add(item);
        return true;
      })
      .slice(0, 20);
    watchExpressions = parsed;
    updateWatchesInput();
    renderDebugWatches();
    return parsed;
  }

  async function applyWatchesToSession() {
    const parsed = parseWatches();
    try {
      const result = await api.setWatches(parsed);
      watchExpressions = Array.isArray(result?.watches) ? result.watches : parsed;
      updateWatchesInput();
      renderDebugWatches();
      return watchExpressions;
    } catch (err) {
      const unsupported = err?.status === 404 || err?.status === 405 || err?.code === "NOT_FOUND";
      if (!unsupported) throw err;
      // Compatibilidad con backends antiguos sin endpoint /debug/watches.
      watchExpressions = parsed;
      updateWatchesInput();
      renderDebugWatches();
      return watchExpressions;
    }
  }

  function formatDebugValue(value) {
    if (value === null || value === undefined) return "--";
    if (typeof value === "string") return escapeHtml(value);
    if (typeof value === "number" || typeof value === "boolean") return String(value);
    try {
      return escapeHtml(JSON.stringify(value));
    } catch {
      return escapeHtml(String(value));
    }
  }

  function renderDebugWatches() {
    if (!debugWatchesPanel || !debugWatchesBody || !debugWatchesEmpty) return;
    const configured = Array.isArray(watchExpressions) ? watchExpressions : [];
    const evaluated = Array.isArray(currentDebugContext?.watches) ? currentDebugContext.watches : [];
    const showPanel = configured.length > 0 || evaluated.length > 0;
    debugWatchesPanel.classList.toggle("hidden", !showPanel);
    if (!showPanel) {
      debugWatchesBody.innerHTML = "";
      return;
    }

    if (!evaluated.length) {
      debugWatchesBody.innerHTML = "";
      debugWatchesEmpty.classList.remove("hidden");
      return;
    }

    const watchedByExpr = new Map();
    for (const item of evaluated) {
      const expr = String(item?.expr ?? "").trim();
      if (!expr) continue;
      watchedByExpr.set(expr, item);
    }

    const rows = [];
    for (const expr of configured) {
      const item = watchedByExpr.get(expr) || { expr, value: null, error: "pendiente" };
      rows.push(item);
      watchedByExpr.delete(expr);
    }
    for (const extra of watchedByExpr.values()) {
      rows.push(extra);
    }

    debugWatchesBody.innerHTML = rows.map((item) => {
      const expr = escapeHtml(String(item?.expr ?? ""));
      const error = item?.error ? escapeHtml(String(item.error)) : "";
      const value = formatDebugValue(item?.value);
      const rowClass = error ? "debug-watch-row-error" : "";
      return `<tr class="${rowClass}"><td>${expr}</td><td>${value}</td><td>${error}</td></tr>`;
    }).join("");
    debugWatchesEmpty.classList.add("hidden");
  }

  function handleDebugContext(payload) {
    if (!payload || typeof payload !== "object") return;
    currentDebugContext = payload;
    if (Number.isInteger(payload.line) && payload.line > 0) {
      currentDebugLine = payload.line;
      renderEditorGutter();
    }
    renderDebugWatches();
  }

  function formatDebugEvent(payload) {
    if (!payload) return "";
    if (payload.type === "breakpoints") {
      return `breakpoints: ${(payload.breakpoints || []).join(", ") || "ninguno"}`;
    }
    if (payload.type === "watches") {
      return `watches: ${(payload.watches || []).join(" | ") || "ninguno"}`;
    }
    if (payload.debug_state) {
      if (payload.debug_state === "paused_breakpoint") {
        return `pausado en linea ${payload.line} (breakpoint)`;
      }
      if (payload.debug_state === "paused_step") {
        return `pausado en linea ${payload.line} (step)`;
      }
      if (payload.debug_state === "paused_manual") {
        return "pausa manual";
      }
      if (payload.debug_state === "idle") {
        return "";
      }
      if (payload.debug_state === "running" && payload.type === "command") {
        return `debug ${payload.action || "continue"}`;
      }
      if (payload.debug_state === "running" && payload.line) {
        return `linea ${payload.line}`;
      }
      if (payload.debug_state === "error") {
        return "debug error";
      }
      if (payload.debug_state === "stopped") {
        return "debug detenido";
      }
      return `debug ${payload.debug_state}`;
    }
    if (!payload.type) return "";
    if (payload.type === "paused") {
      return `pausado en linea ${payload.line} (${payload.reason || "debug"})`;
    }
    if (payload.type === "line" && payload.pause_reason) {
      return `linea ${payload.line}: ${payload.pause_reason}`;
    }
    if (payload.type === "command") {
      return `debug ${payload.action}`;
    }
    if (payload.line) {
      return `linea ${payload.line}`;
    }
    return payload.type;
  }

  function handleDebug(payload) {
    const message = formatDebugEvent(payload);
    if (message) setDebugState(message);
    if (payload?.debug_state) {
      currentDebugState = payload;
      debugPaused = String(payload.debug_state).startsWith("paused_");
      if (!debugPaused) currentDebugContext = null;
      if (Array.isArray(payload.watches)) {
        watchExpressions = payload.watches
          .map((item) => String(item ?? "").trim())
          .filter((item) => item.length > 0);
        updateWatchesInput();
      }
    } else if (payload?.type === "paused") {
      debugPaused = true;
      currentDebugState = { debug_state: "paused_step", can_continue: true, can_step: true, ...payload };
    } else if (payload?.type === "command") {
      debugPaused = false;
      currentDebugContext = null;
      currentDebugState = { debug_state: "running", can_continue: false, can_step: false, ...payload };
    }
    if (payload?.line) {
      currentDebugLine = payload.line;
      renderEditorGutter();
    } else if (payload?.debug_state && !String(payload.debug_state).startsWith("paused_")) {
      currentDebugLine = null;
      renderEditorGutter();
    }
    renderDebugWatches();
    updateControlStates();
  }

  function lineCount() {
    return Math.max(1, codeEditor.value.split("\n").length);
  }

  function parseCssPixelValue(value) {
    const parsed = Number.parseFloat(value || "");
    return Number.isFinite(parsed) ? parsed : null;
  }

  function syncEditorMetrics() {
    if (!codeEditorShell || !codeEditor) return;
    const style = window.getComputedStyle(codeEditor);
    const fontSizePx = parseCssPixelValue(style.fontSize) || 13;
    const resolvedLineHeightPx = parseCssPixelValue(style.lineHeight) || (fontSizePx * 1.45);
    codeEditorShell.style.setProperty("--editor-font-family", style.fontFamily || "Consolas, Menlo, monospace");
    codeEditorShell.style.setProperty("--editor-font-size", `${fontSizePx}px`);
    codeEditorShell.style.setProperty("--editor-line-height-px", `${resolvedLineHeightPx}px`);
    codeEditorShell.style.setProperty("--editor-line-height", String(resolvedLineHeightPx / fontSizePx));
    codeEditorShell.style.setProperty("--editor-pad-top", style.paddingTop || "12px");
    codeEditorShell.style.setProperty("--editor-pad-right", style.paddingRight || "12px");
    codeEditorShell.style.setProperty("--editor-pad-bottom", style.paddingBottom || "72px");
    codeEditorShell.style.setProperty("--editor-pad-left", style.paddingLeft || "12px");
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }

  function formatTelemetryNumber(value, digits = 2) {
    const number = Number(value);
    if (!Number.isFinite(number)) return "--";
    return Number.isInteger(number) ? String(number) : number.toFixed(digits);
  }

  function mmToCm(value) {
    const number = Number(value);
    if (!Number.isFinite(number)) return null;
    return number / 10;
  }

  function formatDistanceCm(value, digits = 1) {
    const cm = mmToCm(value);
    if (cm === null) return "--";
    return formatTelemetryNumber(cm, digits);
  }

  function formatTelemetryValue(value) {
    if (value === true) return "si";
    if (value === false) return "no";
    if (value === null || value === undefined) return "--";
    if (typeof value === "number") return formatTelemetryNumber(value);
    return escapeHtml(value);
  }

  function readableSensorKey(key) {
    return {
      distance_mm: "Distancia",
      presence: "Presencia",
      reflected: "Reflejado",
      ambient: "Ambiente",
      color: "Color",
      angle: "Angulo",
      speed: "Velocidad",
    }[key] || key.replaceAll("_", " ");
  }

  function sensorUnit(key) {
    return {
      distance_mm: " cm",
      angle: " °",
      speed: " °/s",
    }[key] || "";
  }

  function formatSensorTelemetryValue(key, value) {
    if (key === "distance_mm") return formatDistanceCm(value, 1);
    return formatTelemetryValue(value);
  }

  function renderMotorTelemetry(motor) {
    const state = escapeHtml(motor.state || "IDLE");
    const angle = Number(motor.angle);
    const normalizedAngle = Number.isFinite(angle)
      ? ((angle % 360) + 360) % 360
      : null;
    const normalizedText = normalizedAngle === null
      ? "--"
      : `${formatTelemetryNumber(normalizedAngle)} °`;
    return `
      <article class="telemetry-card motor-card">
        <div class="telemetry-card-title">
          <span>Motor ${escapeHtml(motor.port)}</span>
          <span class="telemetry-state">${state}</span>
        </div>
        <div class="motor-metrics">
          <span><b>Vel.</b> ${formatTelemetryNumber(motor.speed)} °/s</span>
          <span><b>Angulo</b> ${formatTelemetryNumber(motor.angle)} °</span>
          <span><b>Angulo 0-360</b> ${normalizedText}</span>
        </div>
      </article>
    `;
  }

  function renderSensorTelemetry(sensor) {
    const value = sensor.value || {};
    const entries = Object.entries(value).filter(([key]) => key !== "port");
    const rows = entries.length
      ? entries.map(([key, item]) => `
          <dt>${escapeHtml(readableSensorKey(key))}</dt>
          <dd>${formatSensorTelemetryValue(key, item)}${sensorUnit(key)}</dd>
        `).join("")
      : "<dt>Valor</dt><dd>--</dd>";
    return `
      <article class="telemetry-card">
        <div class="telemetry-card-title">
          <span class="sensor-port">${escapeHtml(sensor.port)}</span>
          <span class="sensor-type" title="${escapeHtml(sensor.type)}">${escapeHtml(sensor.type)}</span>
        </div>
        <dl class="telemetry-mini-list">${rows}</dl>
      </article>
    `;
  }

  function findCommentStart(line) {
    let inSingle = false;
    let inDouble = false;
    let escaped = false;
    for (let i = 0; i < line.length; i += 1) {
      const ch = line[i];
      if (escaped) {
        escaped = false;
        continue;
      }
      if (ch === "\\") {
        escaped = true;
        continue;
      }
      if (!inDouble && ch === "'") {
        inSingle = !inSingle;
        continue;
      }
      if (!inSingle && ch === '"') {
        inDouble = !inDouble;
        continue;
      }
      if (!inSingle && !inDouble && ch === "#") {
        return i;
      }
    }
    return -1;
  }

  function splitCodeAndComment(line) {
    const commentStart = findCommentStart(line);
    if (commentStart < 0) {
      return { code: line, comment: "" };
    }
    return {
      code: line.slice(0, commentStart),
      comment: line.slice(commentStart),
    };
  }

  function highlightInlineCode(rawCode) {
    const code = escapeHtml(rawCode);
    let expect = "";
    let definitionKind = "";
    return code.replace(
      /(@[A-Za-z_]\w*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b\d+(?:\.\d+)?\b|\b[A-Za-z_]\w*\b)/g,
      (token) => {
        if (/^@/.test(token)) return `<span class="syntax-decorator">${token}</span>`;
        if (/^["']/.test(token)) return `<span class="syntax-string">${token}</span>`;
        if (/^\d/.test(token)) return `<span class="syntax-number">${token}</span>`;
        if (expect === "definition_name") {
          expect = "";
          if (definitionKind === "class") {
            definitionKind = "";
            return `<span class="syntax-classname">${token}</span>`;
          }
          definitionKind = "";
          return `<span class="syntax-defname">${token}</span>`;
        }
        if (token === "def") {
          expect = "definition_name";
          definitionKind = "def";
          return `<span class="syntax-kw">${token}</span>`;
        }
        if (token === "class") {
          expect = "definition_name";
          definitionKind = "class";
          return `<span class="syntax-kw">${token}</span>`;
        }
        if (token === "from") {
          expect = "module_name";
          return `<span class="syntax-kw">${token}</span>`;
        }
        if (token === "import") {
          expect = "import_symbol";
          return `<span class="syntax-kw">${token}</span>`;
        }
        if ((expect === "module_name" || expect === "import_symbol") && /^[A-Za-z_]\w*$/.test(token)) {
          return `<span class="syntax-import">${token}</span>`;
        }
        if (syntaxLiteralKeywords.has(token)) return `<span class="syntax-const">${token}</span>`;
        if (syntaxKeywords.has(token)) return `<span class="syntax-kw">${token}</span>`;
        if (syntaxBuiltins.has(token)) return `<span class="syntax-builtin">${token}</span>`;
        return token;
      },
    );
  }

  function highlightCodeLine(line, state) {
    let remaining = line;
    let output = "";
    while (remaining.length) {
      if (state.blockStringDelim) {
        const endInLine = remaining.indexOf(state.blockStringDelim);
        if (endInLine < 0) {
          output += `<span class="syntax-string">${escapeHtml(remaining)}</span>`;
          break;
        }
        const chunk = remaining.slice(0, endInLine + state.blockStringDelim.length);
        output += `<span class="syntax-string">${escapeHtml(chunk)}</span>`;
        remaining = remaining.slice(endInLine + state.blockStringDelim.length);
        state.blockStringDelim = null;
        continue;
      }

      const tripleDouble = remaining.indexOf('"""');
      const tripleSingle = remaining.indexOf("'''");
      let tripleStart = -1;
      let tripleDelim = "";
      if (tripleDouble >= 0 && (tripleSingle < 0 || tripleDouble < tripleSingle)) {
        tripleStart = tripleDouble;
        tripleDelim = '"""';
      } else if (tripleSingle >= 0) {
        tripleStart = tripleSingle;
        tripleDelim = "'''";
      }

      if (tripleStart < 0) {
        const split = splitCodeAndComment(remaining);
        output += highlightInlineCode(split.code);
        if (split.comment) {
          output += `<span class="syntax-comment">${escapeHtml(split.comment)}</span>`;
        }
        break;
      }

      const commentStart = findCommentStart(remaining);
      if (commentStart >= 0 && commentStart < tripleStart) {
        const split = splitCodeAndComment(remaining);
        output += highlightInlineCode(split.code);
        output += `<span class="syntax-comment">${escapeHtml(split.comment)}</span>`;
        break;
      }

      const prefix = remaining.slice(0, tripleStart);
      if (prefix) {
        output += highlightInlineCode(prefix);
      }

      const restAfterStart = remaining.slice(tripleStart + 3);
      const endInRest = restAfterStart.indexOf(tripleDelim);
      if (endInRest < 0) {
        output += `<span class="syntax-string">${escapeHtml(remaining.slice(tripleStart))}</span>`;
        state.blockStringDelim = tripleDelim;
        break;
      }

      const endIndex = tripleStart + 3 + endInRest + 3;
      const stringChunk = remaining.slice(tripleStart, endIndex);
      output += `<span class="syntax-string">${escapeHtml(stringChunk)}</span>`;
      remaining = remaining.slice(endIndex);
    }
    return output || "&nbsp;";
  }

  function updateSyntaxHighlight() {
    const lines = codeEditor.value.split("\n");
    const state = { blockStringDelim: null };
    syntaxHighlight.innerHTML = lines
      .map((line, index) => {
        const lineNo = index + 1;
        const content = line.length ? highlightCodeLine(line, state) : "&nbsp;";
        return `<span class="syntax-line" data-line="${lineNo}">${content}</span>`;
      })
      .join("");
    syncCurrentDebugLineHighlight();
    syntaxHighlight.scrollTop = codeEditor.scrollTop;
    syntaxHighlight.scrollLeft = codeEditor.scrollLeft;
  }

  function syncCurrentDebugLineHighlight() {
    const previous = syntaxHighlight.querySelector(".syntax-line.current-debug-line");
    if (previous) previous.classList.remove("current-debug-line");
    if (!Number.isInteger(currentDebugLine) || currentDebugLine <= 0) return;
    const target = syntaxHighlight.querySelector(`.syntax-line[data-line="${currentDebugLine}"]`);
    if (target) target.classList.add("current-debug-line");
  }

  function updateBreakpointsInput() {
    breakpointsInput.value = Array.from(gutterBreakpoints).sort((a, b) => a - b).join(", ");
  }

  function renderEditorGutter() {
    const count = lineCount();
    const fragment = document.createDocumentFragment();
    for (let line = 1; line <= count; line += 1) {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "gutter-line";
      if (gutterBreakpoints.has(line)) item.classList.add("has-breakpoint");
      if (currentDebugLine === line) item.classList.add("current-debug-line");
      item.dataset.line = String(line);
      item.textContent = line;
      fragment.appendChild(item);
    }
    editorGutter.innerHTML = "";
    editorGutter.appendChild(fragment);
    editorGutter.scrollTop = codeEditor.scrollTop;
    syncCurrentDebugLineHighlight();
  }

  function toggleBreakpoint(line) {
    if (gutterBreakpoints.has(line)) {
      gutterBreakpoints.delete(line);
    } else {
      gutterBreakpoints.add(line);
    }
    updateBreakpointsInput();
    renderEditorGutter();
  }

  function inferVariableTypes() {
    const types = {};
    const assignments = codeEditor.value.matchAll(/^\s*([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)\s*\(/gm);
    for (const match of assignments) {
      types[match[1]] = match[2];
    }
    const attrAssignments = codeEditor.value.matchAll(/^\s*([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)\.([A-Za-z_]\w*)/gm);
    for (const match of attrAssignments) {
      const ownerType = types[match[2]] || match[2];
      const attrType = attrTypeHints[`${ownerType}.${match[3]}`];
      if (attrType) types[match[1]] = attrType;
    }
    return types;
  }

  function autocompleteContext() {
    const beforeCursor = codeEditor.value.slice(0, codeEditor.selectionStart);
    const dotted = beforeCursor.match(/([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\.([A-Za-z_]\w*)?$/);
    if (dotted) {
      const chain = dotted[1].split(".");
      const types = inferVariableTypes();
      let typeName = types[chain[0]] || chain[0];
      for (const attr of chain.slice(1)) {
        typeName = attrTypeHints[`${typeName}.${attr}`] || typeName;
      }
      return { prefix: dotted[2] || "", contextName: typeName, replaceFrom: codeEditor.selectionStart - (dotted[2] || "").length };
    }
    const word = beforeCursor.match(/([A-Za-z_]\w*)$/);
    return {
      prefix: word?.[1] || "",
      contextName: null,
      replaceFrom: codeEditor.selectionStart - (word?.[1]?.length || 0),
    };
  }

  function autocompleteCandidates(prefix, contextName = null) {
    const source = contextName && contextHints[contextName] ? contextHints[contextName] : autocompleteWords;
    const normalizedPrefix = prefix.toLowerCase();
    return Array.from(new Set(source))
      .filter((item) => !normalizedPrefix || item.toLowerCase().startsWith(normalizedPrefix))
      .slice(0, 12);
  }

  function renderAutocomplete(items) {
    autocompletePopup.innerHTML = "";
    items.forEach((item, index) => {
      const option = document.createElement("button");
      option.type = "button";
      option.className = `autocomplete-item${index === autocompleteSelected ? " active" : ""}`;
      option.dataset.index = String(index);
      option.textContent = item;
      option.addEventListener("mousedown", (event) => {
        event.preventDefault();
        applyAutocomplete(index);
      });
      autocompletePopup.appendChild(option);
    });
  }

  function caretPixelPosition() {
    const mirror = document.createElement("div");
    const style = window.getComputedStyle(codeEditor);
    const props = [
      "boxSizing",
      "width",
      "height",
      "overflowX",
      "overflowY",
      "borderTopWidth",
      "borderRightWidth",
      "borderBottomWidth",
      "borderLeftWidth",
      "paddingTop",
      "paddingRight",
      "paddingBottom",
      "paddingLeft",
      "fontStyle",
      "fontVariant",
      "fontWeight",
      "fontStretch",
      "fontSize",
      "fontFamily",
      "lineHeight",
      "letterSpacing",
      "textTransform",
      "textIndent",
      "textAlign",
      "whiteSpace",
      "wordBreak",
      "overflowWrap",
      "tabSize",
    ];
    mirror.style.position = "absolute";
    mirror.style.visibility = "hidden";
    mirror.style.pointerEvents = "none";
    mirror.style.whiteSpace = "pre-wrap";
    mirror.style.wordBreak = "normal";
    mirror.style.overflowWrap = "normal";
    mirror.style.top = "0";
    mirror.style.left = "0";
    for (const prop of props) {
      mirror.style[prop] = style[prop];
    }
    mirror.style.width = `${codeEditor.clientWidth}px`;

    const before = codeEditor.value.slice(0, codeEditor.selectionStart);
    mirror.textContent = before;
    const marker = document.createElement("span");
    marker.textContent = "\u200b";
    mirror.appendChild(marker);
    codeEditorShell.appendChild(mirror);

    const left = marker.offsetLeft;
    const top = marker.offsetTop;
    mirror.remove();
    return { left, top };
  }

  function placeAutocompletePopup() {
    if (!isAutocompleteVisible() || !codeEditorShell) return;
    const caret = caretPixelPosition();
    const shellRect = codeEditorShell.getBoundingClientRect();
    const editorRect = codeEditor.getBoundingClientRect();
    const popupRect = autocompletePopup.getBoundingClientRect();
    const lineHeight = parseCssPixelValue(window.getComputedStyle(codeEditor).lineHeight) || 20;

    let left = (editorRect.left - shellRect.left) + caret.left - codeEditor.scrollLeft;
    let top = (editorRect.top - shellRect.top) + caret.top - codeEditor.scrollTop + lineHeight;

    const maxLeft = Math.max(8, codeEditorShell.clientWidth - Math.max(autocompletePopup.offsetWidth, popupRect.width) - 8);
    left = Math.max(52, Math.min(left, maxLeft));

    const desiredHeight = Math.max(120, Math.min(220, autocompletePopup.scrollHeight));
    const belowSpace = codeEditorShell.clientHeight - top - 8;
    if (belowSpace < 90) {
      top = top - desiredHeight - lineHeight;
    }
    const maxTop = Math.max(8, codeEditorShell.clientHeight - desiredHeight - 8);
    top = Math.max(8, Math.min(top, maxTop));

    autocompletePopup.style.left = `${Math.round(left)}px`;
    autocompletePopup.style.top = `${Math.round(top)}px`;
  }

  function showAutocomplete(force = false) {
    const context = autocompleteContext();
    const items = autocompleteCandidates(context.prefix, context.contextName);
    if (!items.length || (!force && context.prefix.length < 2 && !context.contextName)) {
      hideAutocomplete();
      return false;
    }
    autocompleteItems = items;
    autocompleteSelected = 0;
    autocompletePopup.dataset.replaceFrom = String(context.replaceFrom);
    renderAutocomplete(items);
    autocompletePopup.classList.remove("hidden");
    placeAutocompletePopup();
    return true;
  }

  function hideAutocomplete() {
    autocompleteItems = [];
    autocompletePopup.classList.add("hidden");
    autocompletePopup.innerHTML = "";
  }

  function isAutocompleteVisible() {
    return !autocompletePopup.classList.contains("hidden");
  }

  function moveAutocompleteSelection(delta) {
    if (!autocompleteItems.length) return;
    autocompleteSelected = (autocompleteSelected + delta + autocompleteItems.length) % autocompleteItems.length;
    renderAutocomplete(autocompleteItems);
    placeAutocompletePopup();
  }

  function applyAutocomplete(index = autocompleteSelected) {
    const value = autocompleteItems[index];
    if (!value) return;
    const replaceFrom = Number.parseInt(autocompletePopup.dataset.replaceFrom || `${codeEditor.selectionStart}`, 10);
    const replaceTo = codeEditor.selectionStart;
    codeEditor.setRangeText(value, replaceFrom, replaceTo, "end");
    hideAutocomplete();
    renderEditorGutter();
    updateSyntaxHighlight();
    codeEditor.focus();
  }

  function insertAtCursor(before, after = "") {
    const start = codeEditor.selectionStart;
    const end = codeEditor.selectionEnd;
    const selected = codeEditor.value.slice(start, end);
    codeEditor.setRangeText(`${before}${selected}${after}`, start, end, "end");
    const cursor = start + before.length + selected.length;
    codeEditor.setSelectionRange(cursor, cursor);
    renderEditorGutter();
    updateSyntaxHighlight();
  }

  function handleEditorPairs(event) {
    const pairs = {
      "(": ")",
      "[": "]",
      "{": "}",
      '"': '"',
      "'": "'",
    };
    const close = pairs[event.key];
    if (!close || event.ctrlKey || event.altKey || event.metaKey) return false;
    event.preventDefault();
    insertAtCursor(event.key, close);
    hideAutocomplete();
    return true;
  }

  function handleEditorEnter(event) {
    if (event.key !== "Enter" || event.ctrlKey || event.altKey || event.metaKey) return false;
    event.preventDefault();
    const beforeCursor = codeEditor.value.slice(0, codeEditor.selectionStart);
    const currentLine = beforeCursor.split("\n").pop() || "";
    const indent = currentLine.match(/^\s*/)?.[0] || "";
    const extraIndent = currentLine.trimEnd().endsWith(":") ? "    " : "";
    insertAtCursor(`\n${indent}${extraIndent}`);
    hideAutocomplete();
    return true;
  }

  function handleEditorTab(event) {
    if (event.key !== "Tab" || event.ctrlKey || event.altKey || event.metaKey) return false;
    event.preventDefault();
    hideAutocomplete();
    if (event.shiftKey) {
      unindentSelection();
    } else {
      indentSelection();
    }
    renderEditorGutter();
    updateSyntaxHighlight();
    return true;
  }

  function selectedLineRange() {
    const value = codeEditor.value;
    const start = codeEditor.selectionStart;
    const end = codeEditor.selectionEnd;
    const lineStart = value.lastIndexOf("\n", Math.max(0, start - 1)) + 1;
    let lineEnd = end;
    if (end > start && value[end - 1] === "\n") {
      lineEnd = end - 1;
    }
    const nextNewline = value.indexOf("\n", lineEnd);
    return {
      start,
      end,
      lineStart,
      lineEnd: nextNewline === -1 ? value.length : nextNewline,
    };
  }

  function indentSelection() {
    const value = codeEditor.value;
    const range = selectedLineRange();
    if (range.start === range.end) {
      codeEditor.setRangeText("    ", range.start, range.end, "end");
      return;
    }
    const block = value.slice(range.lineStart, range.lineEnd);
    const indented = block.split("\n").map((line) => `    ${line}`).join("\n");
    codeEditor.setRangeText(indented, range.lineStart, range.lineEnd, "select");
    codeEditor.selectionStart = range.start + 4;
    codeEditor.selectionEnd = range.end + (indented.length - block.length);
    placeAutocompletePopup();
  }

  function unindentSelection() {
    const value = codeEditor.value;
    const range = selectedLineRange();
    if (range.start === range.end) {
      const lineStart = range.lineStart;
      const cursor = range.start;
      const beforeCursor = value.slice(lineStart, cursor);
      const removable = beforeCursor.match(/ {1,4}$/)?.[0].length || 0;
      if (!removable) return;
      codeEditor.setRangeText("", cursor - removable, cursor, "end");
      placeAutocompletePopup();
      return;
    }
    const block = value.slice(range.lineStart, range.lineEnd);
    let removedBeforeSelection = 0;
    let totalRemoved = 0;
    let cursor = range.lineStart;
    const unindented = block.split("\n").map((line) => {
      const remove = line.startsWith("    ") ? 4 : (line.match(/^ {1,3}/)?.[0].length || 0);
      if (cursor < range.start) removedBeforeSelection += remove;
      totalRemoved += remove;
      cursor += line.length + 1;
      return line.slice(remove);
    }).join("\n");
    codeEditor.setRangeText(unindented, range.lineStart, range.lineEnd, "select");
    codeEditor.selectionStart = Math.max(range.lineStart, range.start - removedBeforeSelection);
    codeEditor.selectionEnd = Math.max(codeEditor.selectionStart, range.end - totalRemoved);
    placeAutocompletePopup();
  }

  function handleAutocompleteKeys(event) {
    if ((event.ctrlKey || event.metaKey) && event.code === "Space") {
      event.preventDefault();
      showAutocomplete(true);
      return true;
    }
    if (!isAutocompleteVisible()) return false;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      moveAutocompleteSelection(1);
      return true;
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      moveAutocompleteSelection(-1);
      return true;
    }
    if (event.key === "Enter" || event.key === "Tab") {
      event.preventDefault();
      applyAutocomplete();
      return true;
    }
    if (event.key === "Escape") {
      event.preventDefault();
      hideAutocomplete();
      return true;
    }
    return false;
  }

  async function init() {
    // En hosting, reutilizar sesion al cargar puede provocar carreras con
    // closeSessionOnUnload de una pestana previa; usamos sesion nueva.
    const session = await api.createSession();
    setStatus(session.status);

    // Priorizar que la simulacion quede operativa de inmediato.
    liveUpdateController.start();
    void refreshSnapshot();

    // Cargar menus en paralelo para no bloquear la interaccion principal.
    void loadExamples().catch((err) => {
      examplesMenu.innerHTML = '<span class="menu-empty">No se pudieron cargar ejemplos</span>';
      log(`Error cargando ejemplos: ${err.message}`);
    });
    void loadMissions().catch((err) => {
      missionsMenu.innerHTML = '<span class="menu-empty">No se pudieron cargar misiones</span>';
      log(`Error cargando misiones: ${err.message}`);
    });
    void (async () => {
      try {
        await loadWorlds();
        await loadWorldFromUrl();
      } catch (err) {
        worldsMenu.innerHTML = `<a href="${api.resolvePath("/worlds")}">Editor de mundos</a><span class="menu-empty">No se pudieron cargar mundos</span>`;
        log(`Error cargando mundos: ${err.message}`);
      }
    })();
  }

  async function loadExamples() {
    const data = await api.listExamples();
    examplesMenu.innerHTML = "";
    for (const item of data.examples) {
      examplesMenu.appendChild(menuButton(item.name, () => loadExampleByName(item.name)));
    }
    if (!data.examples.length) {
      examplesMenu.innerHTML = '<span class="menu-empty">No hay ejemplos</span>';
    }
  }

  async function loadMissions() {
    const data = await api.listMissions();
    missionsMenu.innerHTML = "";
    for (const mission of data.missions) {
      missionsMenu.appendChild(menuButton(mission.title, () => loadMission(mission)));
    }
    if (!data.missions.length) {
      missionsMenu.innerHTML = '<span class="menu-empty">No hay misiones disponibles</span>';
    }
  }

  async function loadWorlds() {
    const data = await api.listWorlds();
    loadedWorldNames = new Set(data.worlds.map((item) => item.name));
    worldsMenu.innerHTML = `<a href="${api.resolvePath("/worlds")}">Editor de mundos</a>`;
    worldsMenu.appendChild(menuButton("Mundo en blanco (sin mapa)", () => {
      void loadBlankWorld();
    }));
    worldsMenu.appendChild(menuButton("Cargar mundo desde tu equipo", () => {
      if (worldFileInput) worldFileInput.value = "";
      worldFileInput?.click();
    }));

    const presetsGroup = document.createElement("div");
    presetsGroup.className = "menu-subgroup";
    const presetsToggle = document.createElement("button");
    presetsToggle.type = "button";
    presetsToggle.className = "menu-subtoggle";
    presetsToggle.setAttribute("aria-expanded", "false");
    presetsToggle.textContent = "Mundos preestablecidos ▸";

    const presetsList = document.createElement("div");
    presetsList.className = "menu-sublist hidden";

    presetsToggle.addEventListener("click", () => {
      const expanded = !presetsList.classList.contains("hidden");
      if (expanded) {
        presetsList.classList.add("hidden");
        presetsToggle.setAttribute("aria-expanded", "false");
        presetsToggle.textContent = "Mundos preestablecidos ▸";
      } else {
        presetsList.classList.remove("hidden");
        presetsToggle.setAttribute("aria-expanded", "true");
        presetsToggle.textContent = "Mundos preestablecidos ▾";
      }
    });

    for (const item of data.worlds) {
      presetsList.appendChild(menuButton(item.name, () => loadWorldByName(item.name)));
    }
    if (!data.worlds.length) {
      const empty = document.createElement("span");
      empty.className = "menu-empty";
      empty.textContent = "No hay mundos";
      presetsList.appendChild(empty);
    }

    presetsGroup.appendChild(presetsToggle);
    presetsGroup.appendChild(presetsList);
    worldsMenu.appendChild(presetsGroup);
  }

  function menuButton(label, action) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.addEventListener("click", () => {
      if (guardMenuAction()) return;
      action();
    });
    setMenuActionState(button, executionMenuLocked);
    return button;
  }

  async function loadWorldFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const worldName = params.get("world");
    if (!worldName) return;
    if (!loadedWorldNames.has(worldName)) {
      log(`Mundo no encontrado: ${worldName}`);
      return;
    }
    await loadWorldByName(worldName);
  }

  function robotStartFromLoadedWorld(world) {
    const spec = world?.editor_spec;
    const placements = Array.isArray(spec?.placements) ? spec.placements : [];
    const robotPlacement = placements.find((item) => String(item?.asset_key || "").includes("robot")) || null;
    if (!robotPlacement) return null;
    const gridSizePx = Number(spec?.grid_size_px || 32);
    const mmPerPx = 100 / Math.max(1, gridSizePx);
    const xPx = Number(robotPlacement.x ?? robotPlacement.x_px ?? 0);
    const yPx = Number(robotPlacement.y ?? robotPlacement.y_px ?? 0);
    const thetaDeg = Number(robotPlacement.rotation ?? robotPlacement.theta_deg ?? 0);
    return {
      x_mm: xPx * mmPerPx + 50,
      y_mm: yPx * mmPerPx + 50,
      theta_deg: ((thetaDeg % 360) + 360) % 360,
    };
  }

  async function refreshSnapshot() {
    if (!api.sessionId) return;
    if (snapshotRequestInFlight) return;
    snapshotRequestInFlight = true;
    try {
      const data = await api.snapshot();
      setStatus(data.status);
      if (data.error) {
        log(`${data.error.error || "Error"}\n${data.error.traceback || ""}`);
      }
      if (data.debug) {
        handleDebug(data.debug);
      }
      if (data.debug_context) {
        handleDebugContext(data.debug_context);
      }
      renderSnapshot(data.snapshot);
    } catch (err) {
      if (isSessionLost(err)) {
        await recoverSession();
        return;
      }
      log(err.message);
    } finally {
      snapshotRequestInFlight = false;
    }
  }

  function clearStreamBootstrapTimeout() {
    if (streamBootstrapTimeout) {
      clearTimeout(streamBootstrapTimeout);
      streamBootstrapTimeout = null;
    }
  }

  function clearStreamRetryTimer() {
    if (streamRetryTimer) {
      clearTimeout(streamRetryTimer);
      streamRetryTimer = null;
    }
  }

  function startSnapshotStream() {
    if (!SSE_ENABLED) {
      startPollingFallback();
      return;
    }
    stopLiveUpdates();
    let hasInitialEvent = false;
    try {
      stream = api.openSnapshotStream({
        snapshot: (payload) => {
          hasInitialEvent = true;
          clearStreamBootstrapTimeout();
          renderSnapshot(payload);
        },
        status: (payload) => {
          hasInitialEvent = true;
          clearStreamBootstrapTimeout();
          if (payload?.status) setStatus(payload.status);
        },
        debug: (payload) => {
          hasInitialEvent = true;
          clearStreamBootstrapTimeout();
          handleDebug(payload);
        },
        debugState: (payload) => {
          hasInitialEvent = true;
          clearStreamBootstrapTimeout();
          handleDebug(payload);
        },
        debugContext: (payload) => {
          handleDebugContext(payload);
          hasInitialEvent = true;
          clearStreamBootstrapTimeout();
        },
        world: (payload) => {
          hasInitialEvent = true;
          clearStreamBootstrapTimeout();
          currentWorld = payload || currentWorld;
          redrawCanvas();
        },
        missionResult: (payload) => renderMissionResult(payload),
        error: (payload) => {
          const message = payload?.error?.message || payload?.message;
          if (message) log(message);
        },
        connectionError: () => {
          clearStreamBootstrapTimeout();
          clearStreamRetryTimer();
          if (usingPollingFallback) return;
          if (stream) {
            stream.close();
            stream = null;
          }
          startPollingFallback();
        },
      });
      streamBootstrapTimeout = setTimeout(() => {
        if (hasInitialEvent || usingPollingFallback) return;
        if (stream) {
          stream.close();
          stream = null;
        }
        startPollingFallback();
      }, STREAM_BOOTSTRAP_TIMEOUT_MS);
    } catch (err) {
      log(err.message);
      startPollingFallback();
    }
  }

  function scheduleStreamRetry() {
    if (streamRetryTimer || !usingPollingFallback) return;
    streamRetryTimer = setTimeout(() => {
      streamRetryTimer = null;
      if (!usingPollingFallback || recoveringSession) return;
      startSnapshotStream();
    }, STREAM_RETRY_DELAY_MS);
  }

  function startPollingFallback() {
    if (usingPollingFallback) return;
    clearStreamBootstrapTimeout();
    clearStreamRetryTimer();
    if (stream) {
      stream.close();
      stream = null;
    }
    usingPollingFallback = true;
    timer = setInterval(refreshSnapshot, POLLING_INTERVAL_MS);
    refreshSnapshot();
    scheduleStreamRetry();
  }

  function stopLiveUpdates() {
    clearStreamBootstrapTimeout();
    clearStreamRetryTimer();
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
    if (stream) {
      stream.close();
      stream = null;
    }
    usingPollingFallback = false;
  }

  function startSnapshotWatchdog() {
    streamHealthController.start();
  }

  async function forceStateRefreshAfterStart() {
    try {
      await refreshSnapshot();
      if (!stream && !timer) {
        startPollingFallback();
      }
    } catch {
      if (!stream && !timer) {
        startPollingFallback();
      }
    }
  }

  function isSessionLost(err) {
    return err?.status === 404 || err?.code === "SESSION_NOT_FOUND";
  }

  async function recoverSession() {
    if (recoveringSession) return;
    recoveringSession = true;
    try {
      stopLiveUpdates();
      const session = await api.createSession({ reuse: true });
      recoveryFailures = 0;
      setStatus(session.status);
      if (selectedWorldName && loadedWorldNames.has(selectedWorldName)) {
        try {
          const worldData = await api.loadWorld(selectedWorldName);
          currentWorld = worldData.world || currentWorld;
          if (statusWorld) statusWorld.textContent = selectedWorldName;
        } catch {
          // Continuar aunque no se pueda rehidratar el mundo seleccionado.
        }
      } else if (selectedBlankWorld) {
        try {
          const worldData = await api.loadBlankWorld({ width_cells: 40, height_cells: 40 });
          currentWorld = worldData.world || currentWorld;
          if (statusWorld) statusWorld.textContent = "Mundo en blanco";
        } catch {
          // Continuar aunque falle la restauracion del mundo en blanco.
        }
      }
      startSnapshotStream();
      await refreshSnapshot();
    } catch (err) {
      log(err.message);
      recoveryFailures += 1;
      if (err?.status === 429 || recoveryFailures >= 3) {
        stopLiveUpdates();
        setStatus("error");
      }
    } finally {
      recoveringSession = false;
    }
  }

  function renderSnapshot(snapshot) {
    snapshotController.apply(snapshot);
  }

  function redrawCanvas() {
    worldViewController.draw();
  }

  function syncSensorBeamsButton() {
    if (!toggleSensorBeamsBtn) return;
    toggleSensorBeamsBtn.textContent = showSensorBeams ? "Haces ON" : "Haces OFF";
    toggleSensorBeamsBtn.classList.toggle("is-active", showSensorBeams);
  }

  function applyMapZoom(action) {
    if (!window.EV3Canvas || !canvas) return;
    worldViewController.zoom(action);
  }

  window.addEventListener("ev3-assets-loaded", redrawCanvas);

  if (toggleSensorBeamsBtn) {
    toggleSensorBeamsBtn.addEventListener("click", () => {
      showSensorBeams = !showSensorBeams;
      syncSensorBeamsButton();
      redrawCanvas();
    });
    syncSensorBeamsButton();
  }

  function updateTelemetry(snapshot) {
    telemetryController.render(snapshot);
  }

  function renderScreenCanvas(canvas, screenData) {
    if (!(canvas instanceof HTMLCanvasElement)) return;

    const widthPx = Math.max(1, Number(screenData?.width_px || 178));
    const heightPx = Math.max(1, Number(screenData?.height_px || 128));
    const lines = Array.isArray(screenData?.lines) ? screenData.lines.map((ln) => String(ln)) : [];
    const drawOps = Array.isArray(screenData?.draw_ops) ? screenData.draw_ops : [];

    if (canvas.width !== widthPx) canvas.width = widthPx;
    if (canvas.height !== heightPx) canvas.height = heightPx;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.save();
    ctx.clearRect(0, 0, widthPx, heightPx);
    ctx.fillStyle = "#dbe8d4";
    ctx.fillRect(0, 0, widthPx, heightPx);

    ctx.strokeStyle = "#cfd9bf";
    ctx.lineWidth = 1;
    for (let y = 0; y < heightPx; y += 3) {
      ctx.beginPath();
      ctx.moveTo(0, y + 0.5);
      ctx.lineTo(widthPx, y + 0.5);
      ctx.stroke();
    }

    for (const op of drawOps) {
      const kind = String(op?.op || "").toLowerCase();
      const color = Number(op?.color ?? 1) ? "#111111" : "#dbe8d4";
      ctx.strokeStyle = color;
      ctx.fillStyle = color;
      ctx.lineWidth = 1;

      if (kind === "pixel") {
        ctx.fillRect(Number(op.x) || 0, Number(op.y) || 0, 1, 1);
      } else if (kind === "line") {
        ctx.beginPath();
        ctx.moveTo((Number(op.x1) || 0) + 0.5, (Number(op.y1) || 0) + 0.5);
        ctx.lineTo((Number(op.x2) || 0) + 0.5, (Number(op.y2) || 0) + 0.5);
        ctx.stroke();
      } else if (kind === "circle") {
        ctx.beginPath();
        ctx.arc(Number(op.x) || 0, Number(op.y) || 0, Math.max(0, Number(op.r) || 0), 0, Math.PI * 2);
        if (op.fill) ctx.fill();
        else ctx.stroke();
      } else if (kind === "box") {
        const x = Number(op.x) || 0;
        const y = Number(op.y) || 0;
        const w = Math.max(0, Number(op.w) || 0);
        const h = Math.max(0, Number(op.h) || 0);
        if (op.fill) ctx.fillRect(x, y, w, h);
        else ctx.strokeRect(x + 0.5, y + 0.5, Math.max(0, w - 1), Math.max(0, h - 1));
      }
    }

    ctx.fillStyle = "#111111";
    ctx.font = "12px 'Courier New', monospace";
    ctx.textBaseline = "top";
    for (let i = 0; i < lines.length && i < 8; i += 1) {
      ctx.fillText(lines[i], 4, 4 + (i * 14));
    }
    ctx.restore();
  }

  function updateBrick(snapshot) {
    if (!snapshot?.brick) return;
    const led = document.getElementById("led");
    led.style.background = {
      RED: "#d62828",
      GREEN: "#2f9e44",
      ORANGE: "#f08c00",
      YELLOW: "#f5c542",
    }[snapshot.brick.led] || "#c9ced6";
    const ledText = document.getElementById("ledText");
    if (ledText) ledText.textContent = snapshot.brick.led || "Apagado";
    const screenCanvas = document.getElementById("screen");
    if (screenCanvas instanceof HTMLCanvasElement) {
      const screenData = snapshot.brick.screen || {};
      renderScreenCanvas(screenCanvas, screenData);
    }
    const speaker = snapshot.brick.speaker;
    const speakerEl = document.getElementById("speaker");
    if (!speakerEl) return;
    if (speaker) {
      speakerEl.textContent =
        `${speaker.freq || 0} Hz, ${Math.round(speaker.duration_ms || 0)} ms, ` +
        `vol ${speaker.volume ?? 50}`;
      window.EV3SpeakerAudio.handleSpeaker(speaker);
    } else {
      speakerEl.textContent = "Inactivo";
      window.EV3SpeakerAudio.handleSpeaker(null);
    }
  }

  runBtn.addEventListener("click", async () => {
    window.EV3SpeakerAudio.unlock();
    const result = await sessionController.run(codeEditor.value);
    if (result) log("");
  });

  debugRunBtn.addEventListener("click", async () => {
    window.EV3SpeakerAudio.unlock();
    const result = await sessionController.debugStart({
      source: codeEditor.value,
      breakpoints: parseBreakpoints(),
      watches: parseWatches(),
    });
    if (result) log("");
  });

  debugStepBtn.addEventListener("click", async () => {
    window.EV3SpeakerAudio.unlock();
    await sessionController.debugStep({
      source: codeEditor.value,
      breakpoints: parseBreakpoints(),
      watches: parseWatches(),
      active: ["running", "paused"].includes(currentStatus),
    });
  });

  debugContinueBtn.addEventListener("click", async () => {
    await sessionController.debugContinue();
  });

  pauseBtn.addEventListener("click", async () => {
    await sessionController.pause();
  });
  resumeBtn.addEventListener("click", async () => {
    await sessionController.resume();
  });
  async function performStopAndReset(options = {}) {
    if (autoResetInProgress) return;
    autoResetInProgress = true;
    suppressStoppedAutoReset = true;
    if (options.automatic && statusEl) {
      statusEl.textContent = "reiniciando";
    }
    updateControlStates();
    try {
      const result = await api.reset();
      window.EV3Canvas.resetTrail();
      await refreshSnapshot();
      robotStart = robotStartFromLoadedWorld(currentWorld) || robotStart;
      robotStartPreview = null;
      showRobotStartMarker = false;
      clearBreakpoints();
      clearDebugState();
      executionMenuLocked = false;
      setStatus(result.status);
      updateRobotStartReadout();
      redrawCanvas();
      if (options.automatic) {
        log("Ejecucion finalizada. Simulacion reiniciada.");
      }
    } catch (err) {
      log(err.message);
    } finally {
      autoResetInProgress = false;
      updateControlStates();
    }
  }

  stopBtn.addEventListener("click", async () => {
    invalidateExecutionNotificationCycle();
    await performStopAndReset({ automatic: false });
  });

  executionSuccessToastClose?.addEventListener("click", hideExecutionSuccessToast);

  async function loadExampleByName(name) {
    if (guardMenuAction()) return;
    try {
      const data = await api.getExample(name);
      codeEditor.value = data.source;
      setScriptName(name);
      clearBreakpoints();
      clearDebugState();
      hideAutocomplete();
      updateSyntaxHighlight();
      log("");
    } catch (err) {
      log(err.message);
    }
  }

  async function loadWorldByName(name) {
    if (guardMenuAction()) return;
    try {
      const data = await api.loadWorld(name);
      selectedWorldName = name;
      selectedBlankWorld = false;
      currentWorld = data.world || currentWorld;
      if (statusWorld) statusWorld.textContent = name;
      robotStart = robotStartFromLoadedWorld(currentWorld);
      robotStartPreview = null;
      showRobotStartMarker = Boolean(robotStart);
      updateRobotStartReadout();
      await refreshSnapshot();
      redrawCanvas();
      log("");
    } catch (err) {
      log(err.message);
    }
  }

  async function loadBlankWorld() {
    if (guardMenuAction()) return;
    try {
      const data = await api.loadBlankWorld({ width_cells: 40, height_cells: 40 });
      selectedWorldName = null;
      selectedBlankWorld = true;
      currentWorld = data.world || currentWorld;
      if (statusWorld) statusWorld.textContent = "Mundo en blanco";
      robotStart = null;
      showRobotStartMarker = false;
      updateRobotStartReadout();
      await refreshSnapshot();
      redrawCanvas();
      log("Mundo en blanco cargado.");
    } catch (err) {
      log(err.message);
    }
  }

  function setRobotStartMode(enabled) {
    robotStartMode = enabled;
    placeRobotStartBtn.classList.toggle("tool-active", enabled);
    if (enabled) showRobotStartMarker = true;
    if (enabled) {
      robotStartReadout.textContent = "Haz clic en el canvas para fijar la pose.";
      return;
    }
    robotStartPreview = null;
    updateRobotStartReadout();
  }

  function hideRobotStartMarker() {
    robotStartMode = false;
    robotStartPreview = null;
    showRobotStartMarker = false;
    placeRobotStartBtn.classList.remove("tool-active");
    redrawCanvas();
  }

  function updateRobotStartReadout(point = null) {
    const pose = point || robotStart;
    if (!pose) {
      robotStartReadout.textContent = "Pose inicial no fijada";
      return;
    }
    robotStartReadout.textContent =
      `X ${formatDistanceCm(pose.x_mm, 1)} cm, Y ${formatDistanceCm(pose.y_mm, 1)} cm, ` +
      `theta ${pose.theta_deg.toFixed(0)} °`;
  }

  async function applyRobotStart(point) {
    const theta = Number(robotThetaInput.value || 0);
    const pose = { x_mm: point.xMm, y_mm: point.yMm, theta_deg: theta };
    try {
      await api.setRobotStart(pose);
      robotStart = pose;
      robotStartPreview = null;
      showRobotStartMarker = true;
      window.EV3Canvas.resetTrail(pose);
      updateRobotStartReadout();
      setRobotStartMode(false);
      log("Pose inicial actualizada.");
      await refreshSnapshot();
    } catch (err) {
      log(err.message);
    }
  }

  async function loadScenario(key) {
    if (guardMenuAction()) return;
    const scenario = scenarios[key];
    if (!scenario) return;
    try {
      await loadWorldByName(scenario.world);
      await loadExampleByName(scenario.example);
      log(`Escenario cargado: ${scenario.label}`);
    } catch (err) {
      log(err.message);
    }
  }

  async function loadMission(mission) {
    if (guardMenuAction()) return;
    await loadWorldByName(mission.world_file);
    await loadExampleByName(mission.starter_script);
    await api.selectMission(mission.id);
    if (missionResultEl) missionResultEl.hidden = true;
    log(`Misión cargada: ${mission.title}`);
  }

  function renderMissionResult(payload) {
    if (!missionResultEl || !payload?.result) return;
    const result = payload.result;
    const completed = payload.outcome === "finished" && result.passed;
    const label = completed ? "Misión completada" : payload.outcome === "cancelled" ? "Misión cancelada" : "Misión no superada";
    const criteria = (result.criteria || []).map((item) => `${item.passed ? "✓" : "✗"} ${item.id}`).join(" · ");
    missionResultEl.textContent = `${label}: ${result.score || 0} puntos. ${criteria}`;
    missionResultEl.className = `mission-result ${completed ? "mission-result-success" : "mission-result-failure"}`;
    missionResultEl.hidden = false;
  }

  async function downloadScript() {
    if (guardMenuAction()) return;
    const suggestedName = (currentScriptName && currentScriptName.endsWith(".py"))
      ? currentScriptName
      : "ev3_script.py";

    if (typeof window.showSaveFilePicker === "function") {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName,
          types: [
            {
              description: "Python",
              accept: {
                "text/x-python": [".py"],
                "text/plain": [".py"],
              },
            },
          ],
        });
        const writable = await handle.createWritable();
        await writable.write(codeEditor.value);
        await writable.close();
        setScriptName(handle.name || suggestedName);
        setSavePath(handle.name || suggestedName);
        log(`Script guardado: ${handle.name || suggestedName}. Ubicacion: seleccionada en el dialogo del sistema.`);
        return;
      } catch (err) {
        if (err?.name === "AbortError") {
          log("Guardado cancelado.");
          return;
        }
      }
    }

    const blob = new Blob([codeEditor.value], { type: "text/x-python;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = suggestedName;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    setSavePath("Descargas (navegador)");
    log(`Script descargado: ${suggestedName}. Ubicacion: Descargas del navegador.`);
  }

  function createNewScript() {
    if (guardMenuAction()) return;
    codeEditor.value = defaultScript;
    setScriptName("editor_actual.py");
    clearBreakpoints();
    clearDebugState();
    hideAutocomplete();
    updateSyntaxHighlight();
    log("Nuevo script creado.");
  }

  function openScriptFromDevice() {
    if (guardMenuAction()) return;
    scriptFileInput.click();
  }

  function handleGlobalShortcuts(event) {
    if (event.defaultPrevented || event.isComposing) return;
    const isCmdOrCtrl = event.ctrlKey || event.metaKey;
    if (!isCmdOrCtrl || event.altKey) return;

    const key = String(event.key || "").toLowerCase();
    if (key === "n") {
      event.preventDefault();
      createNewScript();
      return;
    }
    if (key === "o") {
      event.preventDefault();
      openScriptFromDevice();
      return;
    }
    if (key === "s") {
      event.preventDefault();
      void downloadScript();
    }
  }

  document.getElementById("newScriptMenuBtn").addEventListener("click", createNewScript);

  document.getElementById("openScriptMenuBtn").addEventListener("click", openScriptFromDevice);

  window.EV3FileInputController.bind(scriptFileInput, async (file) => {
    try {
      codeEditor.value = await file.text();
      setScriptName(file.name);
      clearBreakpoints();
      clearDebugState();
      hideAutocomplete();
      updateSyntaxHighlight();
      log(`Script cargado: ${file.name}`);
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("saveScriptMenuBtn").addEventListener("click", () => {
    void downloadScript();
  });

  window.EV3FileInputController.bind(worldFileInput, async (file) => {
    if (guardMenuAction()) {
      return;
    }
    try {
      const data = await api.uploadWorld(file);
      currentWorld = data.world || currentWorld;
      if (statusWorld) statusWorld.textContent = data.loaded_world || file.name;
      robotStart = null;
      showRobotStartMarker = false;
      updateRobotStartReadout();
      await refreshSnapshot();
      redrawCanvas();
      log(`Mundo cargado: ${data.loaded_world || file.name}`);
    } catch (err) {
      log(err.message);
    }
  });

  aboutMenuBtn?.addEventListener("click", () => {
    aboutDialogController.open();
    log("Simulador EV3 Web - migracion Flask del simulador Tkinter.");
  });


  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && aboutDialogController.isOpen()) {
      aboutDialogController.close();
    }
  });

  document.getElementById("scenariosMenu").addEventListener("click", async (event) => {
    const key = event.target?.dataset?.scenario;
    if (key) await loadScenario(key);
  });

  worldsMenu?.addEventListener("click", (event) => {
    const target = event.target;
    if (!target || target.tagName !== "A") return;
    if (!executionMenuLocked) return;
    event.preventDefault();
    log(MENU_LOCK_MESSAGE);
  });

  placeRobotStartBtn.addEventListener("click", () => {
    setRobotStartMode(!robotStartMode);
  });

  robotThetaInput.addEventListener("change", async () => {
    if (!robotStart) return;
    robotStart.theta_deg = Number(robotThetaInput.value || 0);
    try {
      await api.setRobotStart(robotStart);
      updateRobotStartReadout();
      await refreshSnapshot();
    } catch (err) {
      log(err.message);
    }
  });

  mapZoomInBtn?.addEventListener("click", () => {
    applyMapZoom("in");
  });

  mapZoomOutBtn?.addEventListener("click", () => {
    applyMapZoom("out");
  });

  mapZoomResetBtn?.addEventListener("click", () => {
    applyMapZoom("reset");
  });

  canvas.addEventListener("mousemove", (event) => {
    if (!robotStartMode) return;
    const point = window.EV3Canvas.canvasToWorld(canvas, event.clientX, event.clientY, currentWorld);
    robotStartPreview = {
      x_mm: point.xMm,
      y_mm: point.yMm,
      theta_deg: Number(robotThetaInput.value || 0),
    };
    updateRobotStartReadout(robotStartPreview);
    redrawCanvas();
  });

  canvas.addEventListener("click", async (event) => {
    if (!robotStartMode) return;
    const point = window.EV3Canvas.canvasToWorld(canvas, event.clientX, event.clientY, currentWorld);
    await applyRobotStart(point);
  });

  canvas.addEventListener("wheel", async (event) => {
    if (!robotStartMode) return;
    event.preventDefault();
    const delta = event.deltaY < 0 ? 15 : -15;
    robotThetaInput.value = String((Number(robotThetaInput.value || 0) + delta + 360) % 360);
    const point = window.EV3Canvas.canvasToWorld(canvas, event.clientX, event.clientY, currentWorld);
    robotStartPreview = {
      x_mm: point.xMm,
      y_mm: point.yMm,
      theta_deg: Number(robotThetaInput.value || 0),
    };
    updateRobotStartReadout(robotStartPreview);
    redrawCanvas();
  }, { passive: false });

  window.EV3EditorInteractionController.bind(codeEditor, {
    input: () => {
    syncEditorMetrics();
    renderEditorGutter();
    updateSyntaxHighlight();
    placeAutocompletePopup();
    },
    keydown: (event) => {
    handleAutocompleteKeys(event) || handleEditorTab(event) || handleEditorEnter(event) || handleEditorPairs(event);
    },
    keyup: (event) => {
    placeAutocompletePopup();
    if (event.key === ".") showAutocomplete(true);
    },
    blur: () => {
    window.setTimeout(hideAutocomplete, 120);
    },
    scroll: () => {
    editorGutter.scrollTop = codeEditor.scrollTop;
    syntaxHighlight.scrollTop = codeEditor.scrollTop;
    syntaxHighlight.scrollLeft = codeEditor.scrollLeft;
    placeAutocompletePopup();
    },
  });

  breakpointsInput.addEventListener("change", parseBreakpoints);
  watchesInput?.addEventListener("change", async () => {
    try {
      await applyWatchesToSession();
      setDebugState(`watches: ${watchExpressions.join(" | ") || "ninguno"}`);
    } catch (err) {
      log(err.message);
    }
  });

  editorGutter.addEventListener("click", (event) => {
    if (breakpointsInput?.disabled) return;
    const line = Number.parseInt(event.target?.dataset?.line || "", 10);
    if (Number.isInteger(line) && line > 0) toggleBreakpoint(line);
  });

  syncEditorMetrics();
  renderEditorGutter();
  updateSyntaxHighlight();
  updateControlStates();
  window.EV3SpeakerAudio.bindUnlockGesture();
  startSnapshotWatchdog();
  window.addEventListener("resize", syncEditorMetrics);
  window.addEventListener("resize", renderEditorGutter);
  window.addEventListener("resize", placeAutocompletePopup);
  window.addEventListener("load", () => {
    syncEditorMetrics();
    renderEditorGutter();
    placeAutocompletePopup();
  });
  if (document.fonts?.addEventListener) {
    document.fonts.addEventListener("loadingdone", () => {
      syncEditorMetrics();
      renderEditorGutter();
      placeAutocompletePopup();
    });
  }

  window.EV3PageLifecycleController.bind({
    stopLiveUpdates,
    closeSession: api.closeSessionOnUnload,
    recoverLiveState: async () => {
      stopLiveUpdates();
      startSnapshotStream();
      await refreshSnapshot();
      log("Sesion recuperada. Reconexion de estado en vivo.");
    },
    onRecoveryError: () => {},
  });

  window.addEventListener("keydown", handleGlobalShortcuts, true);

  window.EV3ProfileControls.bind(api, log);
  window.EV3RuntimeLimitControls.bind(api, log);

  window.EV3TraceControls.bind(api, log, refreshSnapshot);
  try {
    await init();
  } catch (err) {
    log(err.message);
  }
})();
