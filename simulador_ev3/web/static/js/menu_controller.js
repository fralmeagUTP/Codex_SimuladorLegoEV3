(() => {
  function closeGroup(group) {
    if (!group) return;
    const trigger = group.querySelector(".menu-trigger");
    group.classList.remove("is-open");
    if (trigger) trigger.setAttribute("aria-expanded", "false");
  }

  function closeAll(groups, except = null) {
    for (const group of groups) {
      if (group === except) continue;
      closeGroup(group);
    }
  }

  function firstFocusableItem(group) {
    return group.querySelector(".menu-dropdown button, .menu-dropdown a");
  }

  function bindMenuBar(menuBar) {
    const groups = Array.from(menuBar.querySelectorAll(".menu-group"));
    if (!groups.length) return;

    for (const group of groups) {
      const trigger = group.querySelector(".menu-trigger");
      if (!trigger) continue;
      trigger.setAttribute("aria-expanded", "false");

      trigger.addEventListener("click", (event) => {
        event.preventDefault();
        const willOpen = !group.classList.contains("is-open");
        closeAll(groups);
        if (!willOpen) return;
        group.classList.add("is-open");
        trigger.setAttribute("aria-expanded", "true");
      });

      trigger.addEventListener("keydown", (event) => {
        if (!["Enter", " ", "ArrowDown"].includes(event.key)) return;
        event.preventDefault();
        closeAll(groups);
        group.classList.add("is-open");
        trigger.setAttribute("aria-expanded", "true");
        firstFocusableItem(group)?.focus();
      });

      group.addEventListener("mouseleave", () => {
        if (group.contains(document.activeElement)) return;
        closeGroup(group);
      });
    }

    menuBar.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (!target.closest(".menu-dropdown button, .menu-dropdown a")) return;
      // Un submenú cambia su propio estado; no es todavía una acción terminal.
      // Cerrar aquí impedía abrir los mundos preestablecidos con clic o teclado.
      if (target.closest(".menu-subtoggle")) return;
      closeAll(groups);
    });

    document.addEventListener("click", (event) => {
      if (menuBar.contains(event.target)) return;
      closeAll(groups);
    });

    document.addEventListener("focusin", (event) => {
      if (menuBar.contains(event.target)) return;
      closeAll(groups);
    });

    document.addEventListener("keydown", (event) => {
      if (event.key !== "Escape") return;
      const opened = groups.find((group) => group.classList.contains("is-open"));
      closeAll(groups);
      if (opened) {
        const trigger = opened.querySelector(".menu-trigger");
        trigger?.focus();
      }
    });
  }

  function initMenuController() {
    for (const menuBar of document.querySelectorAll(".menu-bar")) {
      bindMenuBar(menuBar);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMenuController, { once: true });
  } else {
    initMenuController();
  }
})();
