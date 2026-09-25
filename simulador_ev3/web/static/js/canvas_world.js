window.EV3Canvas = (() => {
  const trail = [];
  let lastTick = -1;
  const staticLayerCache = {
    canvasWidth: 0,
    canvasHeight: 0,
    selectedPlacementId: null,
    hidePlacedRobots: false,
    world: null,
    layer: null,
  };

  function invalidateStaticLayer() {
    staticLayerCache.world = null;
    staticLayerCache.layer = null;
  }
  const imageCache = new Map();
  const CELL_SIZE_MM = 100;
  const GRID_SIZE_PX = 32;
  const BASE_PX_PER_MM = GRID_SIZE_PX / CELL_SIZE_MM;
  const MIN_ZOOM = 0.5;
  const MAX_ZOOM = 3.0;
  const ZOOM_STEP = 0.15;
  const DEFAULT_FIT_PADDING_RATIO = 0.05;
  const FIT_PADDING_RATIO = (() => {
    const raw = document?.documentElement?.dataset?.ev3FitPaddingRatio;
    const parsed = Number.parseFloat(raw || "");
    if (!Number.isFinite(parsed)) return DEFAULT_FIT_PADDING_RATIO;
    return clamp(parsed, 0, 0.4);
  })();
  const DEFAULT_WORLD_MM = 4000;
  const ROBOT_WIDTH_MM = 110;
  const ROBOT_HEIGHT_MM = 70;
  const FRONT_SENSOR_OFFSET_MM = 70;
  const ULTRASONIC_MAX_MM = 2500;
  const IR_MAX_MM = 700;
  const TRAIL_TELEPORT_THRESHOLD_MM = 150;
  const FOLLOW_EDGE_MARGIN_RATIO = 0.45;
  const FOLLOW_CENTER_X = 0.5;
  const FOLLOW_CENTER_Y = 0.5;
  const zoomByCanvas = new WeakMap();

  // Inyectado por la plantilla desde AssetCatalog: no mantener una segunda
  // tabla de nombres en JavaScript, pues Tkinter usa el mismo asset_id.
  let assetFiles = window.EV3_ASSET_FILES || {};
  let assetManifest = Array.isArray(window.EV3_ASSET_MANIFEST) ? window.EV3_ASSET_MANIFEST : [];
  let assetMetadata = new Map(assetManifest.map((item) => [String(item.asset_id || ""), item]));
  const assetLayerOrder = { floor: 0, zone: 1, line: 2, wall: 3, robot: 4 };

  function dispatchAssetsLoaded() {
    window.dispatchEvent(new CustomEvent("ev3-assets-loaded"));
  }

  function hydrateAssetCatalogFromApi() {
    if (Object.keys(assetFiles).length || !window.fetch) return;
    const endpoint = window.EV3Api?.resolvePath
      ? window.EV3Api.resolvePath("/api/editor/assets")
      : "/api/editor/assets";
    window.fetch(endpoint)
      .then((response) => (response.ok ? response.json() : null))
      .then((payload) => {
        const assets = Array.isArray(payload?.assets) ? payload.assets : [];
        if (!assets.length) return;
        assetManifest = assets.map((item) => ({ ...item, asset_id: item.key || item.asset_id }));
        assetFiles = Object.fromEntries(
          assetManifest
            .filter((item) => item.asset_id && item.image)
            .map((item) => [String(item.asset_id), String(item.image)]),
        );
        assetMetadata = new Map(assetManifest.map((item) => [String(item.asset_id || ""), item]));
        invalidateStaticLayer();
        dispatchAssetsLoaded();
      })
      .catch(() => {
        // El fallback visual sigue disponible si la red no permite recuperar
        // el catálogo; no se interrumpe la simulación ni la edición.
      });
  }

  hydrateAssetCatalogFromApi();

  function resize(canvas) {
    const rect = canvas.getBoundingClientRect();
    const width = Math.max(1, Math.floor(rect.width));
    const height = Math.max(1, Math.floor(rect.height));
    if (canvas.width !== width) canvas.width = width;
    if (canvas.height !== height) canvas.height = height;
  }

  function syncCanvasWorldSize(canvas, world, view = worldView(world, canvas)) {
    const widthPx = Math.max(1, Math.round(view.widthMm * view.scale));
    const heightPx = Math.max(1, Math.round(view.heightMm * view.scale));
    const cssWidth = `${widthPx}px`;
    const cssHeight = `${heightPx}px`;
    if (canvas.style.width !== cssWidth) canvas.style.width = cssWidth;
    if (canvas.style.height !== cssHeight) canvas.style.height = cssHeight;
    const pane = canvas.parentElement;
    if (pane) {
      // En la composición apilada (<=1120 px) el mapa debe iniciar en el
      // borde visible del panel. Mantener el margen de seguimiento de
      // escritorio desplaza el canvas cientos de píxeles hacia la derecha y
      // parece que conserva un ancho/posición de escritorio.
      const compactViewport = pane.clientWidth <= 420
        || pane.clientHeight <= 360
        || window.matchMedia("(max-width: 1120px)").matches;
      const followMarginX = widthPx > pane.clientWidth
        ? (compactViewport ? 0 : Math.round(pane.clientWidth * FOLLOW_EDGE_MARGIN_RATIO))
        : 0;
      const followMarginY = heightPx > pane.clientHeight
        ? (compactViewport ? 0 : Math.round(pane.clientHeight * FOLLOW_EDGE_MARGIN_RATIO))
        : 0;
      const marginCss = `${followMarginY}px ${followMarginX}px`;
      if (canvas.style.margin !== marginCss) canvas.style.margin = marginCss;
      pane.style.justifyContent = widthPx <= pane.clientWidth ? "center" : "start";
      pane.style.alignContent = heightPx <= pane.clientHeight ? "center" : "start";
    }
  }

  function centerPaneOnPose(canvas, world, pose) {
    if (!pose) return;
    const pane = canvas.parentElement;
    if (!pane) return;
    const view = worldView(world, canvas);
    const marginLeft = Number.parseFloat(canvas.style.marginLeft || "0") || 0;
    const marginTop = Number.parseFloat(canvas.style.marginTop || "0") || 0;
    const robotX = Number(pose.x_mm);
    const robotY = Number(pose.y_mm);
    if (!Number.isFinite(robotX) || !Number.isFinite(robotY)) return;

    const desiredLeft = robotX * view.scale + marginLeft - pane.clientWidth * FOLLOW_CENTER_X;
    const desiredTop = robotY * view.scale + marginTop - pane.clientHeight * FOLLOW_CENTER_Y;
    const maxLeft = Math.max(0, pane.scrollWidth - pane.clientWidth);
    const maxTop = Math.max(0, pane.scrollHeight - pane.clientHeight);
    pane.scrollLeft = clamp(desiredLeft, 0, maxLeft);
    pane.scrollTop = clamp(desiredTop, 0, maxTop);
  }

  function worldView(world, canvas = null) {
    const widthMm = world?.width_mm || DEFAULT_WORLD_MM;
    const heightMm = world?.height_mm || DEFAULT_WORLD_MM;
    const zoom = getZoom(canvas);
    return {
      widthMm,
      heightMm,
      scale: BASE_PX_PER_MM * zoom,
      offsetX: 0,
      offsetY: 0,
    };
  }

  function getZoom(canvas) {
    if (!canvas) return 1;
    const zoom = Number(zoomByCanvas.get(canvas));
    if (!Number.isFinite(zoom)) {
      zoomByCanvas.set(canvas, 1);
      return 1;
    }
    return zoom;
  }

  function clampZoom(value) {
    return clamp(Number(value) || 1, MIN_ZOOM, MAX_ZOOM);
  }

  function setZoom(canvas, value) {
    if (!canvas) return 1;
    const nextZoom = clampZoom(value);
    const currentZoom = getZoom(canvas);
    if (Math.abs(nextZoom - currentZoom) < 1e-9) {
      return currentZoom;
    }
    zoomByCanvas.set(canvas, nextZoom);
    invalidateStaticLayer();
    return nextZoom;
  }

  function zoomIn(canvas) {
    return setZoom(canvas, getZoom(canvas) + ZOOM_STEP);
  }

  function zoomOut(canvas) {
    return setZoom(canvas, getZoom(canvas) - ZOOM_STEP);
  }

  function resetZoom(canvas) {
    return setZoom(canvas, 1);
  }

  function fitToView(canvas, world) {
    if (!canvas) return 1;
    const pane = canvas.parentElement;
    if (!pane) return getZoom(canvas);

    const widthMm = Number(world?.width_mm) || DEFAULT_WORLD_MM;
    const heightMm = Number(world?.height_mm) || DEFAULT_WORLD_MM;
    const paneW = Math.max(1, pane.clientWidth || 1);
    const paneH = Math.max(1, pane.clientHeight || 1);
    const usableW = Math.max(1, paneW * (1 - 2 * FIT_PADDING_RATIO));
    const usableH = Math.max(1, paneH * (1 - 2 * FIT_PADDING_RATIO));
    const zoomX = usableW / (Math.max(1, widthMm) * BASE_PX_PER_MM);
    const zoomY = usableH / (Math.max(1, heightMm) * BASE_PX_PER_MM);
    const nextZoom = setZoom(canvas, Math.min(zoomX, zoomY));
    pane.scrollLeft = 0;
    pane.scrollTop = 0;
    return nextZoom;
  }

  function toCanvas(view, xMm, yMm) {
    return {
      x: view.offsetX + xMm * view.scale,
      y: view.offsetY + yMm * view.scale,
    };
  }

  function sizeToCanvas(view, wMm, hMm) {
    return {
      w: wMm * view.scale,
      h: hMm * view.scale,
    };
  }

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function draw(canvas, snapshot, world, editorState = {}) {
    const view = worldView(world, canvas);
    syncCanvasWorldSize(canvas, world, view);
    resize(canvas);
    const ctx = canvas.getContext("2d");
    const baseLayer = staticWorldLayer(
      canvas,
      world,
      view,
      editorState.selectedPlacementId,
      Boolean(editorState.hidePlacedRobots),
    );

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(baseLayer, 0, 0);
    drawPlacementPreview(ctx, world?.editor_spec, view, editorState.placementPreview);

    updateTrail(snapshot?.robot, snapshot?.tick);
    drawTrail(ctx, trail, view);
    if (snapshot?.robot && editorState.showSensorBeams !== false) {
      drawSensorBeams(ctx, snapshot, view);
    }
    if (snapshot?.robot) {
      drawRobot(ctx, snapshot.robot, view, snapshot.colliding);
    }
    if (editorState.robotStart) {
      drawRobotStartMarker(ctx, editorState.robotStart, view);
    }

    const followPose = snapshot?.robot || (editorState.followRobotStart ? editorState.robotStart : null);
    // La pose interpolada se pinta hasta la frecuencia del monitor. Recentrar
    // el contenedor con scroll en cada uno de esos frames fuerza layout y
    // degrada la animación; la cámara sigue únicamente snapshots reales.
    if (!snapshot?.visual_interpolated) {
      centerPaneOnPose(canvas, world, followPose);
    }
  }

  function drawSensorBeams(ctx, snapshot, view) {
    const robot = snapshot?.robot;
    const sensors = Array.isArray(snapshot?.sensors) ? snapshot.sensors : [];
    if (!robot || !sensors.length) return;

    const thetaRad = ((Number(robot.theta_deg) || 0) * Math.PI) / 180;
    const sxMm = (Number(robot.x_mm) || 0) + Math.cos(thetaRad) * FRONT_SENSOR_OFFSET_MM;
    const syMm = (Number(robot.y_mm) || 0) + Math.sin(thetaRad) * FRONT_SENSOR_OFFSET_MM;

    for (const sensor of sensors) {
      const type = String(sensor?.type || "").toLowerCase();
      const data = sensor?.data && typeof sensor.data === "object" ? sensor.data : {};
      if (type.includes("ultrasonic")) {
        const dist = clamp(Number(data.distance_mm), 0, ULTRASONIC_MAX_MM);
        drawSensorCone(ctx, view, sxMm, syMm, thetaRad, dist || ULTRASONIC_MAX_MM, 12, "rgba(0, 188, 212, 0.16)", "#00acc1");
      } else if (type.includes("infrared")) {
        const proximity = clamp(Number(data.proximity), 0, 100);
        const dist = ((100 - proximity) / 100) * IR_MAX_MM;
        drawSensorCone(ctx, view, sxMm, syMm, thetaRad, dist || IR_MAX_MM, 8, "rgba(255, 111, 0, 0.14)", "#ff8f00");
      }
    }
  }

  function drawSensorCone(ctx, view, sxMm, syMm, angleRad, distMm, halfDeg, fill, stroke) {
    const start = toCanvas(view, sxMm, syMm);
    const left = toCanvas(
      view,
      sxMm + Math.cos(angleRad - (halfDeg * Math.PI) / 180) * distMm,
      syMm + Math.sin(angleRad - (halfDeg * Math.PI) / 180) * distMm,
    );
    const right = toCanvas(
      view,
      sxMm + Math.cos(angleRad + (halfDeg * Math.PI) / 180) * distMm,
      syMm + Math.sin(angleRad + (halfDeg * Math.PI) / 180) * distMm,
    );
    const front = toCanvas(
      view,
      sxMm + Math.cos(angleRad) * distMm,
      syMm + Math.sin(angleRad) * distMm,
    );

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.lineTo(left.x, left.y);
    ctx.lineTo(right.x, right.y);
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 1.2;
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.lineTo(front.x, front.y);
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 1.6;
    ctx.stroke();
    ctx.restore();
  }

  function resetTrail(robot = null) {
    trail.length = 0;
    lastTick = -1;
    if (robot) {
      trail.push({ x: robot.x_mm, y: robot.y_mm });
    }
  }

  function updateTrail(robot, tick) {
    if (!robot || tick === lastTick) return;
    const point = { x: robot.x_mm, y: robot.y_mm };
    const previous = trail.at(-1);
    if (previous && distanceMm(previous, point) > TRAIL_TELEPORT_THRESHOLD_MM) {
      resetTrail();
    }
    trail.push(point);
    if (trail.length > 200) trail.shift();
    lastTick = tick;
  }

  function distanceMm(a, b) {
    const dx = (a.x || 0) - (b.x || 0);
    const dy = (a.y || 0) - (b.y || 0);
    return Math.hypot(dx, dy);
  }

  function staticWorldLayer(canvas, world, view, selectedPlacementId = null, hidePlacedRobots = false) {
    const selectedId = selectedPlacementId || null;
    const worldChanged = staticLayerCache.world !== world;
    if (
      staticLayerCache.layer &&
      !worldChanged &&
      staticLayerCache.canvasWidth === canvas.width &&
      staticLayerCache.canvasHeight === canvas.height &&
      staticLayerCache.selectedPlacementId === selectedId &&
      staticLayerCache.hidePlacedRobots === hidePlacedRobots
    ) {
      return staticLayerCache.layer;
    }

    if (worldChanged) {
      trail.length = 0;
      lastTick = -1;
    }

    const layer = document.createElement("canvas");
    layer.width = canvas.width;
    layer.height = canvas.height;
    const layerCtx = layer.getContext("2d");

    layerCtx.fillStyle = "#ffffff";
    layerCtx.fillRect(0, 0, layer.width, layer.height);
    drawGrid(layerCtx, view);
    drawSurface(layerCtx, world, view);
    drawEditorPlacements(layerCtx, world?.editor_spec, view, selectedId, hidePlacedRobots);
    drawObstacles(layerCtx, world, view);

    staticLayerCache.canvasWidth = canvas.width;
    staticLayerCache.canvasHeight = canvas.height;
    staticLayerCache.selectedPlacementId = selectedId;
    staticLayerCache.hidePlacedRobots = hidePlacedRobots;
    staticLayerCache.world = world;
    staticLayerCache.layer = layer;
    return layer;
  }

  function canvasToEditor(canvas, clientX, clientY, world) {
    const { xMm, yMm } = canvasToWorld(canvas, clientX, clientY, world);
    const gridSizePx = world?.editor_spec?.grid_size_px || GRID_SIZE_PX;
    const x = Math.round(xMm / CELL_SIZE_MM) * gridSizePx;
    const y = Math.round(yMm / CELL_SIZE_MM) * gridSizePx;
    return { x, y, xMm, yMm };
  }

  function canvasToWorld(canvas, clientX, clientY, world) {
    const rect = canvas.getBoundingClientRect();
    const view = worldView(world, canvas);
    return {
      xMm: clamp((clientX - rect.left - view.offsetX) / view.scale, 0, view.widthMm),
      yMm: clamp((clientY - rect.top - view.offsetY) / view.scale, 0, view.heightMm),
    };
  }

  function findPlacementAt(canvas, clientX, clientY, world) {
    const spec = world?.editor_spec;
    if (!spec?.placements) return null;
    const point = canvasToEditor(canvas, clientX, clientY, world);
      const gridSize = spec.grid_size_px || GRID_SIZE_PX;
    const placements = [...spec.placements].reverse();
    for (const placement of placements) {
      const size = assetSize(placement.asset_key, placement.rotation);
      const x0 = placement.x ?? placement.x_px ?? 0;
      const y0 = placement.y ?? placement.y_px ?? 0;
      const x1 = x0 + size.w * gridSize;
      const y1 = y0 + size.h * gridSize;
      if (point.x >= x0 && point.x < x1 && point.y >= y0 && point.y < y1) {
        return placement;
      }
    }
    return null;
  }

  function drawGrid(ctx, view) {
    const worldW = view.widthMm * view.scale;
    const worldH = view.heightMm * view.scale;
    ctx.fillStyle = "#f8fafc";
    ctx.fillRect(view.offsetX, view.offsetY, worldW, worldH);
    ctx.strokeStyle = "#e8edf3";
    ctx.lineWidth = 1;
    const step = CELL_SIZE_MM;
    for (let x = 0; x <= view.widthMm; x += step) {
      const px = view.offsetX + x * view.scale;
      ctx.beginPath();
      ctx.moveTo(px, view.offsetY);
      ctx.lineTo(px, view.offsetY + worldH);
      ctx.stroke();
    }
    for (let y = 0; y <= view.heightMm; y += step) {
      const py = view.offsetY + y * view.scale;
      ctx.beginPath();
      ctx.moveTo(view.offsetX, py);
      ctx.lineTo(view.offsetX + worldW, py);
      ctx.stroke();
    }
    ctx.strokeStyle = "#b0bec5";
    ctx.strokeRect(view.offsetX, view.offsetY, worldW, worldH);
  }

  function drawSurface(ctx, world, view) {
    // Los mundos de seguidor de línea conservan una superficie física negra
    // para los sensores y placements ``line_*`` para su apariencia. Mostrar
    // ambos duplicaba la pista en Web; Tkinter ya usa los placements como la
    // capa visual autoritativa.
    if (world?.editor_spec?.placements?.length) return;
    if (!world?.surface?.cells) return;
    const cs = world.surface.cell_size_mm || 50;
    for (const cell of world.surface.cells) {
      if (cell.color === "WHITE") continue;
      ctx.fillStyle = colorFor(cell.color);
      const pos = toCanvas(view, cell.col * cs, cell.row * cs);
      const size = sizeToCanvas(view, cs, cs);
      ctx.fillRect(pos.x, pos.y, size.w, size.h);
    }
  }

  function drawEditorPlacements(ctx, spec, view, selectedId, hidePlacedRobots = false) {
    if (!spec?.placements) return;
    const gridSize = spec.grid_size_px || GRID_SIZE_PX;
    const mmPerPx = CELL_SIZE_MM / gridSize;
    const normalPlacements = [];
    const robotPlacements = [];
    for (const placement of spec.placements) {
      const key = placement.asset_key || "";
      if (String(key).includes("robot")) robotPlacements.push(placement);
      else normalPlacements.push(placement);
    }
    normalPlacements.sort((left, right) => {
      const leftLayer = assetLayerOrder[assetMetadata.get(String(left.asset_key || ""))?.layer] ?? 4;
      const rightLayer = assetLayerOrder[assetMetadata.get(String(right.asset_key || ""))?.layer] ?? 4;
      return leftLayer - rightLayer || Number(left.y || left.y_px || 0) - Number(right.y || right.y_px || 0);
    });
    const orderedPlacements = [...normalPlacements, ...robotPlacements];

    for (const placement of orderedPlacements) {
      const key = placement.asset_key;
      if (hidePlacedRobots && key?.includes("robot")) {
        continue;
      }
      const xPx = placement.x ?? placement.x_px ?? 0;
      const yPx = placement.y ?? placement.y_px ?? 0;
      const size = assetSize(key, placement.rotation);
      const pos = toCanvas(view, xPx * mmPerPx, yPx * mmPerPx);
      const canvasSize = sizeToCanvas(view, size.w * CELL_SIZE_MM, size.h * CELL_SIZE_MM);
      const isSelected = Boolean(selectedId) && placement.id === selectedId;

      ctx.save();
      drawAsset(ctx, key, pos.x, pos.y, canvasSize.w, canvasSize.h, placement.rotation || 0);
      if (isSelected) {
        ctx.strokeStyle = "#f08c00";
        ctx.lineWidth = 4;
        ctx.strokeRect(pos.x, pos.y, canvasSize.w, canvasSize.h);
      }
      ctx.restore();
    }
  }

  function drawPlacementPreview(ctx, spec, view, preview) {
    if (!spec || !preview?.asset_key) return;
    const gridSize = spec.grid_size_px || GRID_SIZE_PX;
    const mmPerPx = CELL_SIZE_MM / gridSize;
    const size = assetSize(preview.asset_key, preview.rotation || 0);
    const xPx = preview.x ?? preview.x_px ?? 0;
    const yPx = preview.y ?? preview.y_px ?? 0;
    const pos = toCanvas(view, xPx * mmPerPx, yPx * mmPerPx);
    const canvasSize = sizeToCanvas(view, size.w * CELL_SIZE_MM, size.h * CELL_SIZE_MM);

    ctx.save();
    ctx.setLineDash([2, 2]);
    ctx.strokeStyle = "#006CFF";
    ctx.lineWidth = 2;
    ctx.strokeRect(pos.x + 0.5, pos.y + 0.5, canvasSize.w - 1, canvasSize.h - 1);
    ctx.restore();
  }

  function drawObstacles(ctx, world, view) {
    if (!world?.obstacles) return;
    for (const obstacle of world.obstacles) {
      const vertices = obstacle.vertices || [];
      if (!vertices.length) continue;

      // Los mundos históricos describen las cajas únicamente en la geometría
      // física del obstáculo. Su nombre conserva el asset original, por
      // ejemplo ``wall:wall_64x64_b:wall_0002``. Tkinter ya usa ese dato para
      // pintar la textura; si la Web lo ignoraba, mostraba un rectángulo gris.
      const textured = obstacleAssetRectangle(obstacle, vertices);
      if (textured) {
        const start = toCanvas(view, textured.xMm, textured.yMm);
        const size = sizeToCanvas(view, textured.widthMm, textured.heightMm);
        drawAsset(ctx, textured.assetKey, start.x, start.y, size.w, size.h);
        continue;
      }

      ctx.fillStyle = "#39485c";
      ctx.strokeStyle = "#162233";
      ctx.beginPath();
      const first = toCanvas(view, vertices[0][0], vertices[0][1]);
      ctx.moveTo(first.x, first.y);
      for (const vertex of vertices.slice(1)) {
        const point = toCanvas(view, vertex[0], vertex[1]);
        ctx.lineTo(point.x, point.y);
      }
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    }
  }

  function obstacleAssetRectangle(obstacle, vertices) {
    const match = String(obstacle?.name || "").match(/^[^:]+:([^:]+):/);
    const assetKey = match?.[1] || "";
    // Solo se transforma una caja rectangular explícitamente identificada.
    // Obstáculos arbitrarios conservan el polígono físico como fallback.
    if (!assetFiles[assetKey] || !Array.isArray(vertices) || vertices.length !== 4) return null;
    const xValues = vertices.map((vertex) => Number(vertex?.[0]));
    const yValues = vertices.map((vertex) => Number(vertex?.[1]));
    if (![...xValues, ...yValues].every(Number.isFinite)) return null;
    const uniqueX = [...new Set(xValues)];
    const uniqueY = [...new Set(yValues)];
    if (uniqueX.length !== 2 || uniqueY.length !== 2) return null;
    const xMm = Math.min(...uniqueX);
    const yMm = Math.min(...uniqueY);
    const widthMm = Math.max(...uniqueX) - xMm;
    const heightMm = Math.max(...uniqueY) - yMm;
    if (widthMm <= 0 || heightMm <= 0) return null;
    return { assetKey, xMm, yMm, widthMm, heightMm };
  }

  function drawTrail(ctx, points, view) {
    if (points.length < 2) return;
    ctx.strokeStyle = "#1f8fce";
    ctx.lineWidth = 2;
    const first = toCanvas(view, points[0].x, points[0].y);
    ctx.beginPath();
    ctx.moveTo(first.x, first.y);
    for (const point of points.slice(1)) {
      const pos = toCanvas(view, point.x, point.y);
      ctx.lineTo(pos.x, pos.y);
    }
    ctx.stroke();
  }

  function drawRobot(ctx, robot, view, colliding) {
    const pos = toCanvas(view, robot.x_mm, robot.y_mm);
    const theta = (robot.theta_deg || 0) * Math.PI / 180;
    // El sprite es cuadrado: no se estira para ajustarlo al rectángulo físico.
    const visualSideMm = Math.max(ROBOT_WIDTH_MM, ROBOT_HEIGHT_MM);
    const size = sizeToCanvas(view, visualSideMm, visualSideMm);
    const w = size.w;
    const h = size.h;
    ctx.save();
    ctx.translate(pos.x, pos.y);
    ctx.rotate(theta);
    const img = getAssetImage("robot_ev3_32x32");
    if (img?.complete && img.naturalWidth > 0) {
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(img, -w / 2, -h / 2, w, h);
      if (colliding) {
        ctx.strokeStyle = "#d62828";
        ctx.lineWidth = 2;
        ctx.strokeRect(-w / 2, -h / 2, w, h);
      }
      ctx.restore();
      return;
    }

    ctx.fillStyle = "#f5f7fb";
    ctx.strokeStyle = colliding ? "#d62828" : "#20364f";
    ctx.lineWidth = 4;
    ctx.fillRect(-w / 2, -h / 2, w, h);
    ctx.strokeRect(-w / 2, -h / 2, w, h);
    ctx.fillStyle = "#20364f";
    ctx.fillRect(w * 0.1, -h * 0.18, w * 0.28, h * 0.36);
    ctx.fillStyle = "#2f9e44";
    ctx.beginPath();
    ctx.moveTo(w / 2 + 18, 0);
    ctx.lineTo(w / 2 - 12, -16);
    ctx.lineTo(w / 2 - 12, 16);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  function drawRobotStartMarker(ctx, pose, view) {
    const pos = toCanvas(view, pose.x_mm, pose.y_mm);
    const theta = (pose.theta_deg || 0) * Math.PI / 180;
    ctx.save();
    ctx.translate(pos.x, pos.y);
    ctx.rotate(theta);
    ctx.strokeStyle = "#f08c00";
    ctx.fillStyle = "rgba(240, 140, 0, 0.16)";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(0, 0, 18, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(34, 0);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(34, 0);
    ctx.lineTo(24, -7);
    ctx.moveTo(34, 0);
    ctx.lineTo(24, 7);
    ctx.stroke();
    ctx.restore();
  }

  function colorFor(name) {
    return {
      BLACK: "#101820",
      RED: "#d62828",
      GREEN: "#2f9e44",
      BLUE: "#1971c2",
      YELLOW: "#f5c542",
    }[name] || "#e9ecef";
  }

  function drawAsset(ctx, key, x, y, w, h, rotation = 0) {
    const img = getAssetImage(key);
    const angle = ((Number(rotation) || 0) % 360 + 360) % 360;
    if (angle) {
      ctx.save();
      ctx.translate(x + w / 2, y + h / 2);
      ctx.rotate(angle * Math.PI / 180);
      if (img?.complete && img.naturalWidth > 0) {
        ctx.drawImage(img, -w / 2, -h / 2, w, h);
      } else {
        drawFallbackAsset(ctx, key, -w / 2, -h / 2, w, h);
      }
      ctx.restore();
      return;
    }
    if (img?.complete && img.naturalWidth > 0) {
      ctx.drawImage(img, x, y, w, h);
      return;
    }
    drawFallbackAsset(ctx, key, x, y, w, h);
  }

  function getAssetImage(key) {
    const file = assetFiles[key];
    if (!file) return null;
    if (imageCache.has(file)) return imageCache.get(file);
    const img = new Image();
    const src = window.EV3Api?.resolvePath
      ? window.EV3Api.resolvePath(`/assets/${encodeURIComponent(file)}`)
      : `/assets/${encodeURIComponent(file)}`;
    img.onload = () => {
      invalidateStaticLayer();
      dispatchAssetsLoaded();
    };
    img.src = src;
    imageCache.set(file, img);
    return img;
  }

  function isAssetReady(key) {
    const file = assetFiles[key];
    const image = file ? imageCache.get(file) : null;
    return Boolean(image?.complete && image.naturalWidth > 0);
  }

  function drawFallbackAsset(ctx, key, x, y, w, h) {
    ctx.fillStyle = fillForAsset(key);
    ctx.fillRect(x, y, w, h);
    const shouldDrawLabel =
      !key?.includes("line") &&
      !key?.includes("wall") &&
      !key?.includes("floor") &&
      w >= 42 &&
      h >= 24;
    if (shouldDrawLabel) {
      ctx.fillStyle = textColorForAsset(key);
      ctx.font = "12px Segoe UI, Arial";
      ctx.fillText(labelForAsset(key), x + 6, y + 17);
    }
    if (key.includes("line")) {
      drawLineSymbol(ctx, key, x, y, w, h);
    }
    if (key.includes("robot")) {
      ctx.fillStyle = "#2f9e44";
      ctx.beginPath();
      ctx.moveTo(x + w * 0.72, y + h * 0.5);
      ctx.lineTo(x + w * 0.48, y + h * 0.35);
      ctx.lineTo(x + w * 0.48, y + h * 0.65);
      ctx.closePath();
      ctx.fill();
    }
  }

  function assetSize(key, rotation = 0) {
    const metadata = assetMetadata.get(String(key || ""));
    const size = {
      w: Number(metadata?.width_cells) || 2,
      h: Number(metadata?.height_cells) || 2,
    };
    if (Math.abs(rotation) % 180 === 90) {
      return { w: size.h, h: size.w };
    }
    return size;
  }

  function placementOriginForAsset(assetKey, point, world, rotation = 0) {
    const spec = world?.editor_spec || {};
    const gridSize = spec.grid_size_px || GRID_SIZE_PX;
    const worldWidthPx = Math.round((world?.width_mm || DEFAULT_WORLD_MM) / CELL_SIZE_MM * gridSize);
    const worldHeightPx = Math.round((world?.height_mm || DEFAULT_WORLD_MM) / CELL_SIZE_MM * gridSize);
    const size = assetSize(assetKey, rotation);
    const widthPx = size.w * gridSize;
    const heightPx = size.h * gridSize;
    const rawX = point.x - Math.floor(size.w / 2) * gridSize;
    const rawY = point.y - Math.floor(size.h / 2) * gridSize;
    const snappedX = Math.round(rawX / gridSize) * gridSize;
    const snappedY = Math.round(rawY / gridSize) * gridSize;
    return {
      x: clamp(snappedX, 0, Math.max(0, worldWidthPx - widthPx)),
      y: clamp(snappedY, 0, Math.max(0, worldHeightPx - heightPx)),
    };
  }

  function placementMoveTarget(placement, point, world, offset = { x: 0, y: 0 }) {
    const spec = world?.editor_spec || {};
    const gridSize = spec.grid_size_px || GRID_SIZE_PX;
    const worldWidthPx = Math.round((world?.width_mm || DEFAULT_WORLD_MM) / CELL_SIZE_MM * gridSize);
    const worldHeightPx = Math.round((world?.height_mm || DEFAULT_WORLD_MM) / CELL_SIZE_MM * gridSize);
    const size = assetSize(placement?.asset_key, placement?.rotation || 0);
    const widthPx = size.w * gridSize;
    const heightPx = size.h * gridSize;
    const snappedX = Math.round((point.x + (offset.x || 0)) / gridSize) * gridSize;
    const snappedY = Math.round((point.y + (offset.y || 0)) / gridSize) * gridSize;
    return {
      x: clamp(snappedX, 0, Math.max(0, worldWidthPx - widthPx)),
      y: clamp(snappedY, 0, Math.max(0, worldHeightPx - heightPx)),
    };
  }

  function fillForAsset(key) {
    if (key?.includes("wall")) return "#43546a";
    if (key?.includes("zone_red")) return "rgba(214, 40, 40, 0.35)";
    if (key?.includes("zone_green")) return "rgba(47, 158, 68, 0.35)";
    if (key?.includes("line")) return "rgba(16, 24, 32, 0.08)";
    if (key?.includes("robot")) return "#f5f7fb";
    if (key?.includes("floor")) return "#eef2f6";
    return "#edf2f7";
  }

  function strokeForAsset(key) {
    if (key?.includes("wall")) return "#172235";
    if (key?.includes("line")) return "#101820";
    if (key?.includes("robot")) return "#20364f";
    return "#6b7d90";
  }

  function textColorForAsset(key) {
    return key?.includes("wall") ? "#fff" : "#1f2937";
  }

  function labelForAsset(key) {
    if (key?.includes("robot")) return "EV3";
    if (key?.includes("wall")) return "muro";
    if (key?.includes("zone_red")) return "rojo";
    if (key?.includes("zone_green")) return "verde";
    if (key?.includes("zone_white")) return "zona";
    if (key?.includes("line")) return "linea";
    if (key?.includes("floor")) return "piso";
    return "asset";
  }

  function drawLineSymbol(ctx, key, x, y, w, h) {
    ctx.strokeStyle = "#101820";
    ctx.lineWidth = Math.max(3, Math.min(w, h) * 0.08);
    const cx = x + w / 2;
    const cy = y + h / 2;
    ctx.beginPath();
    if (key.includes("hor") || key.includes("cruz")) {
      ctx.moveTo(x + 8, cy);
      ctx.lineTo(x + w - 8, cy);
    }
    if (key.includes("ver") || key.includes("cruz")) {
      ctx.moveTo(cx, y + 8);
      ctx.lineTo(cx, y + h - 8);
    }
    if (key.includes("inf") || key.includes("sup")) {
      ctx.moveTo(cx, cy);
      ctx.lineTo(key.includes("izq") ? x + w - 8 : x + 8, cy);
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx, key.includes("sup") ? y + h - 8 : y + 8);
    }
    ctx.stroke();
  }

  return {
    draw,
    resetTrail,
    zoomIn,
    zoomOut,
    resetZoom,
    fitToView,
    getZoom,
    canvasToEditor,
    canvasToWorld,
    findPlacementAt,
    placementOriginForAsset,
    placementMoveTarget,
    isAssetReady,
  };
})();
