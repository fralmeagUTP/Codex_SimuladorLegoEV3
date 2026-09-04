(() => {
  "use strict";

  const splash = document.getElementById("startupSplash");
  if (!splash) return;

  const dismiss = () => {
    if (splash.dataset.dismissed === "true") return;
    splash.dataset.dismissed = "true";
    splash.classList.add("startup-splash--leaving");
    window.setTimeout(() => splash.remove(), 220);
  };

  window.setTimeout(dismiss, 3000);
})();
