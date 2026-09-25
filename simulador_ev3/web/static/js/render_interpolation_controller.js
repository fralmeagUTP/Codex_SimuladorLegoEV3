/* Interpola solo la pose visual; telemetría y LCD siguen siendo autoritativas. */
window.EV3RenderInterpolationController = {
  create({ onRender, now = () => performance.now(), raf = requestAnimationFrame }) {
    let previous = null; let current = null; let receivedAt = 0; let pending = false;
    let receivedSnapshots = 0; let renderedFrames = 0; let interpolatedFrames = 0;
    const terminal = new Set(["finished", "stopped", "timed_out", "error", "created"]);
    const lerp = (a, b, t) => a + ((b - a) * t);
    const angle = (a, b, t) => a + (((((b - a) + 540) % 360) - 180) * t);
    const compatible = (a, b) => a?.robot && b?.robot && a.snapshot_generation === b.snapshot_generation
      && Number(b.tick) > Number(a.tick) && !a.colliding && !b.colliding && !terminal.has(String(b.status || ""));
    const frame = () => {
      pending = false;
      if (!compatible(previous, current)) return;
      // El motor avanza a 50 Hz (20 ms). No imponer 33 ms aquí: con snapshots
      // a 50 Hz se retrasaba artificialmente cada pose y se percibía a saltos.
      const duration = Math.min(120, Math.max(16, (Number(current.tick) - Number(previous.tick)) * 20));
      const t = Math.min(1, (now() - receivedAt) / duration);
      renderedFrames += 1;
      if (t < 1) interpolatedFrames += 1;
      onRender({ ...current, robot: { ...current.robot, x_mm: lerp(+previous.robot.x_mm, +current.robot.x_mm, t), y_mm: lerp(+previous.robot.y_mm, +current.robot.y_mm, t), theta_deg: angle(+previous.robot.theta_deg, +current.robot.theta_deg, t) }, visual_interpolated: t < 1 });
      if (t < 1) schedule();
    };
    const schedule = () => { if (!pending) { pending = true; raf(frame); } };
    return {
      apply(snapshot) { receivedSnapshots += 1; previous = current; current = snapshot; receivedAt = now(); if (!compatible(previous, current)) { onRender(current); return; } onRender({ ...current, robot: { ...previous.robot }, visual_interpolated: true }); schedule(); },
      reset() { previous = null; current = null; pending = false; },
      diagnostics() { return { receivedSnapshots, renderedFrames, interpolatedFrames }; },
    };
  },
};
