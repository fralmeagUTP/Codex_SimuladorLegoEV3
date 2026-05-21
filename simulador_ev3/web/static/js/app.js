(async () => {
  const api = window.EV3Api;
  const canvas = document.getElementById("worldCanvas");
  const codeEditor = document.getElementById("codeEditor");
  const statusEl = document.getElementById("sessionStatus");
  const consoleEl = document.getElementById("console");
  const exampleSelect = document.getElementById("exampleSelect");
  const worldSelect = document.getElementById("worldSelect");
  const assetSelect = document.getElementById("assetSelect");
  const selectedAssetEl = document.getElementById("selectedAsset");
  const assetPropertiesEl = document.getElementById("assetProperties");
  const moveAssetBtn = document.getElementById("moveAssetBtn");
  const placeRobotStartBtn = document.getElementById("placeRobotStartBtn");
  const robotThetaInput = document.getElementById("robotThetaInput");
  const robotStartReadout = document.getElementById("robotStartReadout");
  let currentWorld = null;
  let editorWorld = null;
  let selectedPlacement = null;
  let moveMode = false;
  let robotStartMode = false;
  let robotStart = null;
  let timer = null;
  let stream = null;
  let usingPollingFallback = false;
  let recoveringSession = false;

  function log(message) {
    consoleEl.textContent = message || "";
  }

  function setStatus(status) {
    statusEl.textContent = status;
  }

  async function init() {
    const session = await api.createSession();
    setStatus(session.status);
    await loadExamples();
    await loadWorlds();
    await loadAssets();
    await createEditorWorld();
    startSnapshotStream();
  }

  async function loadExamples() {
    const data = await api.listExamples();
    exampleSelect.innerHTML = "<option value=''>Seleccionar ejemplo</option>";
    for (const item of data.examples) {
      const option = document.createElement("option");
      option.value = item.name;
      option.textContent = item.name;
      exampleSelect.appendChild(option);
    }
  }

  async function loadWorlds() {
    const data = await api.listWorlds();
    worldSelect.innerHTML = "<option value=''>Seleccionar mundo</option>";
    for (const item of data.worlds) {
      const option = document.createElement("option");
      option.value = item.name;
      option.textContent = item.name;
      worldSelect.appendChild(option);
    }
  }

  async function loadAssets() {
    const data = await api.getEditorAssets();
    assetSelect.innerHTML = "<option value=''>Seleccionar asset</option>";
    const groups = {
      robot: "Robot",
      wall: "Muros",
      line: "Lineas",
      zone: "Zonas",
      floor: "Pisos",
    };
    for (const item of data.assets) {
      const option = document.createElement("option");
      option.value = item.key;
      option.textContent = `${groups[item.type] || item.type}: ${item.key}`;
      assetSelect.appendChild(option);
    }
  }

  async function createEditorWorld() {
    const data = await api.createEditorWorld(20, 20);
    setEditorWorld(data.world);
    showValidation(data.validation);
  }

  function setEditorWorld(world) {
    editorWorld = world;
    currentWorld = editorWorldToRenderWorld(world);
  }

  function editorWorldToRenderWorld(world) {
    if (!world) return currentWorld;
    return {
      width_mm: (world.world_width_cells || 20) * 100,
      height_mm: (world.world_height_cells || 20) * 100,
      surface: { cell_size_mm: 100, default_color: "WHITE", cells: [] },
      obstacles: [],
      beacons: [],
      editor_spec: world,
    };
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
      error: (payload) => log(`${payload.error || "Error"}\n${payload.traceback || ""}`),
      world: (payload) => {
        currentWorld = payload;
        editorWorld = payload?.editor_spec || editorWorld;
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
      await createEditorWorld();
      updateSelection(null);
      robotStart = null;
      updateRobotStartReadout();
      startSnapshotStream();
      log("Sesion recreada.");
    } catch (err) {
      log(err.message);
    } finally {
      recoveringSession = false;
    }
  }

  function renderSnapshot(snapshot) {
    updateTelemetry(snapshot);
    updateBrick(snapshot);
    window.EV3Canvas.draw(canvas, snapshot, currentWorld, {
      selectedPlacementId: selectedPlacement?.id || null,
      robotStart,
    });
  }

  function updateTelemetry(snapshot) {
    const telemetry = document.getElementById("telemetry");
    if (!snapshot) return;
    const robot = snapshot.robot || {};
    telemetry.innerHTML = `
      <dt>Tick</dt><dd>${snapshot.tick}</dd>
      <dt>Tiempo</dt><dd>${snapshot.sim_time_s}s</dd>
      <dt>X</dt><dd>${robot.x_mm}</dd>
      <dt>Y</dt><dd>${robot.y_mm}</dd>
      <dt>Theta</dt><dd>${robot.theta_deg}</dd>
      <dt>Colision</dt><dd>${snapshot.colliding ? "si" : "no"}</dd>
    `;
    const motors = document.getElementById("motors");
    motors.innerHTML = "<h3>Motores</h3>" + (snapshot.motors || [])
      .map((m) => `<div>${m.port}: ${m.speed} dps, ${m.angle} deg, ${m.state}</div>`)
      .join("");
    const sensors = document.getElementById("sensors");
    sensors.innerHTML = "<h3>Sensores</h3>" + (snapshot.sensors || [])
      .map((s) => `<div>${s.port}: ${s.type} = ${JSON.stringify(s.value)}</div>`)
      .join("");
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
    const lines = snapshot.brick.screen?.lines || [];
    document.getElementById("screen").textContent = lines.join("\n");
  }

  function updateSelection(placement) {
    selectedPlacement = placement;
    moveMode = false;
    moveAssetBtn.classList.remove("tool-active");
    selectedAssetEl.textContent = placement
      ? `${placement.id} (${placement.asset_key})`
      : "Sin seleccion";
    if (!placement) {
      assetPropertiesEl.innerHTML = "";
      return;
    }
    assetPropertiesEl.innerHTML = `
      <dt>ID</dt><dd>${placement.id}</dd>
      <dt>Asset</dt><dd>${placement.asset_key}</dd>
      <dt>X</dt><dd>${placement.x ?? placement.x_px ?? 0}</dd>
      <dt>Y</dt><dd>${placement.y ?? placement.y_px ?? 0}</dd>
      <dt>Rotacion</dt><dd>${placement.rotation || 0}</dd>
    `;
  }

  function setRobotStartMode(enabled) {
    robotStartMode = enabled;
    placeRobotStartBtn.classList.toggle("tool-active", enabled);
    if (enabled) {
      moveMode = false;
      moveAssetBtn.classList.remove("tool-active");
      robotStartReadout.textContent = "Haz clic en el canvas";
    } else if (!robotStart) {
      robotStartReadout.textContent = "Pose no fijada";
    }
  }

  function updateRobotStartReadout() {
    if (!robotStart) {
      robotStartReadout.textContent = "Pose no fijada";
      return;
    }
    robotStartReadout.textContent =
      `X ${robotStart.x_mm.toFixed(1)} mm, Y ${robotStart.y_mm.toFixed(1)} mm, ` +
      `${robotStart.theta_deg.toFixed(0)} deg`;
  }

  function refreshSelectedFromWorld() {
    if (!selectedPlacement || !editorWorld?.placements) return;
    const updated = editorWorld.placements.find((p) => p.id === selectedPlacement.id);
    selectedPlacement = updated || null;
    updateSelection(selectedPlacement);
  }

  function showValidation(validation) {
    if (!validation) return;
    const errors = validation.errors || [];
    const warnings = validation.warnings || [];
    if (!errors.length && !warnings.length) {
      log("Mundo valido.");
      return;
    }
    const lines = [];
    if (errors.length) {
      lines.push("Errores:");
      for (const err of errors) lines.push(`- ${err.code}: ${err.message}`);
    }
    if (warnings.length) {
      lines.push("Advertencias:");
      for (const warn of warnings) lines.push(`- ${warn.code}: ${warn.message}`);
    }
    log(lines.join("\n"));
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
    try { setStatus((await api.reset()).status); } catch (err) { log(err.message); }
  });

  exampleSelect.addEventListener("change", async () => {
    if (!exampleSelect.value) return;
    try {
      const data = await api.getExample(exampleSelect.value);
      codeEditor.value = data.source;
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("loadWorldBtn").addEventListener("click", async () => {
    if (!worldSelect.value) return;
    try {
      const data = await api.loadWorld(worldSelect.value);
      currentWorld = data.world;
      editorWorld = data.world?.editor_spec || editorWorld;
      log("");
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("newWorldBtn").addEventListener("click", async () => {
    try {
      const data = await api.createEditorWorld(20, 20);
      setEditorWorld(data.world);
      updateSelection(null);
      showValidation(data.validation);
    } catch (err) {
      log(err.message);
    }
  });

  canvas.addEventListener("click", async (event) => {
    if (!currentWorld) return;
    if (robotStartMode) {
      const point = window.EV3Canvas.canvasToWorld(canvas, event.clientX, event.clientY, currentWorld);
      const theta = Number(robotThetaInput.value || 0);
      try {
        await api.setRobotStart({
          x_mm: point.xMm,
          y_mm: point.yMm,
          theta_deg: theta,
        });
        robotStart = { x_mm: point.xMm, y_mm: point.yMm, theta_deg: theta };
        updateRobotStartReadout();
        setRobotStartMode(false);
        log("Pose inicial actualizada.");
      } catch (err) {
        log(err.message);
      }
      return;
    }
    const clicked = window.EV3Canvas.findPlacementAt(canvas, event.clientX, event.clientY, currentWorld);
    if (moveMode && selectedPlacement) {
      const point = window.EV3Canvas.canvasToEditor(canvas, event.clientX, event.clientY, currentWorld);
      const origin = window.EV3Canvas.placementOriginForAsset(
        selectedPlacement.asset_key,
        point,
        currentWorld,
        selectedPlacement.rotation || 0,
      );
      try {
        const data = await api.moveAsset({ id: selectedPlacement.id, x: origin.x, y: origin.y });
        setEditorWorld(data.world);
        const updated = data.world.placements.find((p) => p.id === selectedPlacement.id);
        updateSelection(updated || null);
        showValidation(data.validation);
      } catch (err) {
        log(err.message);
      }
      return;
    }
    if (clicked) {
      updateSelection(clicked);
      return;
    }
    if (!assetSelect.value) {
      updateSelection(null);
      return;
    }
    const point = window.EV3Canvas.canvasToEditor(canvas, event.clientX, event.clientY, currentWorld);
    const origin = window.EV3Canvas.placementOriginForAsset(assetSelect.value, point, currentWorld, 0);
    try {
      const data = await api.placeAsset({
        asset_key: assetSelect.value,
        x: origin.x,
        y: origin.y,
        rotation: 0,
      });
      setEditorWorld(data.world);
      updateSelection(data.placement);
      showValidation(data.validation);
    } catch (err) {
      log(err.message);
    }
  });

  placeRobotStartBtn.addEventListener("click", () => {
    setRobotStartMode(!robotStartMode);
  });

  document.getElementById("clearRobotStartBtn").addEventListener("click", () => {
    robotStart = null;
    setRobotStartMode(false);
    updateRobotStartReadout();
  });

  robotThetaInput.addEventListener("change", async () => {
    if (!robotStart) return;
    robotStart.theta_deg = Number(robotThetaInput.value || 0);
    try {
      await api.setRobotStart(robotStart);
      updateRobotStartReadout();
    } catch (err) {
      log(err.message);
    }
  });

  moveAssetBtn.addEventListener("click", () => {
    if (!selectedPlacement) return;
    moveMode = !moveMode;
    moveAssetBtn.classList.toggle("tool-active", moveMode);
    selectedAssetEl.textContent = moveMode
      ? `Mover ${selectedPlacement.id}: haz clic en destino`
      : `${selectedPlacement.id} (${selectedPlacement.asset_key})`;
  });

  document.getElementById("rotateAssetBtn").addEventListener("click", async () => {
    if (!selectedPlacement) return;
    try {
      const data = await api.rotateAsset({ id: selectedPlacement.id, delta_deg: 90 });
      setEditorWorld(data.world);
      const updated = data.world.placements.find((p) => p.id === selectedPlacement.id);
      updateSelection(updated || null);
      showValidation(data.validation);
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("duplicateAssetBtn").addEventListener("click", async () => {
    if (!selectedPlacement) return;
    try {
      const data = await api.duplicateAsset({ id: selectedPlacement.id });
      setEditorWorld(data.world);
      updateSelection(data.placement);
      showValidation(data.validation);
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("deleteAssetBtn").addEventListener("click", async () => {
    if (!selectedPlacement) return;
    try {
      const data = await api.removeAsset(selectedPlacement.id);
      setEditorWorld(data.world);
      updateSelection(null);
      showValidation(data.validation);
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("validateWorldBtn").addEventListener("click", async () => {
    try {
      showValidation(await api.validateEditorWorld());
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("exportWorldBtn").addEventListener("click", () => {
    if (!editorWorld) return;
    const blob = new Blob([JSON.stringify(editorWorld, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "mundo_ev3_web.json";
    link.click();
    URL.revokeObjectURL(url);
  });

  document.getElementById("saveWorldBtn").addEventListener("click", async () => {
    const name = document.getElementById("saveWorldName").value.trim();
    try {
      const result = await api.saveEditorWorld(name);
      log(`Mundo guardado: ${result.name}`);
      await loadWorlds();
      worldSelect.value = result.name;
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("importWorldInput").addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const text = await file.text();
      const world = JSON.parse(text);
      const data = await api.importEditorWorld(world);
      setEditorWorld(data.world);
      updateSelection(null);
      showValidation(data.validation);
    } catch (err) {
      log(err.message);
    } finally {
      event.target.value = "";
    }
  });

  document.getElementById("applyWorldBtn").addEventListener("click", async () => {
    try {
      const data = await api.applyEditorWorld();
      currentWorld = data.world;
      editorWorld = data.world?.editor_spec || editorWorld;
      log("Mundo aplicado a la simulacion.");
    } catch (err) {
      log(err.message);
    }
  });

  window.addEventListener("beforeunload", () => {
    stopLiveUpdates();
  });

  try {
    await init();
  } catch (err) {
    log(err.message);
  }
})();
