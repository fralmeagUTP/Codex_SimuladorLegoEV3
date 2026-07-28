/* Encapsula el dibujo y zoom del mundo. */
window.EV3WorldViewController = {
  create({ canvas, getViewState }) {
    function draw() {
      const state = getViewState();
      window.EV3Canvas.draw(canvas, state.snapshot, state.world, {
        hidePlacedRobots: true,
        robotStart: state.robotStart,
        showSensorBeams: state.showSensorBeams,
      });
    }
    return {
      draw,
      zoom(action) {
        const state = getViewState();
        if (action === "in") window.EV3Canvas.zoomIn(canvas);
        else if (action === "out") window.EV3Canvas.zoomOut(canvas);
        else window.EV3Canvas.fitToView(canvas, state.world);
        draw();
      },
    };
  },
};
