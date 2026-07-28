/* Aísla el ciclo de selección y limpieza de archivos de la UI. */
window.EV3FileInputController = {
  bind(input, onSelected) {
    input?.addEventListener("change", async () => {
      const [file] = input.files || [];
      if (!file) return;
      try {
        await onSelected(file);
      } finally {
        input.value = "";
      }
    });
  },
};
