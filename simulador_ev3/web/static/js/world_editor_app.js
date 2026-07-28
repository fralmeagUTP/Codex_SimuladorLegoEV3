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
  const assetSearchInput = document.getElementById("assetSearchInput");
  const assetLibraryHint = document.getElementById("assetLibraryHint");
  const moveAssetBtn = document.getElementById("moveAssetBtn");
  const placeRobotStartBtn = document.getElementById("placeRobotStartBtn");
  const robotThetaInput = document.getElementById("robotThetaInput");
  const robotStartReadout = document.getElementById("robotStartReadout");
  const worldNameLabel = document.getElementById("worldNameLabel");
  const simulateSavedWorldLink = document.getElementById("simulateSavedWorldLink");
  const deleteSavedWorldBtn = document.getElementById("deleteSavedWorldBtn");
  const worldWidthInput = document.getElementById("worldWidthInput");
  const worldHeightInput = document.getElementById("worldHeightInput");
  const worldSizeHint = document.getElementById("worldSizeHint");
  const emptyWorldGuide = document.getElementById("emptyWorldGuide");
  const cursorReadout = document.getElementById("cursorReadout");
  const validationStatus = document.getElementById("validationStatus");
  const layerList = document.getElementById("layerList");
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
  let activeWorldBaseName = "";
  let savedWorldFileName = "";
  let placementPreview = null;
  let dragPlacement = null;
  let suppressNextClick = false;
  const hiddenLayerIds = new Set();
  const lockedLayerIds = new Set();

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
      wall: "Obstáculos",
      line: "Líneas",
      zone: "Zonas y metas",
      floor: "Suelos",
    };
    const categoryContainers = {};
    for (const item of data.assets) {
      const option = document.createElement("option");
      option.value = item.key;
      option.textContent = `${groups[item.type] || item.type}: ${assetLabel(item)}`;
      assetSelect.appendChild(option);
      assetKeyInput.appendChild(option.cloneNode(true));

      const button = document.createElement("button");
      button.type = "button";
      button.className = "asset-tool";
      button.title = assetTooltip(item);
      button.dataset.assetKey = item.key;
      button.dataset.assetLabel = `${assetLabel(item)} ${groups[item.type] || ""}`.toLocaleLowerCase();
      const img = document.createElement("img");
      img.src = api.resolvePath(`/assets/${encodeURIComponent(assetImageFile(item.key))}`);
      img.alt = "";
      img.onerror = () => {
        img.remove();
        button.textContent = assetShortLabel(item);
      };
      button.appendChild(img);
      const label = document.createElement("span");
      label.textContent = assetLabel(item);
      button.appendChild(label);
      button.addEventListener("click", () => {
        assetSelect.value = item.key;
        syncAssetPalette();
        updateSelection(null);
        assetLibraryHint.textContent = `${assetLabel(item)} seleccionado. Haz clic en el mapa para colocarlo.`;
      });
      const category = groups[item.type] || "Otros";
      if (!categoryContainers[category]) {
        const section = document.createElement("section");
        section.className = "asset-category";
        section.innerHTML = `<h3>${category}</h3>`;
        const items = document.createElement("div");
        items.className = "asset-category-items";
        section.appendChild(items);
        assetPalette.appendChild(section);
        categoryContainers[category] = items;
      }
      categoryContainers[category].appendChild(button);
    }
    syncAssetPalette();
    assetSearchInput?.addEventListener("input", filterAssetPalette);
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

  function assetLabel(item) {
    const key = String(item?.key || "");
    if (key.includes("robot")) return "Robot EV3";
    if (key.includes("wall")) return `Muro ${key.slice(-1).toUpperCase()}`;
    if (key.includes("floor")) return `Suelo ${key.slice(-1).toUpperCase()}`;
    if (key.includes("zone_green")) return "Zona verde";
    if (key.includes("zone_red")) return "Zona roja";
    if (key.includes("zone_white")) return "Zona blanca";
    if (key.includes("cruz")) return "Cruce";
    if (key.includes("hor")) return "Línea horizontal";
    if (key.includes("ver")) return "Línea vertical";
    if (key.includes("infder")) return "Curva inferior derecha";
    if (key.includes("infizq")) return "Curva inferior izquierda";
    if (key.includes("supder")) return "Curva superior derecha";
    if (key.includes("supizq")) return "Curva superior izquierda";
    return key;
  }

  function filterAssetPalette() {
    const query = String(assetSearchInput?.value || "").trim().toLocaleLowerCase();
    for (const section of assetPalette.querySelectorAll(".asset-category")) {
      let visible = 0;
      for (const button of section.querySelectorAll(".asset-tool")) {
        const matches = !query || String(button.dataset.assetLabel || "").includes(query);
        button.hidden = !matches;
        if (matches) visible += 1;
      }
      section.hidden = visible === 0;
    }
  }

  function assetTooltip(item) {
    const key = String(item?.key || "");
    const type = String(item?.type || "");
    if (type === "robot") return "Robot EV3 (pose inicial)";
    if (type === "wall") return `Muro: ${key}`;
    if (type === "line") return `Linea de seguimiento: ${key}`;
    if (type === "zone") {
      if (key.includes("green")) return "Zona color verde";
      if (key.includes("red")) return "Zona color roja";
      return "Zona color blanca";
    }
    if (type === "floor") return `Piso/base: ${key}`;
    return key;
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
    await hydrateRobotStartFromSnapshotIfMissing();
    await ensureRobotVisibleOnEditor();
    showValidation(data.validation);
  }

  function setEditorWorld(world) {
    editorWorld = world;
    if (worldWidthInput) worldWidthInput.value = world.world_width_cells || DEFAULT_WORLD_CELLS;
    if (worldHeightInput) worldHeightInput.value = world.world_height_cells || DEFAULT_WORLD_CELLS;
    updateWorldSizeHint();
    currentWorld = editorWorldToRenderWorld(world);
    robotStart = robotStartFromEditorWorld(world);
    if (!robotStart) {
      // Fallback visible inmediato al abrir mundos sin placement de robot.
      robotStart = defaultRobotPoseForWorld(world);
    }
    if (robotStart && robotThetaInput) {
      robotThetaInput.value = String(Math.round(robotStart.theta_deg || 0));
    }
    updateRobotStartReadout();
    prunePresentationLayers();
    renderLayers();
    drawEditor();
  }

  async function hydrateRobotStartFromSnapshotIfMissing() {
    if (robotStart) return;
    try {
      const data = await api.snapshot();
      const robot = data?.snapshot?.robot;
      if (!robot) return;
      const xMm = Number(robot.x_mm);
      const yMm = Number(robot.y_mm);
      const theta = Number(robot.theta_deg);
      if (!Number.isFinite(xMm) || !Number.isFinite(yMm) || !Number.isFinite(theta)) return;
      robotStart = {
        x_mm: xMm,
        y_mm: yMm,
        theta_deg: ((theta % 360) + 360) % 360,
      };
      if (robotThetaInput) {
        robotThetaInput.value = String(Math.round(robotStart.theta_deg));
      }
      await upsertRobotPlacementFromPose(robotStart);
      updateRobotStartReadout();
      drawEditor();
    } catch (_err) {
      // Fallback visual; no interrumpe flujo del editor.
    }
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
    const visibleWorld = hiddenLayerIds.size
      ? { ...currentWorld, editor_spec: { ...editorWorld, placements: (editorWorld?.placements || []).filter((p) => !hiddenLayerIds.has(p.id)) } }
      : currentWorld;
    window.EV3Canvas.draw(canvas, null, visibleWorld, {
      selectedPlacementId: selectedPlacement?.id || null,
      placementPreview,
      robotStart,
      followRobotStart: false,
    });
    emptyWorldGuide?.classList.toggle("hidden", Boolean(editorWorld?.placements?.length));
  }

  function updateWorldSizeHint() {
    if (!worldSizeHint) return;
    const width = Number(worldWidthInput?.value || 0);
    const height = Number(worldHeightInput?.value || 0);
    worldSizeHint.textContent = Number.isFinite(width) && Number.isFinite(height)
      ? `Equivale a ${width * 10} × ${height * 10} cm`
      : "";
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
    const isLocked = Boolean(placement?.id && lockedLayerIds.has(placement.id));
    for (const id of ["deleteAssetBtn", "rotateAssetBtn", "duplicateAssetBtn", "applyAssetPropertiesBtn"]) {
      const button = document.getElementById(id);
      if (button) button.disabled = !placement || isLocked;
    }
    selectedAssetEl.textContent = placement
      ? assetLabel({ key: placement.asset_key })
      : "Selecciona un elemento del lienzo para editarlo.";
    if (!placement) {
      assetPropertiesEl.innerHTML = "";
      assetPropertiesForm.classList.add("hidden");
      drawEditor();
      renderLayers();
      return;
    }
    assetPropertiesEl.innerHTML = `
      <dt>Tipo</dt><dd>${assetLabel({ key: placement.asset_key })}</dd>
      <dt>X</dt><dd>${(placement.x ?? placement.x_px ?? 0) / Number(editorWorld?.grid_size_px || 32)} celdas</dd>
      <dt>Y</dt><dd>${(placement.y ?? placement.y_px ?? 0) / Number(editorWorld?.grid_size_px || 32)} celdas</dd>
      <dt>Rotación</dt><dd>${placement.rotation || 0}°</dd>
    `;
    assetKeyInput.value = placement.asset_key;
    assetXInput.value = (placement.x ?? placement.x_px ?? 0) / Number(editorWorld?.grid_size_px || 32);
    assetYInput.value = (placement.y ?? placement.y_px ?? 0) / Number(editorWorld?.grid_size_px || 32);
    assetRotationInput.value = placement.rotation || 0;
    assetPropertiesForm.classList.remove("hidden");
    drawEditor();
    renderLayers();
  }

  function prunePresentationLayers() {
    const valid = new Set((editorWorld?.placements || []).map((placement) => placement.id));
    for (const id of hiddenLayerIds) if (!valid.has(id)) hiddenLayerIds.delete(id);
    for (const id of lockedLayerIds) if (!valid.has(id)) lockedLayerIds.delete(id);
  }

  function renderLayers() {
    if (!layerList) return;
    layerList.innerHTML = "";
    const placements = [...(editorWorld?.placements || [])].reverse();
    if (!placements.length) {
      layerList.textContent = "No hay elementos en este mundo.";
      return;
    }
    for (const placement of placements) {
      const row = document.createElement("div");
      row.className = "layer-row";
      if (placement.id === selectedPlacement?.id) row.classList.add("selected");
      const select = document.createElement("button");
      select.type = "button";
      select.textContent = assetLabel({ key: placement.asset_key });
      select.addEventListener("click", () => updateSelection(placement));
      const visibility = document.createElement("button");
      visibility.type = "button";
      visibility.textContent = hiddenLayerIds.has(placement.id) ? "Mostrar" : "Ocultar";
      visibility.addEventListener("click", () => {
        if (hiddenLayerIds.has(placement.id)) hiddenLayerIds.delete(placement.id);
        else hiddenLayerIds.add(placement.id);
        drawEditor(); renderLayers();
      });
      const lock = document.createElement("button");
      lock.type = "button";
      lock.textContent = lockedLayerIds.has(placement.id) ? "Desbloq." : "Bloquear";
      lock.addEventListener("click", () => {
        if (lockedLayerIds.has(placement.id)) lockedLayerIds.delete(placement.id);
        else lockedLayerIds.add(placement.id);
        updateSelection(selectedPlacement);
      });
      row.append(select, visibility, lock);
      layerList.appendChild(row);
    }
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

  function robotPlacementFromEditorWorld(world) {
    const placements = Array.isArray(world?.placements) ? world.placements : [];
    return placements.find((item) => String(item?.asset_key || "").includes("robot")) || null;
  }

  function defaultRobotPoseForWorld(world) {
    const widthCells = Number(world?.world_width_cells || DEFAULT_WORLD_CELLS);
    const heightCells = Number(world?.world_height_cells || DEFAULT_WORLD_CELLS);
    const theta = Number(robotThetaInput?.value || 0);
    return {
      x_mm: Math.max(0, widthCells * 50),
      y_mm: Math.max(0, heightCells * 50),
      theta_deg: ((theta % 360) + 360) % 360,
    };
  }

  function robotStartFromEditorWorld(world) {
    const placement = robotPlacementFromEditorWorld(world);
    if (!placement) return null;
    const gridSizePx = Number(world?.grid_size_px || 32);
    const mmPerPx = 100 / Math.max(1, gridSizePx);
    const xPx = Number(placement.x ?? placement.x_px ?? 0);
    const yPx = Number(placement.y ?? placement.y_px ?? 0);
    const theta = Number(placement.rotation || 0);
    return {
      x_mm: xPx * mmPerPx + 50,
      y_mm: yPx * mmPerPx + 50,
      theta_deg: ((theta % 360) + 360) % 360,
    };
  }

  function robotPlacementOriginFromPose(pose) {
    if (!currentWorld || !pose || !editorWorld) return null;
    const gridSize = Number(editorWorld.grid_size_px || 32);
    const mmPerPx = 100 / Math.max(1, gridSize);
    const worldWidthPx = Math.round((currentWorld.width_mm / 100) * gridSize);
    const worldHeightPx = Math.round((currentWorld.height_mm / 100) * gridSize);
    const cellPx = gridSize;
    const centerXPx = Number(pose.x_mm) / mmPerPx;
    const centerYPx = Number(pose.y_mm) / mmPerPx;
    const x = Math.round(centerXPx - (cellPx / 2));
    const y = Math.round(centerYPx - (cellPx / 2));
    const candidate = {
      x: Math.max(0, Math.min(x, Math.max(0, worldWidthPx - cellPx))),
      y: Math.max(0, Math.min(y, Math.max(0, worldHeightPx - cellPx))),
    };
    return snapRobotOriginToNearestFreeCell(candidate, gridSize, worldWidthPx, worldHeightPx);
  }

  function assetSpanCells(assetKey, rotation = 0) {
    let size = { w: 2, h: 2 };
    if (String(assetKey || "").includes("robot")) size = { w: 1, h: 1 };
    else if (String(assetKey || "").includes("zone")) size = { w: 4, h: 4 };
    else if (String(assetKey || "").includes("floor")) size = { w: 8, h: 8 };
    if (Math.abs(Number(rotation) || 0) % 180 === 90) {
      return { w: size.h, h: size.w };
    }
    return size;
  }

  function rectsOverlap(a, b) {
    return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  }

  function robotOriginCollidesWithWall(origin, gridSizePx) {
    const placements = Array.isArray(editorWorld?.placements) ? editorWorld.placements : [];
    const robotRect = { x: origin.x, y: origin.y, w: gridSizePx, h: gridSizePx };
    for (const p of placements) {
      const key = String(p?.asset_key || "");
      if (!key.includes("wall")) continue;
      const span = assetSpanCells(key, Number(p?.rotation || 0));
      const xPx = Number(p?.x ?? p?.x_px ?? 0);
      const yPx = Number(p?.y ?? p?.y_px ?? 0);
      const wallRect = {
        x: xPx,
        y: yPx,
        w: span.w * gridSizePx,
        h: span.h * gridSizePx,
      };
      if (rectsOverlap(robotRect, wallRect)) return true;
    }
    return false;
  }

  function snapRobotOriginToNearestFreeCell(origin, gridSizePx, worldWidthPx, worldHeightPx) {
    const clampOrigin = (x, y) => ({
      x: Math.max(0, Math.min(x, Math.max(0, worldWidthPx - gridSizePx))),
      y: Math.max(0, Math.min(y, Math.max(0, worldHeightPx - gridSizePx))),
    });
    const base = clampOrigin(origin.x, origin.y);
    if (!robotOriginCollidesWithWall(base, gridSizePx)) return base;

    const maxRadius = Math.max(
      1,
      Math.ceil(Math.max(worldWidthPx, worldHeightPx) / Math.max(1, gridSizePx)),
    );
    for (let r = 1; r <= maxRadius; r += 1) {
      for (let dx = -r; dx <= r; dx += 1) {
        for (let dy = -r; dy <= r; dy += 1) {
          if (Math.abs(dx) !== r && Math.abs(dy) !== r) continue;
          const candidate = clampOrigin(
            base.x + dx * gridSizePx,
            base.y + dy * gridSizePx,
          );
          if (!robotOriginCollidesWithWall(candidate, gridSizePx)) {
            return candidate;
          }
        }
      }
    }
    return base;
  }

  async function upsertRobotPlacementFromPose(pose) {
    if (!editorWorld || !currentWorld || !pose) return;
    const origin = robotPlacementOriginFromPose(pose);
    if (!origin) return;
    const rotation = ((Number(pose.theta_deg || 0) % 360) + 360) % 360;
    const existing = robotPlacementFromEditorWorld(editorWorld);
    const payload = {
      asset_key: "robot_ev3_32x32",
      x: origin.x,
      y: origin.y,
      rotation,
    };
    const data = existing
      ? await api.updateAsset({ id: existing.id, ...payload })
      : await api.placeAsset(payload);
    setEditorWorld(data.world);
    showValidation(data.validation);
  }

  async function ensureRobotPlacementPersisted() {
    if (!robotStart) return;
    await upsertRobotPlacementFromPose(robotStart);
  }

  async function ensureRobotVisibleOnEditor() {
    if (!editorWorld || !currentWorld) return;
    const existing = robotPlacementFromEditorWorld(editorWorld);
    if (existing) {
      if (!robotStart) {
        robotStart = robotStartFromEditorWorld(editorWorld);
        if (robotStart && robotThetaInput) {
          robotThetaInput.value = String(Math.round(robotStart.theta_deg || 0));
        }
        updateRobotStartReadout();
        drawEditor();
      }
      return;
    }
    const fallbackPose = robotStart || defaultRobotPoseForWorld(editorWorld);
    robotStart = fallbackPose;
    await upsertRobotPlacementFromPose(fallbackPose);
    if (robotThetaInput) {
      robotThetaInput.value = String(Math.round(fallbackPose.theta_deg || 0));
    }
    updateRobotStartReadout();
    drawEditor();
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

  function setActiveWorldName(name) {
    const base = stripJsonExtension(name);
    activeWorldBaseName = String(base || "").trim();
    setWorldNameLabel(activeWorldBaseName);
  }

  function setSavedWorldFileName(name) {
    savedWorldFileName = String(name || "").trim();
    if (deleteSavedWorldBtn) deleteSavedWorldBtn.disabled = !savedWorldFileName;
  }

  function currentWorldName() {
    if (activeWorldBaseName) return activeWorldBaseName;
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
    await ensureRobotPlacementPersisted();
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
    setActiveWorldName(displayName);
    setSavedWorldFileName(savedFileName);
    setSimulateSavedWorldLink(savedFileName);
    log(`Mundo guardado en servidor: ${savedFileName}`);
  }

  async function downloadWorldAsFile() {
    if (!editorWorld) return;
    await ensureRobotPlacementPersisted();
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
      await hydrateRobotStartFromSnapshotIfMissing();
      await ensureRobotVisibleOnEditor();
      setActiveWorldName("");
      setSavedWorldFileName("");
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
      await hydrateRobotStartFromSnapshotIfMissing();
      await ensureRobotVisibleOnEditor();
      setActiveWorldName("");
      setSavedWorldFileName("");
      setSimulateSavedWorldLink("");
      updateSelection(null);
      showValidation(data.validation);
    } catch (err) {
      log(err.message);
    }
  });

  for (const preset of document.querySelectorAll("[data-world-size]")) {
    preset.addEventListener("click", () => {
      const [width, height] = String(preset.dataset.worldSize || "").split("x").map(Number);
      if (!Number.isFinite(width) || !Number.isFinite(height)) return;
      worldWidthInput.value = String(width);
      worldHeightInput.value = String(height);
      updateWorldSizeHint();
      document.getElementById("applyWorldSizeBtn").click();
    });
  }
  worldWidthInput?.addEventListener("input", updateWorldSizeHint);
  worldHeightInput?.addEventListener("input", updateWorldSizeHint);

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
    if (assetSelect.value) return;
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
        await upsertRobotPlacementFromPose(robotStart);
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
    if (!assetSelect.value) {
      if (clicked) {
        placementPreview = null;
        updateSelection(clicked);
        return;
      }
      placementPreview = null;
      updateSelection(null);
      return;
    }
    const point = window.EV3Canvas.canvasToEditor(canvas, event.clientX, event.clientY, currentWorld);
    const origin = window.EV3Canvas.placementOriginForAsset(assetSelect.value, point, currentWorld, 0);
    try {
      const placingRobot = String(assetSelect.value || "").includes("robot");
      const existingRobot = placingRobot ? robotPlacementFromEditorWorld(editorWorld) : null;
      const data = existingRobot
        ? await api.updateAsset({
            id: existingRobot.id,
            asset_key: existingRobot.asset_key,
            x: origin.x,
            y: origin.y,
            rotation: Number(robotThetaInput.value || existingRobot.rotation || 0),
          })
        : await api.placeAsset({
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
      await upsertRobotPlacementFromPose(robotStart);
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
        x: Math.round(Number(assetXInput.value || "0") * Number(editorWorld?.grid_size_px || 32)),
        y: Math.round(Number(assetYInput.value || "0") * Number(editorWorld?.grid_size_px || 32)),
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
      await hydrateRobotStartFromSnapshotIfMissing();
      await ensureRobotVisibleOnEditor();
      // Priorizar el nombre real del archivo abierto por el usuario.
      const inferredName = stripJsonExtension(file.name || world?.name || world?.world_name);
      setActiveWorldName(inferredName);
      setSavedWorldFileName("");
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
      await ensureRobotPlacementPersisted();
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

  deleteSavedWorldBtn?.addEventListener("click", async () => {
    if (!savedWorldFileName) return;
    if (!window.confirm(`Se eliminará permanentemente ${savedWorldFileName}. ¿Deseas continuar?`)) return;
    try {
      const response = await fetch(api.resolvePath(`/api/sessions/${api.sessionId}/editor/world/save/${encodeURIComponent(savedWorldFileName)}`), {
        method: "DELETE",
        credentials: "same-origin",
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload?.error?.message || `HTTP ${response.status}`);
      await createEditorWorld();
      updateSelection(null);
      setActiveWorldName("");
      setSavedWorldFileName("");
      setSimulateSavedWorldLink("");
      log(`Mundo eliminado: ${payload.name}. Se creó un mundo nuevo.`);
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

  window.addEventListener("pagehide", () => {
    api.closeSessionOnUnload();
  });

  window.addEventListener("beforeunload", () => {
    api.closeSessionOnUnload();
  });

  try {
    await init();
  } catch (err) {
    log(err.message);
  }
})();
