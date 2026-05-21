(async () => {
  const api = window.EV3Api;
  const canvas = document.getElementById("worldCanvas");
  const codeEditor = document.getElementById("codeEditor");
  const editorGutter = document.getElementById("editorGutter");
  const syntaxHighlight = document.getElementById("syntaxHighlight");
  const autocompletePopup = document.getElementById("autocompletePopup");
  const statusEl = document.getElementById("sessionStatus");
  const consoleEl = document.getElementById("console");
  const exampleSelect = document.getElementById("exampleSelect");
  const worldSelect = document.getElementById("worldSelect");
  const statusWorld = document.getElementById("statusWorld");
  const examplesMenu = document.getElementById("examplesMenu");
  const worldsMenu = document.getElementById("worldsMenu");
  const scriptFileInput = document.getElementById("scriptFileInput");
  const placeRobotStartBtn = document.getElementById("placeRobotStartBtn");
  const robotThetaInput = document.getElementById("robotThetaInput");
  const robotStartReadout = document.getElementById("robotStartReadout");
  const breakpointsInput = document.getElementById("breakpointsInput");
  const debugState = document.getElementById("debugState");
  const defaultScript = codeEditor.value;
  const scenarios = {
    line: {
      label: "Seguidor de linea",
      world: "01_linea_negra.json",
      example: "06_siguelineas_basico.py",
    },
    ultrasonic: {
      label: "Ultrasonido + obstaculos",
      world: "02_obstaculos_beacon.json",
      example: "05_esquiva_obstaculos.py",
    },
    brick: {
      label: "Test pantalla/altavoz",
      world: "02_obstaculos_beacon.json",
      example: "12_pantalla_altavoz_test.py",
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
  const syntaxBuiltins = new Set([
    "print", "len", "range", "str", "int", "float", "list", "dict", "set",
    "tuple", "type", "EV3Brick", "Motor", "ColorSensor", "UltrasonicSensor",
    "TouchSensor", "GyroSensor", "DriveBase", "Port", "Color", "wait",
  ]);
  let currentWorld = null;
  let currentStatus = "created";
  let gutterBreakpoints = new Set();
  let currentDebugLine = null;
  let robotStartMode = false;
  let robotStart = null;
  let robotStartPreview = null;
  let latestSnapshot = null;
  let timer = null;
  let stream = null;
  let usingPollingFallback = false;
  let recoveringSession = false;
  let autocompleteItems = [];
  let autocompleteSelected = 0;

  function log(message) {
    consoleEl.textContent = message || "";
  }

  function setStatus(status) {
    currentStatus = status || currentStatus;
    statusEl.textContent = status;
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

  function formatDebugEvent(payload) {
    if (!payload || !payload.type) return "";
    if (payload.type === "paused") {
      return `pausado en linea ${payload.line} (${payload.reason || "debug"})`;
    }
    if (payload.type === "line" && payload.pause_reason) {
      return `linea ${payload.line}: ${payload.pause_reason}`;
    }
    if (payload.type === "breakpoints") {
      return `breakpoints: ${(payload.breakpoints || []).join(", ") || "ninguno"}`;
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
    if (payload?.line) {
      currentDebugLine = payload.line;
      renderEditorGutter();
    }
  }

  function lineCount() {
    return Math.max(1, codeEditor.value.split("\n").length);
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
      distance_mm: " mm",
      angle: " deg",
      speed: " dps",
    }[key] || "";
  }

  function renderMotorTelemetry(motor) {
    const state = escapeHtml(motor.state || "IDLE");
    return `
      <article class="telemetry-card motor-card">
        <div class="telemetry-card-title">
          <span>Motor ${escapeHtml(motor.port)}</span>
          <span class="telemetry-state">${state}</span>
        </div>
        <div class="motor-metrics">
          <span><b>Vel.</b> ${formatTelemetryNumber(motor.speed)} dps</span>
          <span><b>Angulo</b> ${formatTelemetryNumber(motor.angle)} deg</span>
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
          <dd>${formatTelemetryValue(item)}${sensorUnit(key)}</dd>
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

  function highlightCodeLine(line) {
    const escaped = escapeHtml(line);
    const commentIndex = escaped.indexOf("#");
    const code = commentIndex >= 0 ? escaped.slice(0, commentIndex) : escaped;
    const comment = commentIndex >= 0 ? escaped.slice(commentIndex) : "";
    const highlighted = code.replace(
      /("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b\d+(?:\.\d+)?\b|\b[A-Za-z_]\w*\b)/g,
      (token) => {
        if (/^["']/.test(token)) return `<span class="syntax-string">${token}</span>`;
        if (/^\d/.test(token)) return `<span class="syntax-number">${token}</span>`;
        if (syntaxKeywords.has(token)) return `<span class="syntax-kw">${token}</span>`;
        if (syntaxBuiltins.has(token)) return `<span class="syntax-builtin">${token}</span>`;
        return token;
      },
    );
    if (!comment) return highlighted;
    return `${highlighted}<span class="syntax-comment">${comment}</span>`;
  }

  function updateSyntaxHighlight() {
    syntaxHighlight.innerHTML = codeEditor.value
      .split("\n")
      .map(highlightCodeLine)
      .join("\n");
    syntaxHighlight.scrollTop = codeEditor.scrollTop;
    syntaxHighlight.scrollLeft = codeEditor.scrollLeft;
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
  }

  function applyAutocomplete(index = autocompleteSelected) {
    const value = autocompleteItems[index];
    if (!value) return;
    const replaceFrom = Number.parseInt(autocompletePopup.dataset.replaceFrom || `${codeEditor.selectionStart}`, 10);
    const replaceTo = codeEditor.selectionStart;
    codeEditor.setRangeText(value, replaceFrom, replaceTo, "end");
    hideAutocomplete();
    renderEditorGutter();
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
    const session = await api.createSession();
    setStatus(session.status);
    await loadExamples();
    await loadWorlds();
    await loadWorldFromUrl();
    startSnapshotStream();
  }

  async function loadExamples() {
    const data = await api.listExamples();
    exampleSelect.innerHTML = "<option value=''>Seleccionar ejemplo</option>";
    examplesMenu.innerHTML = "";
    for (const item of data.examples) {
      const option = document.createElement("option");
      option.value = item.name;
      option.textContent = item.name;
      exampleSelect.appendChild(option);
      examplesMenu.appendChild(menuButton(item.name, () => loadExampleByName(item.name)));
    }
    if (!data.examples.length) {
      examplesMenu.innerHTML = '<span class="menu-empty">No hay ejemplos</span>';
    }
  }

  async function loadWorlds() {
    const data = await api.listWorlds();
    worldSelect.innerHTML = "<option value=''>Seleccionar mundo</option>";
    worldsMenu.innerHTML = '<a href="/worlds">Editor de mundos</a>';
    for (const item of data.worlds) {
      const option = document.createElement("option");
      option.value = item.name;
      option.textContent = item.name;
      worldSelect.appendChild(option);
      worldsMenu.appendChild(menuButton(item.name, () => loadWorldByName(item.name)));
    }
    if (!data.worlds.length) {
      const empty = document.createElement("span");
      empty.className = "menu-empty";
      empty.textContent = "No hay mundos";
      worldsMenu.appendChild(empty);
    }
  }

  function menuButton(label, action) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.addEventListener("click", action);
    return button;
  }

  async function loadWorldFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const worldName = params.get("world");
    if (!worldName) return;
    const option = Array.from(worldSelect.options).find((item) => item.value === worldName);
    if (!option) {
      log(`Mundo no encontrado: ${worldName}`);
      return;
    }
    worldSelect.value = worldName;
    await loadSelectedWorld();
  }

  async function refreshSnapshot() {
    if (!api.sessionId) return;
    try {
      const data = await api.snapshot();
      setStatus(data.status);
      if (data.error) {
        log(`${data.error.error || "Error"}\n${data.error.traceback || ""}`);
      }
      renderSnapshot(data.snapshot);
    } catch (err) {
      if (isSessionLost(err)) {
        await recoverSession();
        return;
      }
      log(err.message);
    }
  }

  function startSnapshotStream() {
    if (stream || !window.EventSource) {
      startPollingFallback();
      return;
    }
    stream = api.openSnapshotStream({
      snapshot: renderSnapshot,
      status: (payload) => setStatus(payload.status || ""),
      debug: handleDebug,
      error: (payload) => log(`${payload.error || "Error"}\n${payload.traceback || ""}`),
      world: (payload) => {
        currentWorld = payload;
      },
      connectionError: () => {
        if (stream) {
          stream.close();
          stream = null;
        }
        startPollingFallback();
      },
    });
  }

  function startPollingFallback() {
    if (usingPollingFallback) return;
    usingPollingFallback = true;
    timer = setInterval(refreshSnapshot, 120);
    refreshSnapshot();
  }

  function stopLiveUpdates() {
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

  function isSessionLost(err) {
    return err?.status === 404 || err?.code === "SESSION_NOT_FOUND";
  }

  async function recoverSession() {
    if (recoveringSession) return;
    recoveringSession = true;
    try {
      stopLiveUpdates();
      const session = await api.createSession();
      setStatus(session.status);
      currentWorld = null;
      startSnapshotStream();
      log("Sesion recreada.");
    } catch (err) {
      log(err.message);
    } finally {
      recoveringSession = false;
    }
  }

  function renderSnapshot(snapshot) {
    latestSnapshot = snapshot;
    updateTelemetry(snapshot);
    updateBrick(snapshot);
    redrawCanvas();
  }

  function redrawCanvas() {
    window.EV3Canvas.draw(canvas, latestSnapshot, currentWorld, {
      robotStart: robotStartMode ? robotStartPreview : robotStart,
    });
  }

  function updateTelemetry(snapshot) {
    const telemetry = document.getElementById("telemetry");
    if (!snapshot) return;
    const robot = snapshot.robot || {};
    telemetry.innerHTML = `
      <dt>Tick</dt><dd>${snapshot.tick}</dd>
      <dt>Tiempo</dt><dd>${snapshot.sim_time_s}s</dd>
      <dt>X</dt><dd>${formatTelemetryNumber(robot.x_mm)} mm</dd>
      <dt>Y</dt><dd>${formatTelemetryNumber(robot.y_mm)} mm</dd>
      <dt>Theta</dt><dd>${formatTelemetryNumber(robot.theta_deg)} deg</dd>
      <dt>Colision</dt><dd>${snapshot.colliding ? "si" : "no"}</dd>
    `;
    const motors = document.getElementById("motors");
    const motorItems = snapshot.motors || [];
    motors.innerHTML = motorItems.length
      ? motorItems.map(renderMotorTelemetry).join("")
      : '<p class="telemetry-empty">Sin motores</p>';
    const sensors = document.getElementById("sensors");
    const sensorItems = snapshot.sensors || [];
    sensors.innerHTML = sensorItems.length
      ? sensorItems.map(renderSensorTelemetry).join("")
      : '<p class="telemetry-empty">Sin sensores</p>';
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
    const lines = snapshot.brick.screen?.lines || [];
    document.getElementById("screen").textContent = lines.join("\n");
    const speaker = snapshot.brick.speaker;
    const speakerEl = document.getElementById("speaker");
    if (!speakerEl) return;
    if (speaker) {
      speakerEl.textContent =
        `${speaker.freq || 0} Hz, ${Math.round(speaker.duration_ms || 0)} ms, ` +
        `vol ${speaker.volume ?? 50}`;
    } else {
      speakerEl.textContent = "Inactivo";
    }
  }

  document.getElementById("runBtn").addEventListener("click", async () => {
    try {
      await api.loadScript(codeEditor.value);
      const result = await api.start();
      setStatus(result.status);
      log("");
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("debugRunBtn").addEventListener("click", async () => {
    try {
      await api.loadScript(codeEditor.value);
      const result = await api.setBreakpoints(parseBreakpoints());
      setDebugState(`breakpoints: ${result.breakpoints.join(", ") || "ninguno"}`);
      setStatus((await api.start({ debug: true })).status);
      log("");
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("debugStepBtn").addEventListener("click", async () => {
    try {
      if (!["running", "paused"].includes(currentStatus)) {
        await api.loadScript(codeEditor.value);
        await api.setBreakpoints(parseBreakpoints());
        setStatus((await api.start({ debug: true, step_mode: true })).status);
      } else {
        await api.debugStep();
      }
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("debugContinueBtn").addEventListener("click", async () => {
    try {
      await api.debugContinue();
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("pauseBtn").addEventListener("click", async () => {
    try { setStatus((await api.pause()).status); } catch (err) { log(err.message); }
  });
  document.getElementById("resumeBtn").addEventListener("click", async () => {
    try { setStatus((await api.resume()).status); } catch (err) { log(err.message); }
  });
  document.getElementById("stopBtn").addEventListener("click", async () => {
    try { setStatus((await api.stop()).status); } catch (err) { log(err.message); }
  });
  document.getElementById("resetBtn").addEventListener("click", async () => {
    try {
      setStatus((await api.reset()).status);
      setDebugState("");
    } catch (err) { log(err.message); }
  });

  exampleSelect.addEventListener("change", async () => {
    if (!exampleSelect.value) return;
    await loadExampleByName(exampleSelect.value);
  });

  async function loadExampleByName(name) {
    try {
      const data = await api.getExample(name);
      codeEditor.value = data.source;
      exampleSelect.value = name;
      currentDebugLine = null;
      hideAutocomplete();
      renderEditorGutter();
      updateSyntaxHighlight();
      log("");
    } catch (err) {
      log(err.message);
    }
  }

  document.getElementById("loadWorldBtn").addEventListener("click", async () => {
    await loadSelectedWorld();
  });

  async function loadSelectedWorld() {
    if (!worldSelect.value) return;
    await loadWorldByName(worldSelect.value);
  }

  async function loadWorldByName(name) {
    try {
      const data = await api.loadWorld(name);
      currentWorld = data.world;
      worldSelect.value = name;
      if (statusWorld) statusWorld.textContent = name;
      robotStart = null;
      updateRobotStartReadout();
      log("");
    } catch (err) {
      log(err.message);
    }
  }

  function setRobotStartMode(enabled) {
    robotStartMode = enabled;
    placeRobotStartBtn.classList.toggle("tool-active", enabled);
    if (enabled) {
      robotStartReadout.textContent = "Haz clic en el canvas para fijar la pose.";
      return;
    }
    robotStartPreview = null;
    updateRobotStartReadout();
  }

  function updateRobotStartReadout(point = null) {
    const pose = point || robotStart;
    if (!pose) {
      robotStartReadout.textContent = "Pose inicial no fijada";
      return;
    }
    robotStartReadout.textContent =
      `X ${pose.x_mm.toFixed(1)} mm, Y ${pose.y_mm.toFixed(1)} mm, ` +
      `theta ${pose.theta_deg.toFixed(0)} deg`;
  }

  async function applyRobotStart(point) {
    const theta = Number(robotThetaInput.value || 0);
    const pose = { x_mm: point.xMm, y_mm: point.yMm, theta_deg: theta };
    try {
      await api.setRobotStart(pose);
      robotStart = pose;
      robotStartPreview = null;
      updateRobotStartReadout();
      setRobotStartMode(false);
      log("Pose inicial actualizada.");
      await refreshSnapshot();
    } catch (err) {
      log(err.message);
    }
  }

  async function loadScenario(key) {
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

  function downloadScript() {
    const blob = new Blob([codeEditor.value], { type: "text/x-python;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "ev3_script.py";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  document.getElementById("newScriptMenuBtn").addEventListener("click", () => {
    codeEditor.value = defaultScript;
    gutterBreakpoints.clear();
    currentDebugLine = null;
    hideAutocomplete();
    updateBreakpointsInput();
    renderEditorGutter();
    updateSyntaxHighlight();
    setDebugState("");
    log("Nuevo script creado.");
  });

  document.getElementById("openScriptMenuBtn").addEventListener("click", () => {
    scriptFileInput.click();
  });

  document.getElementById("openScriptMenuBtnTop")?.addEventListener("click", () => {
    scriptFileInput.click();
  });

  scriptFileInput.addEventListener("change", async () => {
    const [file] = scriptFileInput.files || [];
    if (!file) return;
    try {
      codeEditor.value = await file.text();
      currentDebugLine = null;
      hideAutocomplete();
      renderEditorGutter();
      updateSyntaxHighlight();
      log(`Script cargado: ${file.name}`);
    } catch (err) {
      log(err.message);
    } finally {
      scriptFileInput.value = "";
    }
  });

  document.getElementById("saveScriptMenuBtn").addEventListener("click", downloadScript);
  document.getElementById("saveScriptMenuBtnTop")?.addEventListener("click", downloadScript);

  document.getElementById("aboutMenuBtn").addEventListener("click", () => {
    log("Simulador EV3 Web - migracion Flask del simulador Tkinter.");
  });

  document.getElementById("scenariosMenu").addEventListener("click", async (event) => {
    const key = event.target?.dataset?.scenario;
    if (key) await loadScenario(key);
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

  codeEditor.addEventListener("input", () => {
    renderEditorGutter();
    updateSyntaxHighlight();
  });
  codeEditor.addEventListener("keydown", (event) => {
    handleAutocompleteKeys(event) || handleEditorEnter(event) || handleEditorPairs(event);
  });
  codeEditor.addEventListener("keyup", (event) => {
    if (event.key === ".") showAutocomplete(true);
  });
  codeEditor.addEventListener("blur", () => {
    window.setTimeout(hideAutocomplete, 120);
  });
  codeEditor.addEventListener("scroll", () => {
    editorGutter.scrollTop = codeEditor.scrollTop;
    syntaxHighlight.scrollTop = codeEditor.scrollTop;
    syntaxHighlight.scrollLeft = codeEditor.scrollLeft;
  });

  breakpointsInput.addEventListener("change", parseBreakpoints);

  editorGutter.addEventListener("click", (event) => {
    const line = Number.parseInt(event.target?.dataset?.line || "", 10);
    if (Number.isInteger(line) && line > 0) toggleBreakpoint(line);
  });

  renderEditorGutter();
  updateSyntaxHighlight();

  window.addEventListener("beforeunload", () => {
    stopLiveUpdates();
  });

  try {
    await init();
  } catch (err) {
    log(err.message);
  }
})();
