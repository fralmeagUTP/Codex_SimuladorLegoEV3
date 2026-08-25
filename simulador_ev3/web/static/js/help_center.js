(() => {
  const root = document.querySelector("[data-help-center]");
  if (!root) return;

  const storageKey = "ev3-help-guide-progress-v1";
  const search = root.querySelector("#helpSearch");
  const status = root.querySelector("#helpSearchStatus");
  const empty = root.querySelector("#helpEmptyState");
  const guides = [...root.querySelectorAll("[data-help-guide]")];
  const categories = [...root.querySelectorAll("[data-help-category]")];
  const teacherToggle = root.querySelector("[data-teacher-mode]");
  const teacherRoute = root.querySelector("[data-teacher-route]");
  let activeCategory = "all";

  const loadProgress = () => {
    try {
      const stored = JSON.parse(window.localStorage.getItem(storageKey) || "{}");
      return stored && typeof stored === "object" ? stored : {};
    } catch {
      return {};
    }
  };
  let progressByGuide = loadProgress();

  const saveProgress = () => {
    try {
      window.localStorage.setItem(storageKey, JSON.stringify(progressByGuide));
    } catch {
      // El Centro de ayuda sigue siendo utilizable si el navegador bloquea almacenamiento local.
    }
  };

  const renderGuideProgress = (guideId) => {
    const card = root.querySelector(`[data-help-guide][id="guide-${guideId}"]`);
    if (!card) return;
    const steps = [...card.querySelectorAll("[data-guide-step]")];
    const completed = new Set(Array.isArray(progressByGuide[guideId]) ? progressByGuide[guideId] : []);
    steps.forEach((step) => {
      step.checked = completed.has(step.dataset.stepId);
    });
    const done = steps.filter((step) => step.checked).length;
    const panel = card.querySelector("[data-guide-progress]");
    panel.querySelector("progress").value = done;
    panel.querySelector("span").textContent = `${done} de ${steps.length} pasos${done === steps.length ? " · Guía completada" : ""}`;
  };

  const applyFilter = () => {
    const query = search.value.trim().toLocaleLowerCase("es");
    let visible = 0;
    guides.forEach((guide) => {
      const matchesCategory = activeCategory === "all" || guide.dataset.category === activeCategory;
      const matchesQuery = !query || guide.dataset.search.toLocaleLowerCase("es").includes(query);
      const isVisible = matchesCategory && matchesQuery;
      guide.hidden = !isVisible;
      if (isVisible) visible += 1;
    });
    empty.hidden = visible !== 0;
    status.textContent = visible === 1 ? "1 guía disponible." : `${visible} guías disponibles.`;
  };

  categories.forEach((button) => {
    button.addEventListener("click", () => {
      activeCategory = button.dataset.helpCategory;
      categories.forEach((item) => {
        const selected = item === button;
        item.classList.toggle("is-active", selected);
        item.setAttribute("aria-pressed", String(selected));
      });
      applyFilter();
    });
  });
  search.addEventListener("input", applyFilter);
  root.querySelectorAll("[data-help-quick]").forEach((card) => {
    card.addEventListener("click", () => {
      activeCategory = "all";
      categories.forEach((item) => {
        const selected = item.dataset.helpCategory === "all";
        item.classList.toggle("is-active", selected);
        item.setAttribute("aria-pressed", String(selected));
      });
      search.value = "";
      applyFilter();
    });
  });
  root.querySelectorAll("[data-guide-step]").forEach((step) => {
    step.addEventListener("change", () => {
      const guideId = step.dataset.guideId;
      const card = step.closest("[data-help-guide]");
      const completed = [...card.querySelectorAll("[data-guide-step]:checked")].map((item) => item.dataset.stepId);
      progressByGuide[guideId] = completed;
      saveProgress();
      renderGuideProgress(guideId);
    });
  });
  root.querySelectorAll("[data-guide-reset]").forEach((button) => {
    button.addEventListener("click", () => {
      const guideId = button.dataset.guideReset;
      delete progressByGuide[guideId];
      saveProgress();
      renderGuideProgress(guideId);
      root.querySelector(`#guide-${guideId} [data-guide-step]`)?.focus();
    });
  });
  root.querySelectorAll("[data-copy-example]").forEach((button) => {
    button.addEventListener("click", async () => {
      const example = root.querySelector(`#help-example-${button.dataset.copyExample}`)?.textContent.trim();
      if (!example) return;
      try {
        await navigator.clipboard.writeText(example);
        button.textContent = "Ejemplo copiado";
      } catch {
        button.textContent = "No se pudo copiar";
      }
      window.setTimeout(() => { button.textContent = "Copiar ejemplo seguro"; }, 2200);
    });
  });
  if (teacherToggle && teacherRoute) {
    const teacherStorageKey = "ev3-help-teacher-mode-v1";
    const setTeacherMode = (enabled) => {
      teacherRoute.hidden = !enabled;
      teacherToggle.setAttribute("aria-pressed", String(enabled));
      teacherToggle.textContent = enabled ? "Ocultar modo docente" : "Modo docente";
      try { window.localStorage.setItem(teacherStorageKey, String(enabled)); } catch { /* almacenamiento opcional */ }
    };
    let teacherEnabled = false;
    try { teacherEnabled = window.localStorage.getItem(teacherStorageKey) === "true"; } catch { /* almacenamiento opcional */ }
    setTeacherMode(teacherEnabled);
    teacherToggle.addEventListener("click", () => setTeacherMode(teacherRoute.hidden));
  }
  guides.forEach((guide) => renderGuideProgress(guide.id.replace("guide-", "")));
})();
