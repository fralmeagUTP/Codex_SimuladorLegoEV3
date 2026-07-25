/* Conecta eventos del editor sin acoplarlos a la sesión. */
window.EV3EditorInteractionController = {
  bind(editor, handlers) {
    editor.addEventListener("input", handlers.input);
    editor.addEventListener("keydown", handlers.keydown);
    editor.addEventListener("keyup", handlers.keyup);
    editor.addEventListener("blur", handlers.blur);
    editor.addEventListener("scroll", handlers.scroll);
  },
};
