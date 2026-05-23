window.EV3Canvas = (() => {
  const trail = [];
  let lastTick = -1;
  const staticLayerCache = {
    canvasWidth: 0,
    canvasHeight: 0,
    selectedPlacementId: null,
    world: null,
    layer: null,
  };
  const imageCache = new Map();
  const CELL_SIZE_MM = 100;
  const GRID_SIZE_PX = 32;
  const PX_PER_MM = GRID_SIZE_PX / CELL_SIZE_MM;
  const DEFAULT_WORLD_MM = 4000;
  const ROBOT_WIDTH_MM = 110;
  const ROBOT_HEIGHT_MM = 70;
  const TRAIL_TELEPORT_THRESHOLD_MM = 150;

  const assetFiles = {
    robot_ev3_32x32: "robot_ev3_32x32.png",
    wall_64x64_a: "wall_64x64_a.png",
    wall_64x64_b: "wall_64x64_b.png",
    wall_64x64_c: "wall_64x64_c.png",
    zone_green_128: "zone_green_128.png",
    zone_red_128: "zone_red_128.png",
    zone_white_128: "zone_white_128.png",
    line_64_64_hor: "line_64_64_Hor.png",
    line_64_64_ver: "line_64_64_Ver.png",
    line_64x64_cruz: "line_64X64_Cruz.png",
    line_64_64_infder: "line_64_64_InfDer.png",
    line_64_64_infizq: "line_64_64_InfIzq.png",
    line_64_64_supder: "line_64_64_SupDer.png",
    line_64_64_supizq: "line_64_64_SupIzq.png",
    floor_tile_256_a: "floor_tile_256_a.png",
    floor_tile_256_b: "floor_tile_256_b.png",
    floor_tile_256_c: "floor_tile_256_c.jpg",
  };

  function resize(canvas) {
    const rect = canvas.getBoundingClientRect();
    const width = Math.max(1, Math.floor(rect.width));
    const height = Math.max(1, Math.floor(rect.height));
    if (canvas.width !== width) canvas.width = width;
    if (canvas.height !== height) canvas.height = height;
  }

  function syncCanvasWorldSize(canvas, world) {
    const view = worldView(world);
    const widthPx = Math.max(1, Math.round(view.widthMm * PX_PER_MM));
    const heightPx = Math.max(1, Math.round(view.heightMm * PX_PER_MM));
    const cssWidth = `${widthPx}px`;
    const cssHeight = `${heightPx}px`;
    if (canvas.style.width !== cssWidth) canvas.style.width = cssWidth;
    if (canvas.style.height !== cssHeight) canvas.style.height = cssHeight;
    const pane = canvas.parentElement;
    if (pane) {
      pane.style.justifyContent = widthPx <= pane.clientWidth ? "center" : "start";
      pane.style.alignContent = heightPx <= pane.clientHeight ? "center" : "start";
    }
  }

  function worldView(world) {
    const widthMm = world?.width_mm || DEFAULT_WORLD_MM;
    const heightMm = world?.height_mm || DEFAULT_WORLD_MM;
    return {
      widthMm,
      heightMm,
      scale: PX_PER_MM,
      offsetX: 0,
      offsetY: 0,
    };
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
    syncCanvasWorldSize(canvas, world);
    resize(canvas);
    const ctx = canvas.getContext("2d");
    const view = worldView(world);
    const baseLayer = staticWorldLayer(canvas, world, view, editorState.selectedPlacementId);

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(baseLayer, 0, 0);
    drawPlacementPreview(ctx, world?.editor_spec, view, editorState.placementPreview);

    updateTrail(snapshot?.robot, snapshot?.tick);
    drawTrail(ctx, trail, view);
    if (snapshot?.robot) {
      drawRobot(ctx, snapshot.robot, view, snapshot.colliding);
    }
    if (editorState.robotStart) {
      drawRobotStartMarker(ctx, editorState.robotStart, view);
    }
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

  function staticWorldLayer(canvas, world, view, selectedPlacementId = null) {
    const selectedId = selectedPlacementId || null;
    const worldChanged = staticLayerCache.world !== world;
    if (
      staticLayerCache.layer &&
      !worldChanged &&
      staticLayerCache.canvasWidth === canvas.width &&
      staticLayerCache.canvasHeight === canvas.height &&
      staticLayerCache.selectedPlacementId === selectedId
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
    drawEditorPlacements(layerCtx, world?.editor_spec, view, selectedId);
    drawObstacles(layerCtx, world, view);

    staticLayerCache.canvasWidth = canvas.width;
    staticLayerCache.canvasHeight = canvas.height;
    staticLayerCache.selectedPlacementId = selectedId;
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
    const view = worldView(world);
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

  function drawEditorPlacements(ctx, spec, view, selectedId) {
    if (!spec?.placements) return;
    const gridSize = spec.grid_size_px || GRID_SIZE_PX;
    const mmPerPx = CELL_SIZE_MM / gridSize;
    for (const placement of spec.placements) {
      const key = placement.asset_key;
      const xPx = placement.x ?? placement.x_px ?? 0;
      const yPx = placement.y ?? placement.y_px ?? 0;
      const size = assetSize(key, placement.rotation);
      const pos = toCanvas(view, xPx * mmPerPx, yPx * mmPerPx);
      const canvasSize = sizeToCanvas(view, size.w * CELL_SIZE_MM, size.h * CELL_SIZE_MM);

      ctx.save();
      drawAsset(ctx, key, pos.x, pos.y, canvasSize.w, canvasSize.h);
      ctx.strokeStyle = placement.id === selectedId ? "#f08c00" : strokeForAsset(key);
      ctx.lineWidth = placement.id === selectedId ? 4 : 1.5;
      ctx.strokeRect(pos.x, pos.y, canvasSize.w, canvasSize.h);
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
    ctx.fillStyle = "#39485c";
    ctx.strokeStyle = "#162233";
    for (const obstacle of world.obstacles) {
      const vertices = obstacle.vertices || [];
      if (!vertices.length) continue;
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
    const size = sizeToCanvas(view, ROBOT_WIDTH_MM, ROBOT_HEIGHT_MM);
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

  function drawAsset(ctx, key, x, y, w, h) {
    const img = getAssetImage(key);
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
    img.onload = () => window.dispatchEvent(new CustomEvent("ev3-assets-loaded"));
    img.src = `/assets/images/${encodeURIComponent(file)}`;
    imageCache.set(file, img);
    return img;
  }

  function drawFallbackAsset(ctx, key, x, y, w, h) {
    ctx.fillStyle = fillForAsset(key);
    ctx.fillRect(x, y, w, h);
    ctx.fillStyle = textColorForAsset(key);
    ctx.font = "12px Segoe UI, Arial";
    ctx.fillText(labelForAsset(key), x + 6, y + 17);
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
    let size = { w: 2, h: 2 };
    if (key?.includes("robot")) size = { w: 1, h: 1 };
    if (key?.includes("zone")) size = { w: 4, h: 4 };
    if (key?.includes("floor")) size = { w: 8, h: 8 };
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
    canvasToEditor,
    canvasToWorld,
    findPlacementAt,
    placementOriginForAsset,
    placementMoveTarget,
  };
})();
