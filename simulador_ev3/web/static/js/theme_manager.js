(() => {
  const STORAGE_KEY = "ev3_theme";
  const THEMES = new Set(["light", "dark"]);

  function systemTheme() {
    return window.matchMedia?.("(prefers-color-scheme: dark)")?.matches ? "dark" : "light";
  }

  function sanitizeTheme(value) {
    return THEMES.has(value) ? value : null;
  }

  function currentTheme() {
    const stored = sanitizeTheme(window.localStorage.getItem(STORAGE_KEY));
    return stored || sanitizeTheme(document.documentElement.dataset.theme) || systemTheme();
  }

  function applyTheme(theme) {
    const normalized = sanitizeTheme(theme) || systemTheme();
    document.documentElement.setAttribute("data-theme", normalized);
    document.body?.setAttribute("data-theme", normalized);
    window.localStorage.setItem(STORAGE_KEY, normalized);
    syncControls(normalized);
  }

  function syncControls(theme) {
    for (const control of document.querySelectorAll("[data-theme-select]")) {
      if (control.value !== theme) control.value = theme;
    }
    for (const button of document.querySelectorAll("[data-theme-choice]")) {
      const isActive = button.dataset.themeChoice === theme;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", isActive ? "true" : "false");
    }
  }

  function bindThemeControls() {
    for (const control of document.querySelectorAll("[data-theme-select]")) {
      control.addEventListener("change", (event) => {
        applyTheme(event.target.value);
      });
    }
    for (const button of document.querySelectorAll("[data-theme-choice]")) {
      button.addEventListener("click", () => {
        applyTheme(button.dataset.themeChoice);
      });
    }
  }

  function initThemeManager() {
    applyTheme(currentTheme());
    bindThemeControls();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initThemeManager, { once: true });
  } else {
    initThemeManager();
  }
})();
