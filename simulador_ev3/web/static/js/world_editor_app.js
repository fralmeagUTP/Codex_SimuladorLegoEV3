(async () => {
  const api = window.EV3Api;
  const canvas = document.getElementById("worldCanvas");
  const statusEl = document.getElementById("sessionStatus");
  const consoleEl = document.getElementById("console");
  const assetSelect = document.getElementById("assetSelect");
  const assetKeyInput = document.getElementById("assetKeyInput");
  const assetXInput = document.getElementById("assetXInput");
  const assetYInput = document.getElementById("assetYInput");
  const assetRotationInput = document.getElementById("assetRotationInput");
  const assetPropertiesForm = document.getElementById("assetPropertiesForm");
  const selectedAssetEl = document.getElementById("selectedAsset");
  const assetPropertiesEl = document.getElementById("assetProperties");
  const assetPalette = document.getElementById("assetPalette");
  const moveAssetBtn = document.getElementById("moveAssetBtn");
  const placeRobotStartBtn = document.getElementById("placeRobotStartBtn");
  const robotThetaInput = document.getElementById("robotThetaInput");
  const robotStartReadout = document.getElementById("robotStartReadout");
  const worldNameLabel = document.getElementById("worldNameLabel");
  const simulateSavedWorldLink = document.getElementById("simulateSavedWorldLink");
  const worldWidthInput = document.getElementById("worldWidthInput");
  const worldHeightInput = document.getElementById("worldHeightInput");
  const cursorReadout = document.getElementById("cursorReadout");
  const validationStatus = document.getElementById("validationStatus");
  const worldMapZoomInBtn = document.getElementById("worldMapZoomInBtn");
  const worldMapZoomOutBtn = document.getElementById("worldMapZoomOutBtn");
  const worldMapZoomResetBtn = document.getElementById("worldMapZoomResetBtn");
  const DEFAULT_WORLD_CELLS = 40;
  let currentWorld = null;
  let editorWorld = null;
  let selectedPlacement = null;
  let moveMode = false;
  let robotStartMode = false;
  let robotStart = null;
  let placementPreview = null;
  let dragPlacement = null;
  let suppressNextClick = false;

  function log(message) {
    consoleEl.textContent = message || "";
  }

  function setStatus(status) {
    statusEl.textContent = status;
  }

  async function init() {
    const session = await api.createSession();
    setStatus(session.status);
    await loadAssets();
    await createEditorWorld();
    drawEditor();
  }

  async function loadAssets() {
    const data = await api.getEditorAssets();
    assetSelect.innerHTML = "<option value=''>Seleccionar asset</option>";
    assetPalette.innerHTML = "";
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
      assetKeyInput.appendChild(option.cloneNode(true));

      const button = document.createElement("button");
      button.type = "button";
      button.className = "asset-tool";
      button.title = item.key;
      button.dataset.assetKey = item.key;
      const img = document.createElement("img");
      img.src = api.resolvePath(`/assets/${encodeURIComponent(assetImageFile(item.key))}`);
      img.alt = "";
      img.onerror = () => {
        img.remove();
        button.textContent = assetShortLabel(item);
      };
      button.appendChild(img);
      button.addEventListener("click", () => {
        assetSelect.value = item.key;
        syncAssetPalette();
        updateSelection(null);
      });
      assetPalette.appendChild(button);
    }
    syncAssetPalette();
  }

  function assetImageFile(key) {
    return {
      floor_tile_256_c: "floor_tile_256_c.jpg",
    }[key] || `${key}.png`;
  }

  function assetShortLabel(item) {
    if (item.type === "line") return "L";
    if (item.type === "wall") return "W";
    if (item.type === "zone") return item.key.includes("red") ? "R" : item.key.includes("green") ? "G" : "Z";
    if (item.type === "robot") return "EV3";
    return "F";
  }

  function syncAssetPalette() {
    for (const button of assetPalette.querySelectorAll(".asset-tool")) {
      button.classList.toggle("tool-active", button.dataset.assetKey === assetSelect.value);
    }
  }

  async function createEditorWorld() {
    const width = Number.parseInt(worldWidthInput?.value || String(DEFAULT_WORLD_CELLS), 10);
    const height = Number.parseInt(worldHeightInput?.value || String(DEFAULT_WORLD_CELLS), 10);
    const data = await api.createEditorWorld(width || DEFAULT_WORLD_CELLS, height || DEFAULT_WORLD_CELLS);
    setEditorWorld(data.world);
    showValidation(data.validation);
  }

  function setEditorWorld(world) {
    editorWorld = world;
    if (worldWidthInput) worldWidthInput.value = world.world_width_cells || DEFAULT_WORLD_CELLS;
    if (worldHeightInput) worldHeightInput.value = world.world_height_cells || DEFAULT_WORLD_CELLS;
    currentWorld = editorWorldToRenderWorld(world);
    drawEditor();
  }

  function editorWorldToRenderWorld(world) {
    if (!world) return currentWorld;
    return {
      width_mm: (world.world_width_cells || DEFAULT_WORLD_CELLS) * 100,
      height_mm: (world.world_height_cells || DEFAULT_WORLD_CELLS) * 100,
      surface: { cell_size_mm: 100, default_color: "WHITE", cells: [] },
      obstacles: [],
      beacons: [],
      editor_spec: world,
    };
  }

  function drawEditor() {
    window.EV3Canvas.draw(canvas, null, currentWorld, {
      selectedPlacementId: selectedPlacement?.id || null,
      placementPreview,
      robotStart,
    });
  }

  function applyMapZoom(action) {
    if (!window.EV3Canvas || !canvas) return;
    if (action === "in") {
      window.EV3Canvas.zoomIn(canvas);
    } else if (action === "out") {
      window.EV3Canvas.zoomOut(canvas);
    } else {
      window.EV3Canvas.fitToView(canvas, currentWorld);
    }
    drawEditor();
  }

  window.addEventListener("ev3-assets-loaded", drawEditor);

  function updateSelection(placement) {
    selectedPlacement = placement;
    moveMode = false;
    moveAssetBtn.classList.remove("tool-active");
    selectedAssetEl.textContent = placement
      ? `${placement.id} (${placement.asset_key})`
      : "Sin seleccion";
    if (!placement) {
      assetPropertiesEl.innerHTML = "";
      assetPropertiesForm.classList.add("hidden");
      drawEditor();
      return;
    }
    assetPropertiesEl.innerHTML = `
      <dt>ID</dt><dd>${placement.id}</dd>
      <dt>Asset</dt><dd>${placement.asset_key}</dd>
      <dt>X</dt><dd>${placement.x ?? placement.x_px ?? 0}</dd>
      <dt>Y</dt><dd>${placement.y ?? placement.y_px ?? 0}</dd>
      <dt>Rotacion</dt><dd>${placement.rotation || 0}</dd>
    `;
    assetKeyInput.value = placement.asset_key;
    assetXInput.value = placement.x ?? placement.x_px ?? 0;
    assetYInput.value = placement.y ?? placement.y_px ?? 0;
    assetRotationInput.value = placement.rotation || 0;
    assetPropertiesForm.classList.remove("hidden");
    drawEditor();
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

    const xCm = robotStart.x_mm / 10;
    const yCm = robotStart.y_mm / 10;
    robotStartReadout.textContent =
      `X ${xCm.toFixed(1)} cm, Y ${yCm.toFixed(1)} cm, ` +
      `${robotStart.theta_deg.toFixed(0)} °`;
  }

  function showValidation(validation) {
    if (!validation) return;
    const errors = validation.errors || [];
    const warnings = validation.warnings || [];
    if (!errors.length && !warnings.length) {
      validationStatus.textContent = "Validacion: OK";
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
    validationStatus.textContent = errors.length
      ? `Validacion: ${errors.length} error(es)`
      : `Validacion: ${warnings.length} advertencia(s)`;
    log(lines.join("\n"));
  }

  function setWorldNameLabel(name) {
    if (!worldNameLabel) return;
    const text = String(name || "").trim();
    worldNameLabel.textContent = text || "sin nombre";
  }

  function currentWorldName() {
    if (!worldNameLabel) return "";
    const value = (worldNameLabel.textContent || "").trim();
    return value === "sin nombre" ? "" : value;
  }

  function stripJsonExtension(name) {
    return String(name || "").replace(/\.json$/i, "");
  }

  function setSimulateSavedWorldLink(savedName) {
    if (!simulateSavedWorldLink) return;
    if (!savedName) {
      simulateSavedWorldLink.classList.add("hidden");
      simulateSavedWorldLink.href = api.resolvePath("/");
      return;
    }
    const name = String(savedName || "").trim();
    if (!name) {
      simulateSavedWorldLink.classList.add("hidden");
      simulateSavedWorldLink.href = api.resolvePath("/");
      return;
    }
    const encoded = encodeURIComponent(name);
    simulateSavedWorldLink.href = api.resolvePath(`/?world=${encoded}`);
    simulateSavedWorldLink.classList.remove("hidden");
  }

  async function saveWorldOnServer() {
    const currentName = currentWorldName();
    const suggested = currentName || "mundo_ev3_web";
    const rawName = window.prompt("Nombre del mundo para guardar en servidor", suggested);
    if (rawName === null) {
      log("Guardado cancelado.");
      return;
    }
    const trimmed = String(rawName || "").trim();
    if (!trimmed) {
      log("Debes indicar un nombre de mundo.");
      return;
    }
    const result = await api.saveEditorWorld(trimmed);
    const savedFileName = String(result.name || "").trim();
    const displayName = stripJsonExtension(savedFileName || trimmed);
    setWorldNameLabel(displayName);
    setSimulateSavedWorldLink(savedFileName);
    log(`Mundo guardado en servidor: ${savedFileName}`);
  }

  async function downloadWorldAsFile() {
    if (!editorWorld) return;
    const baseName = currentWorldName() || "mundo_ev3_web";
    const suggestedName = baseName.toLowerCase().endsWith(".json") ? baseName : `${baseName}.json`;
    const worldJson = JSON.stringify(editorWorld, null, 2);

    if (typeof window.showSaveFilePicker === "function") {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName,
          types: [
            {
              description: "JSON",
              accept: {
                "application/json": [".json"],
                "text/json": [".json"],
              },
            },
          ],
        });
        const writable = await handle.createWritable();
        await writable.write(worldJson);
        await writable.close();
        log(`Mundo exportado: ${handle.name || suggestedName}. Ubicacion: seleccionada en el dialogo del sistema.`);
        return;
      } catch (err) {
        if (err?.name === "AbortError") {
          log("Guardado cancelado.");
          return;
        }
      }
    }

    const blob = new Blob([worldJson], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = suggestedName;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    log(`Mundo descargado: ${suggestedName}. Ubicacion: Descargas del navegador.`);
  }

  document.getElementById("newWorldBtn").addEventListener("click", async () => {
    try {
      const width = Number.parseInt(worldWidthInput.value || String(DEFAULT_WORLD_CELLS), 10);
      const height = Number.parseInt(worldHeightInput.value || String(DEFAULT_WORLD_CELLS), 10);
      const data = await api.createEditorWorld(width || DEFAULT_WORLD_CELLS, height || DEFAULT_WORLD_CELLS);
      setEditorWorld(data.world);
      setWorldNameLabel("");
      setSimulateSavedWorldLink("");
      updateSelection(null);
      showValidation(data.validation);
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("applyWorldSizeBtn").addEventListener("click", async () => {
    try {
      const data = await api.createEditorWorld(
        Number.parseInt(worldWidthInput.value || String(DEFAULT_WORLD_CELLS), 10),
        Number.parseInt(worldHeightInput.value || String(DEFAULT_WORLD_CELLS), 10),
      );
      setEditorWorld(data.world);
      setWorldNameLabel("");
      setSimulateSavedWorldLink("");
      updateSelection(null);
      showValidation(data.validation);
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("openWorldBtn").addEventListener("click", () => {
    document.getElementById("importWorldInput").click();
  });

  assetSelect.addEventListener("change", () => {
    syncAssetPalette();
    placementPreview = null;
    updateSelection(null);
  });

  canvas.addEventListener("mousemove", (event) => {
    if (!currentWorld) return;
    const point = window.EV3Canvas.canvasToWorld(canvas, event.clientX, event.clientY, currentWorld);
    const editorPoint = window.EV3Canvas.canvasToEditor(canvas, event.clientX, event.clientY, currentWorld);
    const xCm = point.xMm / 10;
    const yCm = point.yMm / 10;
    cursorReadout.textContent =
      `Cursor: (${xCm.toFixed(1)} cm, ${yCm.toFixed(1)} cm) | Snap: ` +
      `(${editorPoint.x}px, ${editorPoint.y}px) | Tool: ${assetSelect.value || "Select"}`;
    const canPreviewPlacement =
      assetSelect.value && !robotStartMode && !moveMode && !dragPlacement;
    if (canPreviewPlacement) {
      const origin = window.EV3Canvas.placementOriginForAsset(assetSelect.value, editorPoint, currentWorld, 0);
      placementPreview = {
        asset_key: assetSelect.value,
        x: origin.x,
        y: origin.y,
        rotation: 0,
      };
      drawEditor();
    } else if (placementPreview) {
      placementPreview = null;
      drawEditor();
    }
    if (dragPlacement) {
      const dx = Math.abs(event.clientX - dragPlacement.startClientX);
      const dy = Math.abs(event.clientY - dragPlacement.startClientY);
      if (dx > 3 || dy > 3) {
        dragPlacement.moved = true;
        dragPlacement.target = window.EV3Canvas.placementMoveTarget(
          dragPlacement.placement,
          editorPoint,
          currentWorld,
          dragPlacement.offset,
        );
        selectedAssetEl.textContent =
          `Arrastrar ${dragPlacement.id}: (${dragPlacement.target.x}px, ${dragPlacement.target.y}px)`;
      }
    }
  });

  canvas.addEventListener("mouseleave", () => {
    if (!placementPreview) return;
    placementPreview = null;
    drawEditor();
  });

  canvas.addEventListener("mousedown", (event) => {
    if (!currentWorld || robotStartMode) return;
    const clicked = window.EV3Canvas.findPlacementAt(canvas, event.clientX, event.clientY, currentWorld);
    if (!clicked) return;
    const editorPoint = window.EV3Canvas.canvasToEditor(canvas, event.clientX, event.clientY, currentWorld);
    const x0 = clicked.x ?? clicked.x_px ?? 0;
    const y0 = clicked.y ?? clicked.y_px ?? 0;
    updateSelection(clicked);
    dragPlacement = {
      id: clicked.id,
      placement: clicked,
      startClientX: event.clientX,
      startClientY: event.clientY,
      offset: { x: x0 - editorPoint.x, y: y0 - editorPoint.y },
      moved: false,
      target: null,
    };
  });

  canvas.addEventListener("mouseup", async () => {
    if (!dragPlacement) return;
    const drag = dragPlacement;
    dragPlacement = null;
    if (!drag.moved || !drag.target) return;
    suppressNextClick = true;
    try {
      const data = await api.moveAsset({ id: drag.id, x: drag.target.x, y: drag.target.y });
      setEditorWorld(data.world);
      const updated = data.world.placements.find((p) => p.id === drag.id);
      updateSelection(updated || null);
      showValidation(data.validation);
    } catch (err) {
      log(err.message);
    }
  });

  canvas.addEventListener("click", async (event) => {
    if (!currentWorld) return;
    if (suppressNextClick) {
      suppressNextClick = false;
      return;
    }
    if (robotStartMode) {
      placementPreview = null;
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
        drawEditor();
        log("Pose inicial actualizada.");
      } catch (err) {
        log(err.message);
      }
      return;
    }
    const clicked = window.EV3Canvas.findPlacementAt(canvas, event.clientX, event.clientY, currentWorld);
    if (moveMode && selectedPlacement) {
      placementPreview = null;
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
      placementPreview = null;
      updateSelection(clicked);
      return;
    }
    if (!assetSelect.value) {
      placementPreview = null;
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
      placementPreview = null;
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
    drawEditor();
  });

  robotThetaInput.addEventListener("change", async () => {
    if (!robotStart) return;
    robotStart.theta_deg = Number(robotThetaInput.value || 0);
    try {
      await api.setRobotStart(robotStart);
      updateRobotStartReadout();
      drawEditor();
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

  assetPropertiesForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!selectedPlacement) return;
    try {
      const data = await api.updateAsset({
        id: selectedPlacement.id,
        asset_key: assetKeyInput.value,
        x: Number.parseInt(assetXInput.value || "0", 10),
        y: Number.parseInt(assetYInput.value || "0", 10),
        rotation: Number.parseInt(assetRotationInput.value || "0", 10),
      });
      setEditorWorld(data.world);
      updateSelection(data.placement);
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

  document.getElementById("exportWorldBtn").addEventListener("click", async () => {
    try {
      await downloadWorldAsFile();
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
      const importPayload = (world && typeof world === "object" && world.editor_spec && typeof world.editor_spec === "object")
        ? world.editor_spec
        : world;
      const data = await api.importEditorWorld(importPayload);
      setEditorWorld(data.world);
      const inferredName = stripJsonExtension(world?.name || world?.world_name || file.name);
      setWorldNameLabel(inferredName);
      setSimulateSavedWorldLink("");
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
      await api.applyEditorWorld();
      log("Mundo validado y listo para simulacion.");
    } catch (err) {
      log(err.message);
    }
  });

  document.getElementById("saveWorldBtn").addEventListener("click", async () => {
    try {
      await saveWorldOnServer();
    } catch (err) {
      log(err.message);
    }
  });

  worldMapZoomInBtn?.addEventListener("click", () => {
    applyMapZoom("in");
  });

  worldMapZoomOutBtn?.addEventListener("click", () => {
    applyMapZoom("out");
  });

  worldMapZoomResetBtn?.addEventListener("click", () => {
    applyMapZoom("reset");
  });

  try {
    await init();
  } catch (err) {
    log(err.message);
  }
})();
