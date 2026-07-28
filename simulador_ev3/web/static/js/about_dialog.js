/* Controla el dialogo informativo sin acoplarlo a la simulacion. */
window.EV3AboutDialog = {
  create(message) {
    const dialog = document.getElementById("aboutDialog");
    const backdrop = document.getElementById("aboutDialogBackdrop");
    const text = document.getElementById("aboutDialogText");
    const close = () => {
      dialog?.classList.add("hidden");
      backdrop?.classList.add("hidden");
    };
    const open = () => {
      if (text) text.textContent = message;
      dialog?.classList.remove("hidden");
      backdrop?.classList.remove("hidden");
    };
    document.getElementById("aboutDialogCloseBtn")?.addEventListener("click", close);
    document.getElementById("aboutDialogOkBtn")?.addEventListener("click", close);
    backdrop?.addEventListener("click", close);
    return { close, open, isOpen: () => Boolean(dialog && !dialog.classList.contains("hidden")) };
  },
};
